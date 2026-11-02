"""ShinkaEvolve external evaluator contract, with no host import of candidates."""

import argparse
import json
from pathlib import Path

from .contracts import Scenario, digest
from .evaluation import evaluate_program
from .families import transform

UPSTREAM_REVISION = "8adc053a2ce4511ad2ac310e004c530a73fb974a"


def evaluate(program_path: Path, results_dir: Path, *, operators=("identity",)) -> dict:
    if results_dir.exists() and any((results_dir / name).exists() for name in ("metrics.json", "correct.json", "evaluation.json")):
        raise ValueError("Refusing to overwrite existing evaluation artifacts")
    results_dir.mkdir(parents=True, exist_ok=True)
    # Read as data. Never import or exec the candidate in this process.
    program = program_path.read_text()
    rows = []
    error = None
    try:
        if not program.strip() or len(program.encode()) > 16000:
            raise ValueError("Candidate program exceeds the bounded interface")
        for index, operator in enumerate(operators):
            scenario = transform(Scenario(), operator).scenario
            trace = Path("traces") / f"case-{index:02d}.jsonl"
            rows.append({"case": operator, "trace": str(trace),
                         **evaluate_program(program, scenario, results_dir / trace)})
    except (ValueError, OSError) as exc:
        error = str(exc)
    execution_ok = bool(rows) and error is None and all(row["error"] is None for row in rows)
    success = sum(row["verified"] for row in rows) / len(rows) if rows else 0
    metrics = {"combined_score": success if execution_ok else 0,
               "verified_completions": sum(row["verified"] for row in rows),
               "trial_count": len(rows), "text_feedback": error or "; ".join(
                   f"{row['case']}: {row['reason']}" for row in rows)}
    # Shinka correctness means the candidate/evaluation interface ran correctly;
    # task quality remains the score, so bad policies are retained with low fitness.
    correct = {"correct": execution_ok, "error": error or next(
        (row["error"] for row in rows if row["error"]), None)}
    artifact = {"schema": "agentqa.shinka-evaluation.v1", "upstream_revision": UPSTREAM_REVISION,
                "program_hash": digest(program), "metrics": metrics, "correct": correct, "results": rows}
    for name, payload in (("metrics.json", metrics), ("correct.json", correct), ("evaluation.json", artifact)):
        with (results_dir / name).open("x") as stream:
            json.dump(payload, stream, indent=2)
    return artifact


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--program_path", type=Path, required=True)
    parser.add_argument("--results_dir", type=Path, required=True)
    parser.add_argument("--operators", default="identity")
    args = parser.parse_args()
    result = evaluate(args.program_path, args.results_dir, operators=tuple(args.operators.split(",")))
    print(json.dumps({"metrics": result["metrics"], "correct": result["correct"]}))


if __name__ == "__main__":
    main()
