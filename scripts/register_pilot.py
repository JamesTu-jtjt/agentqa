"""Import existing pilot provenance into an immutable registry; no new inference."""

import argparse
import hashlib
import json
from pathlib import Path

from agentqa.contracts import Scenario, canonical
from agentqa.registry import CandidateRegistry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    registry = CandidateRegistry(args.output / "registry.sqlite3")
    source_hash = Scenario().identity
    registry.add("parent", "def choose_action(observation):\n    return 'complete'\n",
                 parent=None, source_hash=source_hash, origin="authored-control",
                 provenance={"description": "Original authored always-complete policy"})
    pilot = Path("evidence/codex-pilot-001")
    inference = json.loads((pilot / "inference.json").read_text())
    registry.begin_attempt("generation-001", parent="parent", source_hash=source_hash,
                           details={"imported_retrospectively": True,
                                    "prompt_sha256": hashlib.sha256((pilot / "prompt.txt").read_bytes()).hexdigest()})
    ids = ["parent"]
    for index in range(2):
        record = json.loads((pilot / f"candidate-{index:02d}.json").read_text())
        candidate_id = f"repair-{index:02d}"
        registry.add(candidate_id, record["program"], parent="parent", source_hash=source_hash,
                     origin="model-generated", provenance={"attempt": "generation-001", "rationale": record["rationale"],
                                                             "model": "gpt-6.1-sol"})
        ids.append(candidate_id)
        (args.output / f"{candidate_id}.py").write_text(record["program"])
    registry.finish_attempt("generation-001", "completed", {"candidate_ids": ids[1:], "usage": inference["usage"]})
    manifest = registry.freeze("pilot-pool-001", ids, parent="parent")
    (args.output / "pool.json").write_bytes(canonical(manifest) + b"\n")
    registry.close()
    print(json.dumps({"pool_hash": manifest["hash"], "candidate_count": len(ids)}))


if __name__ == "__main__":
    main()
