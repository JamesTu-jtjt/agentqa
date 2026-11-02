"""No-inference native Shinka initialization study; fixed authored programs only."""

import argparse
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time

from agentqa.contracts import digest
from agentqa.native_study import (SCHEMA, EVALUATOR, Cell, cells, program,
                                  snapshot_database, grade, analyze_rows)
from agentqa.shinka_bridge import UPSTREAM_REVISION

ROOT = Path(__file__).resolve().parents[1]
CHECKOUT = ROOT / "vendor/ShinkaEvolve"


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact_hashes(path):
    return {name: file_hash(path / name) for name in ("metrics.json", "correct.json") if (path / name).exists()}


def guard_network(event, args):
    if event == "socket.connect":
        address = args[1]
        if isinstance(address, tuple):
            raise RuntimeError("N1 forbids Internet sockets")


def worker(args):
    os.environ["SHINKA_PRICING_MODE"] = "offline"
    os.environ["SHINKA_CACHE_DIR"] = str(args.cell_root / "offline-cache")
    os.environ["WANDB_MODE"] = "disabled"
    sys.addaudithook(guard_network)
    from shinka.core import ShinkaEvolveRunner, EvolutionConfig
    from shinka.database import DatabaseConfig
    from shinka.launch import LocalJobConfig
    import shinka.launch.scheduler as scheduler_module
    from agentqa.bundles import parse_result, run_bound_job

    if not Path(scheduler_module.__file__).resolve().is_relative_to(CHECKOUT):
        raise ValueError("Wrong upstream import location")
    events = []
    original_submit = scheduler_module.submit_local

    def observe(*positional, **kwargs):
        started = time.monotonic()
        proc = original_submit(*positional, **kwargs)
        events.append((proc, {"command_hash": digest(positional[1]),
                              "results_dir": str(Path(positional[0]).relative_to(args.cell_root)),
                              "started_monotonic": started}))
        return proc

    # Pure observation: delegate the exact arguments and original return object.
    scheduler_module.submit_local = observe
    init_path = args.cell_root / f"{args.phase}-initial.py"
    mode = args.mode if args.phase == "target" else (
        "block_after_publication" if args.history == "interrupted" else "positive")
    init_path.write_text(program(mode, primer=args.phase == "primer"))
    evo = EvolutionConfig(num_generations=1, init_program_path=str(init_path),
        results_dir=str(args.cell_root / "native"), llm_models=[], llm_dynamic_selection=None,
        llm_kwargs={}, embedding_model=None, meta_rec_interval=None, meta_llm_models=None,
        novelty_llm_models=None, evolve_prompts=False, enable_wandb_logging=False)
    job = LocalJobConfig(eval_program_path=str(args.cell_root / "evaluate.py"),
        python_executable=sys.executable, time="00:00:10", eval_verbose=False, numeric_threads_per_job=1)
    runner = ShinkaEvolveRunner(evo, job, DatabaseConfig(num_islands=1), verbose=False,
        max_evaluation_jobs=1, max_proposal_jobs=1, max_db_workers=1)
    adapter_records = []
    if args.phase == "target" and args.policy != "upstream":
        base = runner.scheduler

        class Adapter:
            def __getattr__(self, name):
                return getattr(base, name)

            def run(self, source, output):
                started = time.monotonic()
                attempt = args.cell_root / "defense-attempt"
                result_path = Path(output)
                if args.policy == "bound":
                    manifest = run_bound_job(base, Path(source), args.cell_root / "evaluate.py", attempt,
                        trusted_evaluator=True, timeout=10,
                        runtime_identity={"python": sys.version.split()[0], "shinka_revision": UPSTREAM_REVISION})
                    verdict = manifest["verdict"]
                    returned = {"correct": {"correct": verdict["correct"]},
                                "metrics": {"combined_score": verdict["score"] if verdict["valid"] else 0}}
                    adapter_records.append({"policy": args.policy, "manifest": manifest,
                                            "valid_publication": verdict["valid"], "returned": returned})
                    return returned, time.monotonic() - started
                if args.policy in {"fresh_only", "fresh_exit_schema"}:
                    result_path = attempt / "results"
                    result_path.mkdir(parents=True, exist_ok=False)
                before = len(events)
                raw, _ = base.run(source, str(result_path))
                if len(events) != before + 1:
                    raise RuntimeError("Expected exactly one observed evaluator process")
                returncode = events[-1][0].returncode
                returned = raw
                valid = None
                if args.policy in {"exit_only", "fresh_exit_schema"} and returncode != 0:
                    valid = False
                if args.policy in {"schema_only", "fresh_exit_schema"}:
                    try:
                        parsed = parse_result(result_path)
                        if valid is not False:
                            valid, returned = True, {**raw, **parsed}
                    except (OSError, ValueError, TypeError, KeyError):
                        valid = False
                if valid is False:
                    returned = {"correct": {"correct": False}, "metrics": {"combined_score": 0}}
                adapter_records.append({"policy": args.policy, "returncode": returncode,
                    "raw": raw, "returned": returned, "valid_publication": valid,
                    "results_dir": str(result_path.relative_to(args.cell_root))})
                return returned, time.monotonic() - started

        runner.scheduler = Adapter()
    started = time.monotonic()
    runner.run()
    observed = []
    for process, event in events:
        event.update(returncode=process.returncode, completed=process.poll() is not None,
                     duration_seconds=time.monotonic() - event["started_monotonic"])
        observed.append(event)
    if len(observed) != 1 or not all(event["completed"] for event in observed):
        raise RuntimeError("Native run did not finish exactly one evaluator")
    write_json(args.cell_root / f"{args.phase}-worker.json", {
        "schema": SCHEMA, "phase": args.phase, "policy": args.policy,
        "duration_seconds": time.monotonic() - started,
        "total_proposals_generated": runner.total_proposals_generated,
        "recorded_api_cost": runner.total_api_cost, "llm_models": [], "network": "Internet socket connect blocked",
        "events": observed, "adapters": adapter_records,
        "database": snapshot_database(args.cell_root / "native/programs.sqlite")})


