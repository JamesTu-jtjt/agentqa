"""Actual upstream scheduler with fresh, host-bound publication receipts."""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import shinka.launch.scheduler as scheduler_module
from shinka.launch.scheduler import JobScheduler, LocalJobConfig

from agentqa.bundles import run_bound_job
from agentqa.contracts import digest
from agentqa.shinka_bridge import UPSTREAM_REVISION
from probe_shinka_results import EVALUATOR


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkout = Path(__file__).resolve().parents[1] / "vendor/ShinkaEvolve"
    revision = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if revision != UPSTREAM_REVISION or not Path(scheduler_module.__file__).resolve().is_relative_to(checkout):
        raise ValueError("Wrong upstream scheduler")
    args.output.mkdir(parents=True, exist_ok=False)
    snapshot = args.output / "code_snapshot"
    snapshot.mkdir()
    import agentqa.bundles
    from shutil import copyfile
    for source in (Path(agentqa.bundles.__file__), Path(__file__)):
        copyfile(source, snapshot / source.name)
    evaluator = args.output / "authored_evaluator.py"
    evaluator.write_text(EVALUATOR)
    cases = [("nonzero", "fail", False), ("zero-no-publication", "no_publish", False),
             ("partial-publication", "partial", False), ("normal-publication", "pass", True)]
    plan = {"schema": "agentqa.bound-check.v1", "upstream_revision": revision, "cases": cases,
            "evaluator_hash": digest(EVALUATOR), "inference_calls": 0, "retry_policy": "none",
            "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshot.iterdir()}}
    (args.output / "plan.json").write_text(json.dumps({**plan, "plan_hash": digest(plan)}, indent=2))
    scheduler = JobScheduler("local", LocalJobConfig(eval_program_path=str(evaluator.absolute()),
        python_executable=sys.executable, numeric_threads_per_job=1), max_workers=1)
    rows = []
    try:
        for name, mode, expected in cases:
            program = args.output / f"{name}-program.json"
            program.write_text(json.dumps({"mode": mode, "score": .25, "version": "changed"}))
            manifest = run_bound_job(scheduler, program, evaluator, args.output / name,
                trusted_evaluator=True, runtime_identity={"shinka_revision": revision, "python": sys.version.split()[0]})
            rows.append({"case": name, "expected_valid": expected, "bundle": name, **manifest})
            print(json.dumps({"case": name, **manifest["verdict"]}), flush=True)
    finally:
        scheduler.executor.shutdown(wait=True)
    summary = {"schema": "agentqa.bound-check.v1", "plan_hash": digest(plan), "results": rows,
               "matches": sum(row["expected_valid"] == row["verdict"]["valid"] for row in rows), "inference_calls": 0}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    if summary["matches"] != len(rows):
        raise RuntimeError("Bound publication did not match the declared contract")


if __name__ == "__main__":
    main()
