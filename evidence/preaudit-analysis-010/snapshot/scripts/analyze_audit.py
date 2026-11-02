"""Analyze an already verified, complete frozen audit grid; never executes it."""

import argparse
import json
from pathlib import Path

from agentqa.analysis import analyze_audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--outcomes", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = analyze_audit(json.loads(args.plan.read_text()), json.loads(args.outcomes.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x") as stream:
        json.dump(result, stream, indent=2)
    print(json.dumps({"scope": result["scope"], "source_pool_count": result["source_pool_count"],
                      "audit_trial_count": result["audit_trial_count"]}))


if __name__ == "__main__":
    main()
