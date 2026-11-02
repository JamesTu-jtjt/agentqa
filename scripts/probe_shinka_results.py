"""Bounded source qualification against an unmodified pinned Shinka scheduler.

All evaluation fixtures here are authored data/processes. No generated program
runs on the host and no model inference is requested.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import shinka.launch.scheduler as scheduler_module
from shinka.launch.scheduler import JobScheduler, LocalJobConfig

from agentqa.contracts import digest
from agentqa.shinka_bridge import UPSTREAM_REVISION

EVALUATOR = '''import argparse, json, pathlib, sys
p = argparse.ArgumentParser()
p.add_argument('--program_path', required=True)
p.add_argument('--results_dir', required=True)
a = p.parse_args()
state = json.loads(pathlib.Path(a.program_path).read_text())
root = pathlib.Path(a.results_dir)
root.mkdir(parents=True, exist_ok=True)
if state['mode'] == 'fail':
    print('Authored evaluation failure before publication', file=sys.stderr)
    sys.exit(7)
if state['mode'] == 'no_publish':
    print('Authored zero-exit evaluation without result publication')
    sys.exit(0)
(root / 'metrics.json').write_text(json.dumps({'combined_score': state['score']}))
if state['mode'] != 'partial':
    (root / 'correct.json').write_text(json.dumps({'correct': True, 'error': None}))
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    checkout = root / "vendor/ShinkaEvolve"
    revision = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if revision != UPSTREAM_REVISION or not Path(scheduler_module.__file__).resolve().is_relative_to(checkout):
        raise ValueError("Scheduler must come from the unchanged pinned checkout")
    changed = subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain"], text=True)
    if changed.strip():
        raise ValueError("Upstream checkout is not clean")
    args.output.mkdir(parents=True, exist_ok=False)
    evaluator = args.output / "authored_evaluator.py"
    evaluator.write_text(EVALUATOR)
    cases = [("nonzero-reused", "fail", True), ("nonzero-fresh", "fail", False),
             ("zero-no-publication", "no_publish", True), ("partial-publication", "partial", True),
             ("normal-publication", "pass", True), ("normal-fresh", "pass", False)]
    paths = ["shinka/launch/local.py", "shinka/launch/scheduler.py", "shinka/utils/general.py"]
    plan = {"schema": "agentqa.upstream-probe-plan.v1", "upstream_revision": revision,
            "source_hashes": {name: sha(checkout / name) for name in paths},
            "evaluator_sha256": sha(evaluator), "cases": cases, "inference_calls": 0,
            "scope": "Public scheduler API under authored rerun/failure conditions; not observed native agent behavior",
            "retry_policy": "none", "expected_contract": "Never attribute old/mixed result files to a changed evaluation request"}
    (args.output / "plan.json").write_text(json.dumps({**plan, "plan_hash": digest(plan)}, indent=2))
    source_dir = args.output / "upstream-source"
    for name in paths:
        path = source_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(checkout / name, path)
    shutil.copyfile(checkout / "LICENSE", source_dir / "LICENSE")
    scheduler = JobScheduler("local", LocalJobConfig(eval_program_path=str(evaluator.resolve()),
        python_executable=sys.executable, eval_verbose=False, numeric_threads_per_job=1), max_workers=1)
    rows = []
    try:
        for name, mode, prime in cases:
            folder = args.output / name
            folder.mkdir()
            program = folder / "program.json"
            results = folder / "results"
            program.write_text(json.dumps({"mode": "pass", "score": 1, "version": "original"}))
            previous_hash = sha(program)
            if prime:
                prior, _ = scheduler.run(str(program.resolve()), str(results.resolve()))
                if prior["correct"]["correct"] is not True:
                    raise RuntimeError("Priming evaluation did not succeed")
                shutil.copytree(results, folder / "prior-results")
            program.write_text(json.dumps({"mode": mode, "score": .25, "version": "changed"}))
            started = time.monotonic()
            process = scheduler.submit_async(str(program.resolve()), str(results.resolve()))
            observed = scheduler.get_job_results(process, str(results.resolve()))
            artifacts = {p.name: sha(p) for p in results.glob("*.json")}
            prior_artifacts = {p.name: sha(p) for p in (folder / "prior-results").glob("*.json")} if prime else {}
            complete_publication = mode == "pass"
            row = {"case": name, "mode": mode, "primed": prime, "returncode": process.returncode,
                   "prior_program_sha256": previous_hash, "current_program_sha256": sha(program),
                   "current_artifacts": artifacts, "prior_artifacts": prior_artifacts,
                   "observed_result": observed, "expected_accept": complete_publication,
                   "observed_accept": observed.get("correct", {}).get("correct") is True,
                   "duration_seconds": time.monotonic() - started}
            rows.append(row)
            with (args.output / "outcomes.jsonl").open("a") as stream:
                stream.write(json.dumps(row) + "\n")
            print(json.dumps({key: row[key] for key in ("case", "returncode", "expected_accept", "observed_accept")}), flush=True)
    finally:
        scheduler.executor.shutdown(wait=True)
    summary = {"schema": "agentqa.upstream-probe.v1", "plan_hash": digest(plan), "inference_calls": 0,
               "upstream_revision": revision, "results": rows,
               "false_acceptances": sum(row["observed_accept"] and not row["expected_accept"] for row in rows)}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
