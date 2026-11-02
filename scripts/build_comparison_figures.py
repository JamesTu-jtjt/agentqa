"""Report-ready development plots; trace replay precedes every plotted score."""

import argparse
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(ROOT / "scratch/matplotlib"))
os.environ.setdefault("XDG_CACHE_HOME", str(ROOT / "scratch/cache"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

from agentqa.recorder import replay
from agentqa.registry import validate_pool


def save(fig, output, stem):
    for extension in ("png", "svg", "pdf"):
        kwargs = {"dpi": 180} if extension == "png" else {}
        if extension == "svg":
            kwargs["metadata"] = {"Date": None}
        fig.savefig(output / f"{stem}.{extension}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    plan_path, pool_path = args.summary.parent / "plan.json", args.summary.parent / "pool.json"
    plan, pool = json.loads(plan_path.read_text()), json.loads(pool_path.read_text())
    validate_pool(pool)
    if summary["scope"] != "development-only-not-independent-audit" or summary["plan_hash"] != plan["hash"]:
        raise ValueError("Unexpected scope or plan")
    slots = {slot["id"]: slot for slot in plan["slots"]}
    for row in summary["results"]:
        verdict = replay(args.summary.parent / row["trace"], row["trace_tip"])
        if any(row[key] != value for key, value in verdict.to_dict().items()):
            raise ValueError("Saved score does not match trace replay")
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "svg.hashsalt": "agentqa-development-comparison-v1"})
    candidates = [candidate["id"] for candidate in pool["candidates"]]
    methods = ["source-only", "generic", "failure-family"]
    matrix = np.zeros((len(candidates), len(methods)))
    counts = {}
    for i, candidate in enumerate(candidates):
        for j, method in enumerate(methods):
            rows = [row for row in summary["results"] if row["candidate"] == candidate
                    and slots[row["slot"]]["method"] == method]
            numerator = sum(row["verified"] for row in rows)
            matrix[i, j] = numerator / len(rows)
            counts[(i, j)] = (numerator, len(rows))
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.imshow(matrix, cmap=ListedColormap(["#f7dedb", "#d0eadd"]), vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(3), ["Source-only", "Generic variations", "Failure families"])
    ax.set_yticks(range(len(candidates)), ["Authored parent" if name == "parent" else name for name in candidates])
    for (i, j), (passed, total) in counts.items():
        ax.text(j, i, f"{passed}/{total}", ha="center", va="center", fontsize=16, color="#243b53")
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Development comparison: both repairs pass every selector's suite", loc="left", pad=18, weight="bold")
    fig.subplots_adjust(left=0.24, bottom=0.28, top=0.86)
    fig.text(0.04, 0.04, "Verified completions / six matched slots · two common regression controls per candidate\nAll selectors chose repair-00. Repeated pure-policy trials; no independent audit or selection advantage established.", fontsize=10, color="#475569")
    save(fig, args.output, "development-comparison")

    workers = [worker for row in summary["results"] for worker in row["worker_results"]]
    measured = [worker for worker in workers if worker["startup_seconds"] is not None]
    startup = [worker["startup_seconds"] for worker in measured]
    remainder = [max(0, worker["duration_seconds"] - worker["startup_seconds"]) for worker in measured]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.boxplot([startup, remainder], tick_labels=["Container startup", "Remaining wall time"],
               showfliers=True, patch_artist=True,
               boxprops={"facecolor": "#d8e7f5", "edgecolor": "#526e8a"},
               medianprops={"color": "#a34432", "linewidth": 1.8})
    ax.set_ylabel("Seconds per worker invocation")
    ax.set_title("Worker overhead is measured separately", loc="left", weight="bold", pad=15)
    ax.spines[["top", "right"]].set_visible(False)
    fig.subplots_adjust(bottom=0.25)
    fig.text(0.08, 0.035, f"{len(measured)} measured local worker invocations · remaining time includes execution and cleanup.\nTiming describes this machine/run, not model inference latency.", fontsize=9, color="#475569")
    save(fig, args.output, "worker-timing")
    manifest = {"scope": summary["scope"], "replayed_trials": len(summary["results"]),
                "worker_invocations": len(workers), "matplotlib_version": matplotlib.__version__,
                "inputs": {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                           for path in [args.summary, plan_path, pool_path, Path(__file__)]}}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
