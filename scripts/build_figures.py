"""Regenerate report figures from replay-verified authored-control traces."""

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / "scratch/matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import numpy as np

from agentqa.recorder import replay


def save(fig, directory, stem):
    for extension in ("png", "svg", "pdf"):
        options = {"dpi": 180} if extension == "png" else {}
        if extension == "svg":
            options["metadata"] = {"Date": None}
        fig.savefig(directory / f"{stem}.{extension}", bbox_inches="tight", **options)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text())
    if summary["origin"] != "authored-controls":
        raise ValueError("This figure layout is specifically labeled for authored controls")
    for result in summary["results"]:
        verdict = replay(args.summary.parent / result["trace"], result["trace_tip"])
        if any(result[key] != value for key, value in verdict.to_dict().items()):
            raise ValueError("Summary does not agree with independently replayed verdict")
    args.output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.size": 11, "svg.hashsalt": "agentqa-controls-v1"})
    cases = list(dict.fromkeys(row["case"] for row in summary["results"]))
    policies = list(dict.fromkeys(row["policy"] for row in summary["results"]))
    matrix = np.zeros((len(policies), len(cases)))
    labels = [[""] * len(cases) for _ in policies]
    for row in summary["results"]:
        i, j = policies.index(row["policy"]), cases.index(row["case"])
        matrix[i, j] = 1 if row["verified"] else 0
        labels[i][j] = "Pass" if row["verified"] else ("Refused" if not row["completed"] else "Stale")
    fig, ax = plt.subplots(figsize=(11.5, 5.3))
    ax.imshow(matrix, cmap=ListedColormap(["#f7dedb", "#d0eadd"]), vmin=0, vmax=1)
    ax.set_xticks(range(len(cases)), [case.replace("_", " ") for case in cases], rotation=25, ha="right")
    ax.set_yticks(range(len(policies)), ["Trust old evidence", "Narrow reminder", "Always rerun", "Check provenance", "Refuse"])
    for i in range(len(policies)):
        for j in range(len(cases)):
            ax.text(j, i, labels[i][j], ha="center", va="center", color="#203646", fontsize=10)
    ax.set_title("Authored controls: source repair can fail after a valid transformation", pad=18, loc="left", weight="bold")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(length=0)
    fig.text(0.04, 0.015, "One real local execution per cell · 35 trials · 0 model calls\nMeasurement demonstration only; not an evolved-agent comparison or a generalization estimate.", fontsize=10, color="#475569")
    fig.subplots_adjust(bottom=0.24, left=0.20, top=0.87)
    save(fig, args.output, "authored-control-outcomes")

    fig, ax = plt.subplots(figsize=(12, 5.5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5)
    ax.axis("off")
    boxes = [(0.2, 2.7, 2.2, 1.1, "Confirmed failure\n+ explicit contract"),
             (3.2, 3.2, 2.5, 1.1, "Common candidate pool\n(source feedback only)"),
             (3.2, 1.1, 2.5, 1.1, "Validated test families\n+ generic controls"),
             (6.4, 2.7, 2.2, 1.1, "Matched selection\n+ regression gate"),
             (9.3, 2.7, 2.4, 1.1, "Frozen independent audit\nrepair transfer + cost")]
    for x, y, w, h, label in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08", fc="#eaf0f7", ec="#526e8a", lw=1.3))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=10)
    for start, end in [((2.5, 3.5), (3.1, 3.7)), ((2.4, 2.8), (3.1, 1.8)),
                       ((5.8, 3.7), (6.3, 3.4)), ((5.8, 1.8), (6.3, 2.9)),
                       ((8.7, 3.25), (9.2, 3.25))]:
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=15, color="#526e8a", lw=1.5))
    ax.axvline(8.95, ymin=0.16, ymax=0.9, color="#b05d47", linestyle="--")
    ax.text(8.95, 0.45, "Freeze selection before audit; no audit feedback to editor", ha="center", fontsize=10, color="#9c4937")
    ax.text(0.15, 4.7, "Planned experimental separation", fontsize=17, weight="bold")
    fig.text(0.12, 0.025, "Conceptual design · Live candidate generation and independent audit have not run.", fontsize=10, color="#475569")
    save(fig, args.output, "experimental-design")
    manifest = {"origin": "authored-controls-and-conceptual-design", "model_calls": 0,
                "summary_sha256": hashlib.sha256(args.summary.read_bytes()).hexdigest(),
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "matplotlib_version": matplotlib.__version__, "replayed_traces": len(summary["results"])}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
