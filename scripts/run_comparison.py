import argparse
import json
from pathlib import Path

from agentqa.comparison import run_comparison

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pool", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_comparison(json.loads(args.pool.read_text()), args.output)
    print(json.dumps({"trials": result["trial_count"], "scope": result["scope"],
                      "selected": {method: value["selected"] for method, value in result["decisions"].items()}}))
