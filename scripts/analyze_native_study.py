"""Replay before producing descriptive native-run tables and figures."""

import argparse
import csv
import hashlib
import json
from pathlib import Path

from agentqa.native_replay import verify_native_study


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("evidence/native-initialization-013"))
    parser.add_argument("--output", type=Path, default=Path("report/figures/native-initialization-013"))
    args = parser.parse_args()
    result = verify_native_study(args.input)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "verification.json").write_text(json.dumps(result, indent=2) + "\n")
    rows = []
    names = {"upstream": "Upstream", "exit_only": "Exit only", "schema_only": "Schema only",
             "fresh_only": "Fresh directory", "fresh_exit_schema": "Fresh + exit + schema", "bound": "Bound receipts"}
    for policy, counts in result["analysis"]["defenses"].items():
        rows.append({"policy": policy, "label": names[policy], **counts})
    with (args.output / "defenses.csv").open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    table = "| Defense | Incorrectly accepted / 5 invalid attempts | Invalid target archived | Invalid target best | Positive / negative preserved |\n| --- | ---: | ---: | ---: | --- |\n"
    for row in rows:
        table += f"| {row['label']} | {row['incorrect_acceptance']}/5 | {row['incorrect_archive']} | {row['incorrect_best']} | {row['positive_preserved']}/1; {row['negative_preserved']}/1 |\n"
    (args.output / "table.md").write_text(table)
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "font.family": "DejaVu Sans", "svg.fonttype": "none"})
    fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4.4), gridspec_kw={"width_ratios": [1, 1.45]})
    histories = result["analysis"]["native"]
    labels = ["Fresh run", "Restart after\ngeneration zero", "Retry after\ninterruption"]
    values = [histories[key]["incorrect_acceptance"] for key in ("fresh", "completed", "interrupted")]
    left.bar(range(3), values, color=["#7e9db2", "#ba5448", "#ba5448"])
    left.set_xticks(range(3), labels)
    left.set_ylim(0, 5.8); left.set_ylabel("Invalid attempts stored as correct (of 5)")
    left.set_title("Native initialization and persistence", loc="left", weight="bold", fontsize=11)
    for i, value in enumerate(values):
        left.text(i, value + .1, str(value), ha="center")
    right.barh([row["label"] for row in rows][::-1], [row["incorrect_acceptance"] for row in rows][::-1],
               color=["#3b8073" if row["incorrect_acceptance"] == 0 else "#ba5448" for row in rows][::-1])
    right.set_xlim(0, 5.8); right.set_xlabel("Invalid attempts stored as correct (of 5)")
    right.set_title("Defenses on the same restart conditions", loc="left", weight="bold", fontsize=11)
    for i, row in enumerate(rows[::-1]):
        right.text(row["incorrect_acceptance"] + .08, i, str(row["incorrect_acceptance"]), va="center")
    left.yaxis.set_major_locator(MaxNLocator(integer=True)); right.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig.suptitle("Fault-injected native runs expose acceptance failures; simple combined checks suffice", fontsize=12, weight="bold")
    fig.text(.02, .02, "Authored deterministic cases at one Shinka revision; no model calls, population rates or selector advantage. Both valid controls retained by every defense.", fontsize=8)
    fig.tight_layout(rect=(0, .07, 1, .93), w_pad=3)
    for extension in ("png", "svg"):
        fig.savefig(args.output / f"native-consequences.{extension}", dpi=180)
    plt.close(fig)
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in args.output.iterdir() if path.name != "manifest.json"}
    (args.output / "manifest.json").write_text(json.dumps({"plan_hash": result["plan_hash"], "files": outputs,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), "pdf_generated": False}, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "analysis"}))


if __name__ == "__main__":
    main()
