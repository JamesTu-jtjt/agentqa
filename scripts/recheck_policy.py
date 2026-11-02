"""Diagnostic rerun of cached policy after infrastructure changes; no inference."""

import argparse
import hashlib
import json
from pathlib import Path

from agentqa.contracts import Scenario
from agentqa.evaluation import evaluate_program
from agentqa.families import generate
import agentqa.sandbox


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prior", type=Path, required=True)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    program = args.program.read_text()
    results = []
    for case in generate(Scenario()):
        trace = Path("traces") / f"{case.transformation}.jsonl"
        results.append({"case": case.transformation, "trace": str(trace),
                        **evaluate_program(program, case.scenario, args.output / trace)})
    result = {"schema": "agentqa.infrastructure-recheck.v1", "inference_calls": 0,
              "reason": "Separate container startup from candidate execution timeout",
              "prior_sha256": hashlib.sha256(args.prior.read_bytes()).hexdigest(),
              "worker_sha256": hashlib.sha256(Path(agentqa.sandbox.__file__).read_bytes()).hexdigest(),
              "scope": "Diagnostic rerun; original attempted outcomes remain unchanged",
              "results": results}
    (args.output / "summary.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"verified": sum(row["verified"] for row in results), "trials": len(results)}))


if __name__ == "__main__":
    main()
