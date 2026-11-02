"""Frozen authored native-run study. Core analysis has no Shinka dependency."""

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import sqlite3

from .contracts import digest

SCHEMA = "agentqa.native-initialization.v1"
POLICIES = ("upstream", "exit_only", "schema_only", "fresh_only", "fresh_exit_schema", "bound")
HISTORIES = ("fresh", "completed", "interrupted")
MODES = ("nonzero_empty", "zero_empty", "metrics_only", "correct_only",
         "full_then_nonzero", "positive", "negative")


@dataclass(frozen=True)
class Cell:
    history: str
    policy: str
    mode: str

    @property
    def name(self):
        return f"{self.history}--{self.policy}--{self.mode}"


def cells():
    native = [Cell(h, "upstream", m) for h in HISTORIES for m in MODES]
    defenses = [Cell("completed", p, m) for p in POLICIES[1:] for m in MODES]
    return native + defenses


def program(mode, *, primer=False):
    if mode not in (*MODES, "block_after_publication"):
        raise ValueError("Unknown authored mode")
    # Only these fixed, authored programs may execute in the host experiment.
    state = {"mode": mode, "score": .1 if primer else .9, "correct": mode != "negative",
             "phase": "primer" if primer else "target"}
    return "# Fixed authored native study fixture\ndef evaluate():\n    return " + repr(state) + "\n"


EVALUATOR = '''import argparse, json, pathlib, runpy, sys, time
p = argparse.ArgumentParser()
p.add_argument('--program_path', required=True)
p.add_argument('--results_dir', required=True)
a = p.parse_args()
s = runpy.run_path(a.program_path)['evaluate']()
r = pathlib.Path(a.results_dir)
r.mkdir(parents=True, exist_ok=True)
mode = s['mode']
print(json.dumps(s), flush=True)
if mode == 'nonzero_empty':
    sys.exit(7)
if mode == 'zero_empty':
    sys.exit(0)
if mode != 'correct_only':
    (r / 'metrics.json').write_text(json.dumps({'combined_score': s['score']}))
if mode != 'metrics_only':
    (r / 'correct.json').write_text(json.dumps({'correct': s['correct'], 'error': None}))
if mode == 'full_then_nonzero':
    sys.exit(7)
if mode == 'block_after_publication':
    (r / 'published.marker').write_text('complete output published; evaluator deliberately blocked')
    while True:
        time.sleep(.05)
'''


def snapshot_database(path):
    """Read native tables without constructing or mutating an upstream database."""
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        rows = [dict(row) for row in conn.execute(
            "SELECT id,code,generation,correct,combined_score,metadata FROM programs ORDER BY rowid")]
        archive = [row[0] for row in conn.execute("SELECT program_id FROM archive ORDER BY program_id")]
        metadata = dict(conn.execute("SELECT key,value FROM metadata_store"))
    for row in rows:
        row["correct"] = bool(row["correct"])
        row["metadata"] = json.loads(row["metadata"] or "{}")
    return {"programs": rows, "archive": archive, "metadata": metadata}


def grade(cell, current, database):
    """Keep invalid acceptance, score attribution and negative evidence distinct."""
    if current["code"] != program(cell.mode):
        raise ValueError("Target program differs from frozen authored source")
    valid = cell.mode in {"positive", "negative"}
    incorrect_acceptance = not valid and current["correct"]
    expected_score = .9 if valid else None
    return {"valid_attempt": valid, "incorrect_acceptance": incorrect_acceptance,
            "invalid_nonzero_score": not valid and current["combined_score"] not in (None, 0),
            "incorrect_archive": incorrect_acceptance and current["id"] in database["archive"],
            "incorrect_best": incorrect_acceptance and current["id"] == database["metadata"].get("best_program_id"),
            "positive_preserved": cell.mode == "positive" and current["correct"] and current["combined_score"] == expected_score,
            "negative_preserved": cell.mode == "negative" and not current["correct"] and current["combined_score"] == expected_score}


def analyze_rows(rows):
    expected = {cell.name: cell for cell in cells()}
    seen = set()
    for row in rows:
        cell = Cell(**row["cell"])
        if cell.name not in expected or cell.name in seen:
            raise ValueError("Unexpected or duplicate native cell")
        seen.add(cell.name)
        if row["grade"] != grade(cell, row["current"], row["database"]):
            raise ValueError("Native grade changed")
        if row["target_report"]["total_proposals_generated"] != 0:
            raise ValueError("Unexpected model proposal")
    if seen != set(expected):
        raise ValueError("Incomplete native grid")

    def counts(group):
        return {"cells": len(group), "invalid_cells": sum(not r["grade"]["valid_attempt"] for r in group),
                **{key: sum(r["grade"][key] for r in group) for key in (
                    "incorrect_acceptance", "invalid_nonzero_score", "incorrect_archive", "incorrect_best",
                    "positive_preserved", "negative_preserved")}}

    return {"schema": SCHEMA, "model_calls": 0, "independent_source_pools": 0,
            "native": {history: counts([r for r in rows if r["cell"]["history"] == history
                      and r["cell"]["policy"] == "upstream"]) for history in HISTORIES},
            "defenses": {policy: counts([r for r in rows if r["cell"]["history"] == "completed"
                        and r["cell"]["policy"] == policy]) for policy in POLICIES},
            "rows_hash": digest(rows), "confidence_interval": None,
            "scope": "Authored deterministic native initialization/restart and defense comparison; not generated repair selection"}