def execute(root, cell, phase):
    cmd = [sys.executable, str(Path(__file__).resolve()), "--worker", "--cell-root", str(root),
           "--phase", phase, "--mode", cell.mode, "--history", cell.history, "--policy", cell.policy]
    with (root / f"{phase}-stdout.log").open("w") as stdout, (root / f"{phase}-stderr.log").open("w") as stderr:
        proc = subprocess.Popen(cmd, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            if phase == "primer" and cell.history == "interrupted":
                marker = root / "native/gen_0/results/published.marker"
                deadline = time.monotonic() + 20
                while not marker.exists() and proc.poll() is None and time.monotonic() < deadline:
                    time.sleep(.02)
                if not marker.exists():
                    raise RuntimeError("Interrupted primer did not reach its frozen publication barrier")
                # No insert is possible while the evaluator remains blocked.
                before = snapshot_database(root / "native/programs.sqlite")
                if before["programs"]:
                    raise RuntimeError("Primer unexpectedly inserted before interruption")
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=5)
                after = snapshot_database(root / "native/programs.sqlite")
                if after["programs"]:
                    raise RuntimeError("Interrupted primer database is not empty")
                report = {"interrupted": True, "worker_returncode": proc.returncode,
                          "database": after, "marker": marker.read_text(), "fault": "external process-group SIGTERM"}
                write_json(root / "primer-interruption.json", report)
                return report
            proc.wait(timeout=30)
            if proc.returncode != 0:
                raise RuntimeError(f"Native {phase} worker failed, status {proc.returncode}; preserve logs")
            return json.loads((root / f"{phase}-worker.json").read_text())
        finally:
            if proc.poll() is None:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)


