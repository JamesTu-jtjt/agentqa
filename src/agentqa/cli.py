import argparse
import json
from pathlib import Path

from .demo import run_demo
from .recorder import replay


def main():
    parser = argparse.ArgumentParser(description="AgentQA offline measurement tools")
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo = subcommands.add_parser("demo", help="Execute authored controls; no model calls")
    demo.add_argument("--output", type=Path, required=True, help="New, nonexistent directory")
    check = subcommands.add_parser("replay", help="Recompute a verdict from a recorded trace")
    check.add_argument("trace", type=Path)
    check.add_argument("--expected-tip", help="Final event hash from the frozen manifest")
    evidence = subcommands.add_parser("verify-evidence", help="Verify saved development evidence; no execution/model calls")
    evidence.add_argument("--root", type=Path, required=True, help="AgentQA checkout or extracted reproduction bundle")
    args = parser.parse_args()
    if args.command == "demo":
        result = run_demo(args.output)
        print(json.dumps({"output": str(args.output), "cases": len(result["validation"]),
                          "trials": len(result["results"]), "claim": result["claim"]}, indent=2))
    elif args.command == "replay":
        print(json.dumps(replay(args.trace, args.expected_tip).to_dict(), indent=2))
    else:
        from .evidence import verify_evidence
        print(json.dumps(verify_evidence(args.root), indent=2))


if __name__ == "__main__":
    main()
