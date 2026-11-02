"""Run a real pinned ShinkaEvolve scheduler job without any inference calls."""

import argparse
import json
from pathlib import Path
import subprocess
import sys

from shinka.launch.scheduler import JobScheduler, LocalJobConfig
import shinka.launch.scheduler as scheduler_module

from agentqa.shinka_bridge import UPSTREAM_REVISION


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    checkout = root / "vendor/ShinkaEvolve"
    revision = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if revision != UPSTREAM_REVISION or not Path(scheduler_module.__file__).resolve().is_relative_to(checkout):
        raise ValueError("Actual scheduler does not come from the pinned upstream checkout")
    if args.output.exists():
        raise ValueError("Use a new output directory")
    config = LocalJobConfig(eval_program_path=str(root / "scripts/shinka_evaluate.py"),
                            python_executable=sys.executable, eval_verbose=False,
                            numeric_threads_per_job=1, extra_cmd_args={"operators": "identity,compaction"})
    scheduler = JobScheduler("local", config, max_workers=1)
    try:
        result, runtime = scheduler.run(str(args.program.resolve()), str(args.output.resolve()))
    finally:
        scheduler.executor.shutdown(wait=True)
    artifact = {"schema": "agentqa.shinka-integration.v1", "upstream_revision": revision,
                "scheduler_module": str(Path(scheduler_module.__file__).relative_to(checkout)),
                "result": result, "runtime_seconds": runtime, "inference_calls": 0}
    (args.output / "integration.json").write_text(json.dumps(artifact, indent=2))
    if result["correct"]["correct"] is not True or result["metrics"]["combined_score"] != 1:
        raise RuntimeError("Real scheduler evaluation did not return the expected valid fitness")
    print(json.dumps({"status": "passed", "upstream_revision": revision, "runtime_seconds": runtime}))


if __name__ == "__main__":
    main()
