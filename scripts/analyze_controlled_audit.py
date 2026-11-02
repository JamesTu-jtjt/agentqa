"""Replay amendment C1, then export measured tables and a scientific figure."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from agentqa.contracts import digest
from agentqa.controlled_audit import finish_audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--expected-hash", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    summary, analysis = finish_audit(args.root, args.audit, args.expected_hash)
    plan = json.loads((args.audit / "plan.json").read_text())
    args.output.mkdir(parents=True, exist_ok=False)
    templates = [template["id"] for template in plan["templates"]]
    pool = plan["pools"][0]
    candidates = [*pool["candidates"], *pool["references"]]
    by_case = {case["id"]: case for case in plan["cases"]}
    table = []
    for row in summary["results"]:
        table.append({"candidate": row["candidate"], "case": row["slot_id"],
                      "template": by_case[row["slot_id"]]["template_id"],
                      **{key: row[key] for key in ("completed", "functional", "fresh", "verified", "refusal")},
                      "visible_runs_including_setup": row["visible_runs_including_setup"],
                      "workers": len(row["worker_results"]),
                      "worker_seconds": sum(w["duration_seconds"] for w in row["worker_results"])})
    with (args.output / "trials.csv").open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)
    lines = ["# Controlled transfer pilot results", "", f"Frozen plan: `{args.expected_hash}`.", "",
             "One authored source pool; unchanged cached model repairs; nine new controlled cases. No additional inference.", "",
             "| Policy | Verified / cases | Functional | Fresh | Explicit refusals |", "| --- | ---: | ---: | ---: | ---: |"]
    scores = analysis["by_pool"][pool["pool_id"]]["candidates"]
    for candidate in candidates:
        count = scores[candidate]["raw_counts"]
        lines.append(f'| {candidate} | {count["verified"]} / {scores[candidate]["cases"]} | {count["functional"]} | {count["fresh"]} | {count["refusal"]} |')
    lines += ["", "| Selector | Previously selected policy | Verified / cases |", "| --- | --- | ---: |"]
    for method, selected in pool["decisions"].items():
        lines.append(f'| {method} | {selected} | {scores[selected]["raw_counts"]["verified"]} / {scores[selected]["cases"]} |')
    lines += ["", "Failure-family minus source-only and generic verified-completion differences: "
              + ", ".join(f'{method}: {result["difference"]:+.3f}' for method, result in analysis["family_minus_baseline"].items()) + ".",
              "No interval: one source pool. Equal outcomes do not establish equivalence or a selector advantage.", "",
              f'{summary["trial_count"]} trials; {summary["worker_count"]} Docker workers; {summary["worker_seconds"]:.2f} summed worker seconds. '
              "Zero new model calls or API calls; shared generation subscription dollar cost remains unknown.", "",
              "The authored reference is not selectable. Task implementations are authored; the generated programs choose completion/verification actions. "
              "This does not evaluate native Sakana evolution, naturally occurring model failures, or interactive repair of new repositories."]
    (args.output / "results.md").write_text("\n".join(lines) + "\n")

    fig, ax = plt.subplots(figsize=(9.4, 5.2))
    colors = ("#b85555", "#276ca8", "#73a5ca", "#438b6a")
    labels = ("Authored parent", "Generated repair 00", "Generated repair 01", "Authored rerun reference")
    width = .18
    for index, candidate in enumerate(candidates):
        counts = [sum(row["verified"] for row in table if row["candidate"] == candidate and row["template"] == template) for template in templates]
        positions = [i + (index - 1.5) * width for i in range(len(templates))]
        bars = ax.bar(positions, counts, width=width, color=colors[index], label=labels[index])
        for bar, count in zip(bars, counts):
            ax.text(bar.get_x() + width / 2, count + .055, f"{count}/3", ha="center", fontsize=9)
    ax.set_xticks(range(3), ["Text normalization", "Discounted totals", "Graph reachability"])
    ax.set_ylim(0, 3.55)
    ax.set_yticks(range(4))
    ax.set_ylabel("Verified completions (three cases per template)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, alpha=.18)
    ax.set_axisbelow(True)
    ax.set_title("Controlled policy transfer: one source pool", loc="left", fontsize=15, pad=26)
    ax.text(0, 1.03, "All three frozen selectors chose repair 00; no observed selector advantage.", transform=ax.transAxes, fontsize=10)
    fig.legend(loc="lower center", bbox_to_anchor=(.5, .07), ncol=2, frameon=False, fontsize=10)
    fig.text(.08, .025, "Authored tasks · cached deterministic policies · no confidence interval · zero new inference", fontsize=9, color="#444444")
    fig.subplots_adjust(left=.08, right=.98, top=.79, bottom=.25)
    for extension in ("png", "svg", "pdf"):
        fig.savefig(args.output / f"controlled-transfer.{extension}", dpi=180)
    plt.close(fig)
    outputs = {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in sorted(args.output.iterdir())}
    manifest = {"schema": "agentqa.controlled-audit-figure.v1", "audit_plan_hash": args.expected_hash,
                "analysis_hash": digest(analysis), "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "inputs": {name: hashlib.sha256((args.audit / name).read_bytes()).hexdigest()
                           for name in ("plan.json", "summary.json", "outcomes.json", "analysis.json")},
                "outputs": outputs, "new_model_calls": 0}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"trials": summary["trial_count"], "source_pools": analysis["source_pool_count"], "output": str(args.output)}))


if __name__ == "__main__":
    main()
