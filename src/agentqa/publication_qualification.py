"""Authored development qualification; never an independent agent-repair audit."""

from collections import defaultdict
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path

from .bundles import verify_bundle
from .contracts import digest

SCHEMA = "agentqa.publication-qualification.v1"


@dataclass(frozen=True)
class PublicationCase:
    case_id: str
    mode: str
    layout: str
    expected_valid: bool
    expected_correct: bool

    @property
    def identity(self):
        return digest(asdict(self))


def cases():
    modes = ("positive", "negative", "exit_after_publication", "metrics_only", "correct_only",
             "boolean_score", "duplicate_key", "changed_program", "changed_config", "no_publication")
    return [PublicationCase(f"{layout}-{mode}", mode, layout, mode in {"positive", "negative"},
                            mode == "positive") for layout in ("plain", "renamed") for mode in modes]


PUBLISHER = '''import argparse, json, pathlib, sys
parser = argparse.ArgumentParser()
parser.add_argument('--program_path', required=True)
parser.add_argument('--results_dir', required=True)
args = parser.parse_args()
program = pathlib.Path(args.program_path)
state = json.loads(program.read_text())
mode = state['mode']
root = pathlib.Path(args.results_dir)
root.mkdir(parents=True, exist_ok=True)
if mode == 'no_publication':
    sys.exit(0)
if mode == 'changed_program':
    program.write_text(json.dumps({**state, 'touched_during_run': True}))
if mode == 'changed_config':
    config = pathlib.Path(state['config'])
    config.write_text(json.dumps({'limit': 11}))
if mode != 'correct_only':
    metrics = {'combined_score': -.5 if mode == 'negative' else 2.5}
    if mode == 'boolean_score':
        metrics['combined_score'] = True
    text = json.dumps(metrics)
    if mode == 'duplicate_key':
        text = '{"combined_score": 2.5, "combined_score": 99}'
    (root / 'metrics.json').write_text(text)
if mode != 'metrics_only':
    (root / 'correct.json').write_text(json.dumps({'correct': mode != 'negative', 'error': None}))
if mode == 'exit_after_publication':
    sys.exit(7)
'''


def validate_qualification(root: Path):
    """Recheck frozen identities, every result receipt, and renamed-pair behavior."""
    envelope = json.loads((root / "plan.json").read_text())
    plan = {key: value for key, value in envelope.items() if key != "plan_hash"}
    if digest(plan) != envelope.get("plan_hash") or plan.get("schema") != SCHEMA:
        raise ValueError("Qualification plan mismatch")
    summary = json.loads((root / "summary.json").read_text())
    if summary.get("plan_hash") != envelope["plan_hash"]:
        raise ValueError("Qualification result/plan mismatch")
    for name, expected in plan["source_hashes"].items():
        if hashlib.sha256((root / "code_snapshot" / name).read_bytes()).hexdigest() != expected:
            raise ValueError("Qualification code snapshot changed")
    declared = {case["case_id"]: case for case in plan["cases"]}
    seen, pairs = set(), defaultdict(list)
    matches = 0
    for row in summary["results"]:
        case = row["case"]
        identity = case["case_id"]
        if identity in seen or declared.get(identity) != case or digest(case) != row["case_hash"]:
            raise ValueError("Unplanned/duplicate case or changed case identity")
        seen.add(identity)
        bundle = root / row["bundle"]
        result = verify_bundle(bundle, expected_request_hash=row["request_hash"],
                               expected_receipt_hash=row["receipt_hash"]).to_dict()
        if result != row["verdict"]:
            raise ValueError("Publication verdict differs from receipt replay")
        request = json.loads((bundle / "request.json").read_text())
        evaluator = Path(request["inputs"]["evaluator"]["path"])
        # The request records absolute original paths; match the preserved local
        # evaluator by its basename instead, so offline verification is portable.
        relative = Path(row["publisher"])
        if evaluator.name != relative.name or digest((root / relative).read_text()) != plan["publisher_hash"]:
            raise ValueError("Publisher identity mismatch")
        expected = case["expected_valid"] == result["valid"] and case["expected_correct"] == result["correct"]
        matches += expected
        pairs[case["mode"]].append((case["layout"], result))
    if seen != set(declared):
        raise ValueError("Incomplete qualification grid")
    invariant = 0
    for values in pairs.values():
        if {layout for layout, _ in values} != {"plain", "renamed"} or len(values) != 2:
            raise ValueError("Missing renamed counterpart")
        if values[0][1] == values[1][1]:
            invariant += 1
    if summary["contract_matches"] != matches or summary["renaming_pairs_invariant"] != invariant:
        raise ValueError("Qualification count mismatch")
    return {"cases": len(seen), "contract_matches": matches, "renaming_pairs": len(pairs),
            "renaming_pairs_invariant": invariant, "model_calls": 0, "independent_audit": False}