def make_plan(output):
    revision = subprocess.check_output(["git", "-C", str(CHECKOUT), "rev-parse", "HEAD"], text=True).strip()
    if revision != UPSTREAM_REVISION or subprocess.check_output(
            ["git", "-C", str(CHECKOUT), "status", "--porcelain"], text=True).strip():
        raise ValueError("Use the clean pinned upstream tree")
    output.mkdir(parents=True, exist_ok=False)
    paths = ["scripts/run_native_study.py", "src/agentqa/native_study.py", "src/agentqa/bundles.py",
             "src/agentqa/contracts.py", "docs/native-followup-protocol.md", "tests/test_native_study.py"]
    upstream = ["shinka/core/async_runner.py", "shinka/core/config.py", "shinka/database/dbase.py",
                "shinka/database/async_dbase.py", "shinka/launch/scheduler.py", "shinka/launch/local.py",
                "shinka/utils/general.py", "LICENSE"]
    for prefix, base, names in (("code_snapshot", ROOT, paths), ("upstream-source", CHECKOUT, upstream)):
        for name in names:
            destination = output / prefix / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(base / name, destination)
    plan = {"schema": SCHEMA, "upstream_revision": revision,
        "source_hashes": {name: file_hash(ROOT / name) for name in paths},
        "upstream_hashes": {name: file_hash(CHECKOUT / name) for name in upstream},
        "cells": [asdict(cell) for cell in cells()], "evaluator_hash": digest(EVALUATOR),
        "model_calls": 0, "max_evaluator_processes": 105, "retry_policy": "none",
        "native_target_generations": 1, "python": sys.version.split()[0]}
    write_json(output / "plan.json", {**plan, "plan_hash": digest(plan)})
    return plan


def run(output):
    envelope = json.loads((output / "plan.json").read_text())
    plan = {k: v for k, v in envelope.items() if k != "plan_hash"}
    if digest(plan) != envelope["plan_hash"] or plan["cells"] != [asdict(cell) for cell in cells()]:
        raise ValueError("Frozen native plan changed")
    for name, expected in plan["source_hashes"].items():
        if file_hash(ROOT / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    if any((output / "cells").glob("*")):
        raise ValueError("Refuse resampling or overwriting existing native cells")
    rows = []
    for cell in cells():
        root = output / "cells" / cell.name
        root.mkdir(parents=True, exist_ok=False)
        write_json(root / "reservation.json", {"cell": asdict(cell), "plan_hash": envelope["plan_hash"]})
        (root / "evaluate.py").write_text(EVALUATOR)
        primer = None
        if cell.history != "fresh":
            primer = execute(root, cell, "primer")
            if cell.history == "completed":
                entries = primer["database"]["programs"]
                if len(entries) != 1 or not entries[0]["correct"] or entries[0]["combined_score"] != .1:
                    raise RuntimeError("Native primer qualification failed")
            shutil.copytree(root / "native/gen_0/results", root / "prior-results")
        before = primer["database"] if primer else {"programs": [], "archive": [], "metadata": {}}
        old_ids = {p["id"] for p in before["programs"]}
        report = execute(root, cell, "target")
        database = report["database"]
        new = [p for p in database["programs"] if p["id"] not in old_ids]
        if len(new) != 1:
            raise RuntimeError("Expected exactly one new native target program")
        row = {"cell": asdict(cell), "plan_hash": envelope["plan_hash"],
               "current": new[0], "database": database, "target_report": report,
               "prior_artifacts": artifact_hashes(root / "prior-results"),
               "current_artifacts": artifact_hashes(root / "native/gen_0/results"),
               "primer": primer}
        row["grade"] = grade(cell, new[0], database)
        write_json(root / "result.json", row)
        rows.append(row)
        print(json.dumps({"cell": cell.name, "correct": new[0]["correct"],
            "score": new[0]["combined_score"], **row["grade"]}), flush=True)
    write_json(output / "outcomes.json", rows)
    write_json(output / "analysis.json", analyze_rows(rows))
    # All paths are internal; raw file hashes make the saved execution independently checkable.
    hashes = {str(p.relative_to(output)): file_hash(p) for p in output.rglob("*")
              if p.is_file() and p.name != "file-manifest.json"}
    write_json(output / "file-manifest.json", {"schema": SCHEMA, "files": hashes,
        "files_hash": digest(hashes), "plan_hash": envelope["plan_hash"]})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--freeze", action="store_true")
    parser.add_argument("--worker", action="store_true")
    parser.add_argument("--cell-root", type=Path)
    parser.add_argument("--phase", choices=("primer", "target"))
    parser.add_argument("--mode")
    parser.add_argument("--history")
    parser.add_argument("--policy")
    args = parser.parse_args()
    if args.worker:
        worker(args)
    elif args.freeze:
        make_plan(args.output.resolve())
    else:
        run(args.output.resolve())


if __name__ == "__main__":
    main()
