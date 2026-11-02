"""Offline replay of the standard-producer applicability-boundary study."""

import hashlib
import json
from pathlib import Path

from .bundles import parse_result
from .contracts import digest


def verify_standard_wrapper(root: Path):
    root = root.resolve()
    envelope = json.loads((root / "plan.json").read_text())
    plan = {k: v for k, v in envelope.items() if k != "plan_hash"}
    if digest(plan) != envelope["plan_hash"] or plan["schema"] != "agentqa.standard-wrapper.v1":
        raise ValueError("Standard wrapper plan mismatch")
    manifest = json.loads((root / "file-manifest.json").read_text())
    if digest(manifest["files"]) != manifest["files_hash"] or manifest["plan_hash"] != envelope["plan_hash"]:
        raise ValueError("Standard wrapper manifest mismatch")
    actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name != "file-manifest.json"}
    if actual != set(manifest["files"]):
        raise ValueError("Standard wrapper inventory changed")
    for name, expected in manifest["files"].items():
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Unsafe wrapper evidence path")
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Standard wrapper artifact changed: {name}")
    for name, expected in plan["helpers"].items():
        if hashlib.sha256((root / f"{name}.py").read_bytes()).hexdigest() != expected:
            raise ValueError("Standard helper changed")
    rows = json.loads((root / "outcomes.json").read_text())
    remaining = {digest(cell): cell for cell in plan["cells"]}
    counts = {}
    for row in rows:
        cell = row["cell"]
        if remaining.pop(digest(cell), None) != cell:
            raise ValueError("Unexpected or repeated wrapper cell")
        name = "--".join(cell[k] for k in ("helper", "policy", "mode"))
        folder = root / "cells" / name
        if row != json.loads((folder / "result.json").read_text()):
            raise ValueError("Standard wrapper saved row differs")
        if json.loads((folder / "reservation.json").read_text()) != {"cell": cell, "plan_hash": envelope["plan_hash"]}:
            raise ValueError("Standard wrapper reservation changed")
        expected_exit = 7 if cell["mode"] in {"inside_nonzero", "before_nonzero"} else 0
        if row["target"]["returncode"] != expected_exit or row["primer"]["returncode"] != 0:
            raise ValueError("Standard helper process status mismatch")
        results = root / row["target_results"]
        if not results.resolve().is_relative_to(folder):
            raise ValueError("Wrapper result path escaped cell")
        raw = row["target"]["raw"]
        for file, field, fallback in (("metrics.json", "metrics", {}), ("correct.json", "correct", {"correct": False})):
            observed = json.loads((results / file).read_text()) if (results / file).exists() else fallback
            if raw[field] != observed:
                raise ValueError("Standard helper raw result differs from artifacts")
        returned = raw
        if cell["policy"] == "fresh_exit_schema":
            try:
                if expected_exit:
                    raise ValueError("Nonzero attempt")
                returned = {**raw, **parse_result(results)}
            except (OSError, ValueError, TypeError, KeyError):
                returned = {"correct": {"correct": False}, "metrics": {"combined_score": 0}}
        if returned != row["returned"]:
            raise ValueError("Standard helper defense replay mismatch")
        correct = returned.get("correct", {}).get("correct") is True
        score = returned.get("metrics", {}).get("combined_score")
        flags = {"incorrect_acceptance": cell["mode"] not in {"positive", "negative"} and correct,
                 "positive_preserved": cell["mode"] == "positive" and correct and score == .9,
                 "negative_preserved": cell["mode"] == "negative" and not correct and score == .9}
        if any(row[k] != value for k, value in flags.items()):
            raise ValueError("Standard helper outcome classification changed")
        key = f"{cell['helper']}--{cell['policy']}"
        group = counts.setdefault(key, {"cells": 0, "invalid_cells": 0, "incorrect_acceptance": 0,
                                       "positive_preserved": 0, "negative_preserved": 0,
                                       "inside_invalid_accepted": 0, "before_invalid_accepted": 0})
        group["cells"] += 1
        group["invalid_cells"] += cell["mode"] not in {"positive", "negative"}
        for flag, value in flags.items():
            group[flag] += value
        if flags["incorrect_acceptance"]:
            group["inside_invalid_accepted" if cell["mode"].startswith("inside_") else "before_invalid_accepted"] += 1
    if remaining or 2 * len(rows) != plan["max_evaluator_processes"]:
        raise ValueError("Incomplete standard helper grid")
    return {"schema": "agentqa.standard-wrapper-replay.v1", "cells": len(rows), "evaluator_processes": 2 * len(rows),
            "model_calls": 0, "plan_hash": envelope["plan_hash"], "files_hash": manifest["files_hash"],
            "groups": counts, "complete_pr_tested": False,
            "scope": "Exact isolated producer helpers with authored faults; public scheduler endpoint, not an independent repair audit"}
