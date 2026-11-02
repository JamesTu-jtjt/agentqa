"""Freeze, execute or verify amendment C1; no model inference."""

import argparse
from pathlib import Path

from agentqa.controlled_audit import finish_audit, freeze_audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("freeze", "run", "verify"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expected-hash")
    args = parser.parse_args()
    if args.mode == "freeze":
        print(freeze_audit(args.root, args.output)["plan_hash"])
    else:
        if not args.expected_hash:
            parser.error("run/verify require the external --expected-hash")
        summary, analysis = finish_audit(args.root, args.output, args.expected_hash, execute=args.mode == "run")
        print({"trials": summary["trial_count"], "workers": summary["worker_count"],
               "source_pools": analysis["source_pool_count"], "new_inference_calls": 0})


if __name__ == "__main__":
    main()
