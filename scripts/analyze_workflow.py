"""Replay workflow evidence and regenerate descriptive checkpoint figures."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np

from agentqa.contracts import digest
from agentqa.recorder import replay


def inspect(root):
    summary = json.loads((root / "summary.json").read_text())
    plan = json.loads((root / "plan.json").read_text())
    plan_hash = plan.pop("plan_hash")
    if digest(plan) != plan_hash or summary["plan_hash"] != plan_hash:
        raise ValueError("Plan identity mismatch")
    if digest(plan["source_hashes"]) != plan["code_hash"]:
        raise ValueError("Code manifest mismatch")
    for name, expected in plan["source_hashes"].items():
        if hashlib.sha256((root / "code_snapshot" / Path(name).name).read_bytes()).hexdigest() != expected:
            raise ValueError("Code snapshot mismatch")
    rows = []
    coordinates = set()
    for row in summary["results"]:
        coordinate = (row["candidate"], row["case"]["name"])
        if coordinate in coordinates or row["case"] not in plan["cases"]:
            raise ValueError("Duplicate/unplanned workflow trial")
        coordinates.add(coordinate)
        if digest(row["case"]) != row["case_hash"]:
            raise ValueError("Case identity mismatch")
        if digest((root / f'{row["candidate"]}.py').read_text()) != row["program_hash"]:
            raise ValueError("Controller identity mismatch")
        trace = root / row["trace"]
        verdict = replay(trace, row["tip"]).to_dict()
        if any(row[key] != value for key, value in verdict.items()):
            raise ValueError("Summary differs from replay")
        events = [json.loads(line) for line in trace.read_text().splitlines()]
        tests = [event for event in events if event["kind"] == "test"]
        if len(tests) != len(row["task_workers"]):
            raise ValueError("Missing worker records")
        for event, worker in zip(tests, row["task_workers"]):
            worker = dict(worker)
            purpose = worker.pop("purpose")
            if event["payload"]["purpose"] != purpose or event["payload"]["worker_hash"] != digest(worker):
                raise ValueError("Worker provenance mismatch")
        actions = [event["payload"]["value"]["action"] for event in events
                   if event["kind"] == "observation" and event["payload"].get("event") == "action"]
        workers = row["task_workers"] + row["controller_workers"]
        rows.append({"candidate": row["candidate"], "case": row["case"]["name"],
            **verdict, "infrastructure_error": row["infrastructure_error"], "error_kind": row["error_kind"],
            "actions": row["actions"], "action_sequence": actions,
            "actual_edits": sum(event["kind"] == "state" and event["payload"].get("cause") == "agent_write" for event in events),
            "visible_executions": sum(event["payload"]["purpose"] == "visible" for event in tests),
            "handoffs": sum(event["kind"] == "observation" and event["payload"].get("event") == "handoff" for event in events),
            "transition_reached": row["transition_reached"], "workers": len(workers),
            "worker_seconds": sum(worker["duration_seconds"] for worker in workers),
            "cleanup_confirmed": all(worker["cleanup_confirmed"] for worker in workers),
            "trace": str(trace), "tip": row["tip"]})
    for candidate in {row["candidate"] for row in rows}:
        if len([row for row in rows if row["candidate"] == candidate]) != len(plan["cases"]):
            raise ValueError("Incomplete workflow case grid")
    return rows


def save_figure(figure, root, name):
    for extension in ("png", "svg", "pdf"):
        figure.savefig(root / f"{name}.{extension}", dpi=180, bbox_inches="tight")
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = [row for root in args.inputs for row in inspect(root)]
    args.output.mkdir(parents=True, exist_ok=False)
    candidates = list(dict.fromkeys(row["candidate"] for row in rows))
    cases = list(dict.fromkeys(row["case"] for row in rows))
    matrix = np.full((len(candidates), len(cases)), -1, dtype=int)
    labels = {}
    for row in rows:
        value = (3 if row["infrastructure_error"] else 2 if row["verified"] else
                 1 if row["completed"] and row["functional"] and not row["fresh"] else 0)
        matrix[candidates.index(row["candidate"]), cases.index(row["case"])] = value
        labels[(row["candidate"], row["case"])] = ("Infrastructure\ninconclusive" if value == 3 else
            "Verified" if value == 2 else "Stale evidence" if value == 1 else row["reason"].replace("_", "\n"))
    if (matrix < 0).any():
        raise ValueError("Incomplete candidate/case grid")
    fig, ax = plt.subplots(figsize=(12, 4.4))
    fig.subplots_adjust(bottom=.28)
    ax.imshow(matrix, cmap=ListedColormap(["#f1b66b", "#f4b1b0", "#b7dfcd", "#d5d9df"]), vmin=0, vmax=3, aspect="auto")
    ax.set_xticks(range(len(cases)), [name.capitalize() for name in cases])
    display = {"reference": "Reference (authored)", "stale-control": "Stale control (authored)",
               "generated": "GPT-6.1 Sol controller"}
    ax.set_yticks(range(len(candidates)), [display.get(name, name) for name in candidates])
    ax.tick_params(length=0, pad=9)
    for i, candidate in enumerate(candidates):
        for j, case in enumerate(cases):
            ax.text(j, i, labels[candidate, case], ha="center", va="center", fontsize=9)
    ax.set_title("Stateful coding workflow: actual edits, verification and handoffs", pad=18, fontsize=13)
    fig.text(0.5, .035, "Development cases; one execution per cell. Model generated a controller once, not at each tool step.\nAuthored controls validate measurement; these outcomes do not compare repair selectors.", ha="center", fontsize=9, color="#444444")
    save_figure(fig, args.output, "workflow-outcomes")

    fig, ax = plt.subplots(figsize=(12, 4.4))
    fig.subplots_adjust(bottom=.30)
    colors = {"read": "#406c95", "write": "#bd662e", "status": "#6c638f", "verify": "#2f8064",
              "handoff": "#735097", "complete": "#303b47", "refuse": "#a94343"}
    for i, candidate in enumerate(candidates):
        row = next(row for row in rows if row["candidate"] == candidate and row["case"] == "config")
        sequence = row["action_sequence"]
        ax.plot(range(1, len(sequence) + 1), [i] * len(sequence), color="#c5cbd0", zorder=1)
        for step, action in enumerate(sequence, 1):
            ax.scatter(step, i, color=colors[action], s=65, zorder=2)
            ax.annotate(action, (step, i), (0, 12), textcoords="offset points", ha="center", fontsize=8)
        suffix = "verified" if row["verified"] else row["reason"].replace("_", " ")
        ax.text(12.4, i, suffix, va="center", fontsize=9)
    ax.set_yticks(range(len(candidates)), [display.get(name, name) for name in candidates])
    ax.set_xticks(range(1, 13))
    ax.set_xlim(.6, 16)
    ax.set_ylim(len(candidates) - .5, -.7)
    ax.set_xlabel("Controller action number (allowance: 12)")
    ax.set_title("Recorded action sequences: configuration-change case", pad=16)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    fig.text(.5, .02, "The environment updates configuration and resets memory immediately after the first passing verification.\nSubsequent status/verification actions are controller decisions, not forced repairs.", ha="center", fontsize=9, color="#444444")
    save_figure(fig, args.output, "workflow-actions")

    counts = Counter(row["candidate"] for row in rows if row["verified"])
    result = {"schema": "agentqa.workflow-analysis.v1", "trials": len(rows), "rows": rows,
              "verified_by_candidate": dict(counts), "worker_invocations": sum(row["workers"] for row in rows),
              "worker_seconds": sum(row["worker_seconds"] for row in rows),
              "infrastructure_inconclusive": sum(row["infrastructure_error"] for row in rows),
              "all_cleanup_confirmed": all(row["cleanup_confirmed"] for row in rows)}
    (args.output / "analysis.json").write_text(json.dumps(result, indent=2))
    inputs = {str(root / "summary.json"): hashlib.sha256((root / "summary.json").read_bytes()).hexdigest() for root in args.inputs}
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in args.output.iterdir()}
    manifest = {"inputs": inputs, "outputs": outputs,
                "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "note": "All plotted traces replayed; no inference or candidate execution during analysis."}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}))


if __name__ == "__main__":
    main()
