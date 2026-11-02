"""Twenty fixed authored checks through the real pinned local scheduler."""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import shinka.launch.scheduler as scheduler_module
from shinka.launch.scheduler import JobScheduler, LocalJobConfig

import agentqa.bundles
import agentqa.contracts
import agentqa.publication_qualification as qualification
from agentqa.bundles import run_bound_job
from agentqa.contracts import digest
from agentqa.shinka_bridge import UPSTREAM_REVISION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    checkout = Path(__file__).resolve().parents[1] / "vendor/ShinkaEvolve"
    revision = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if (revision != UPSTREAM_REVISION or not Path(scheduler_module.__file__).resolve().is_relative_to(checkout)
            or subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain"], text=True).strip()):
        raise ValueError("Use the unchanged pinned scheduler")
    args.output.mkdir(parents=True, exist_ok=False)
    snapshot = args.output / "code_snapshot"
    snapshot.mkdir()
    for path in (Path(agentqa.bundles.__file__), Path(agentqa.contracts.__file__),
                 Path(qualification.__file__), Path(__file__)):
        shutil.copyfile(path, snapshot / path.name)
    plan = {"schema": qualification.SCHEMA, "cases": [asdict(case) for case in qualification.cases()],
            "publisher_hash": digest(qualification.PUBLISHER), "upstream_revision": revision,
            "source_hashes": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in snapshot.iterdir()},
            "retry_policy": "none", "inference_calls": 0, "max_processes": 20,
            "scope": "Authored development qualification; not generated candidates or independent audit"}
    (args.output / "plan.json").write_text(json.dumps({**plan, "plan_hash": digest(plan)}, indent=2))
    results = []
    for case in qualification.cases():
        root = args.output / case.case_id
        inputs = root / ("task inputs" if case.layout == "renamed" else "inputs")
        inputs.mkdir(parents=True)
        publisher = inputs / ("evaluation tool.py" if case.layout == "renamed" else "evaluate.py")
        program = inputs / ("request data.json" if case.layout == "renamed" else "program.json")
        config = inputs / ("settings data.json" if case.layout == "renamed" else "config.json")
        publisher.write_text(qualification.PUBLISHER)
        config.write_text('{"limit":10}')
        program.write_text(json.dumps({"mode": case.mode, "config": str(config.absolute())}))
        scheduler = JobScheduler("local", LocalJobConfig(eval_program_path=str(publisher.absolute()),
            python_executable=sys.executable, numeric_threads_per_job=1), max_workers=1)
        try:
            manifest = run_bound_job(scheduler, program, publisher, root / "attempt", trusted_evaluator=True,
                extra_inputs={"config": config}, timeout=10,
                runtime_identity={"shinka_revision": revision, "python": sys.version.split()[0]})
        finally:
            scheduler.executor.shutdown(wait=True)
        row = {"case": asdict(case), "case_hash": case.identity,
               "bundle": str(Path(case.case_id) / "attempt"),
               "publisher": str(publisher.relative_to(args.output)), **manifest}
        results.append(row)
        with (args.output / "outcomes.jsonl").open("a") as stream:
            stream.write(json.dumps(row) + "\n")
        print(json.dumps({"case": case.case_id, **manifest["verdict"]}), flush=True)
    groups = {mode: [row["verdict"] for row in results if row["case"]["mode"] == mode]
              for mode in {case.mode for case in qualification.cases()}}
    summary = {"schema": qualification.SCHEMA, "plan_hash": digest(plan), "results": results,
               "contract_matches": sum(row["case"]["expected_valid"] == row["verdict"]["valid"]
                   and row["case"]["expected_correct"] == row["verdict"]["correct"] for row in results),
               "renaming_pairs_invariant": sum(values[0] == values[1] for values in groups.values()),
               "inference_calls": 0, "independent_audit": False}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    checked = qualification.validate_qualification(args.output)
    print(json.dumps(checked))


if __name__ == "__main__":
    main()
