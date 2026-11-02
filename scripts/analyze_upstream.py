"""Check diagnostic artifacts and render the source/repair qualification figure."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from agentqa.bundles import verify_bundle
from agentqa.contracts import digest


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_probe(root):
    plan = json.loads((root / "plan.json").read_text())
    expected_plan_hash = plan.pop("plan_hash")
    summary = json.loads((root / "summary.json").read_text())
    if digest(plan) != expected_plan_hash or summary["plan_hash"] != expected_plan_hash:
        raise ValueError("Upstream probe plan mismatch")
    if sha(root / "authored_evaluator.py") != plan["evaluator_sha256"]:
        raise ValueError("Evaluator source mismatch")
    for name, expected in plan["source_hashes"].items():
        if sha(root / "upstream-source" / name) != expected:
            raise ValueError("Pinned source copy mismatch")
    expected_cases = {name: (mode, prime) for name, mode, prime in plan["cases"]}
    if len(summary["results"]) != len(expected_cases):
        raise ValueError("Incomplete diagnostic grid")
    seen = set()
    for row in summary["results"]:
        name = row["case"]
        if name in seen or expected_cases[name] != (row["mode"], row["primed"]):
            raise ValueError("Unplanned or repeated case")
        seen.add(name)
        folder = root / name
        state = json.loads((folder / "program.json").read_text())
        if sha(folder / "program.json") != row["current_program_sha256"] or state["mode"] != row["mode"]:
            raise ValueError("Request identity mismatch")
        if row["prior_program_sha256"] == row["current_program_sha256"]:
            raise ValueError("Expected a changed evaluation request")
        for subfolder, field in (("results", "current_artifacts"), ("prior-results", "prior_artifacts")):
            actual = {path.name: sha(path) for path in (folder / subfolder).glob("*.json")}
            if actual != row[field]:
                raise ValueError("Result file mismatch")
        returned = row["observed_result"]
        if row["observed_accept"] != (returned["correct"].get("correct") is True):
            raise ValueError("Attribution summary mismatch")
        if row["expected_accept"] != (row["mode"] == "pass"):
            raise ValueError("Publisher/expected-contract mismatch")
        if row["returncode"] != (7 if row["mode"] == "fail" else 0):
            raise ValueError("Unexpected process status")
        if row["primed"]:
            if row["mode"] in {"fail", "no_publish"} and row["current_artifacts"] != row["prior_artifacts"]:
                raise ValueError("No-publication condition changed result artifacts")
            if row["mode"] == "partial":
                if (row["current_artifacts"]["correct.json"] != row["prior_artifacts"]["correct.json"]
                        or row["current_artifacts"]["metrics.json"] == row["prior_artifacts"]["metrics.json"]):
                    raise ValueError("Partial-publication condition not realized")
    if summary["false_acceptances"] != sum(row["observed_accept"] and not row["expected_accept"] for row in summary["results"]):
        raise ValueError("Diagnostic count mismatch")
    return summary


def verify_bound(root):
    plan = json.loads((root / "plan.json").read_text())
    plan_hash = plan.pop("plan_hash")
    summary = json.loads((root / "summary.json").read_text())
    if digest(plan) != plan_hash or summary["plan_hash"] != plan_hash:
        raise ValueError("Bound check plan mismatch")
    for name, expected in plan.get("source_hashes", {}).items():
        if sha(root / "code_snapshot" / name) != expected:
            raise ValueError("Bound adapter source mismatch")
    if digest((root / "authored_evaluator.py").read_text()) != plan["evaluator_hash"]:
        raise ValueError("Bound evaluator mismatch")
    expected_cases = {name: expected for name, _, expected in plan["cases"]}
    if len(summary["results"]) != len(expected_cases):
        raise ValueError("Incomplete bound grid")
    seen = set()
    for row in summary["results"]:
        if row["case"] in seen or row["expected_valid"] != expected_cases[row["case"]]:
            raise ValueError("Unexpected bound check coordinate")
        seen.add(row["case"])
        verdict = verify_bundle(root / row["bundle"], expected_request_hash=row["request_hash"],
                                expected_receipt_hash=row["receipt_hash"]).to_dict()
        if verdict != row["verdict"]:
            raise ValueError("Bound receipt did not replay")
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--bound", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = verify_probe(args.source)
    bound = verify_bound(args.bound)
    args.output.mkdir(parents=True, exist_ok=False)
    fig, axes = plt.subplots(2, 1, figsize=(12, 6), gridspec_kw={"height_ratios": [1, 1]})
    fig.subplots_adjust(hspace=.9, bottom=.22, top=.88)
    labels = {"nonzero-reused": "Exit 7\nreused directory", "nonzero-fresh": "Exit 7\nfresh directory",
              "zero-no-publication": "Exit 0\nno publication", "partial-publication": "Partial\npublication",
              "normal-publication": "Complete\npublication", "normal-fresh": "Complete\nfresh directory", "nonzero": "Exit 7\nno publication"}
    for ax, rows, title, outcome in ((axes[0], source["results"], "Unmodified pinned Shinka scheduler: six diagnostic cases", "observed_accept"),
                                    (axes[1], bound["results"], "Local adapter: four fresh, attempt-bound publication checks", "valid")):
        values, annotations = [], []
        for row in rows:
            actual = row[outcome] if outcome in row else row["verdict"][outcome]
            expected = row["expected_accept"] if "expected_accept" in row else row["expected_valid"]
            matches = actual == expected
            values.append(2 if not matches else 1 if actual else 0)
            annotations.append("Stale/mixed\nresult accepted" if not matches else "New result\naccepted" if actual else "Result\nrejected")
        ax.imshow([values], cmap=ListedColormap(["#cbd9eb", "#b7dfcd", "#efb2b1"]), vmin=0, vmax=2, aspect="auto")
        for n, annotation in enumerate(annotations):
            ax.text(n, 0, annotation, ha="center", va="center", fontsize=10)
        ax.set_xticks(range(len(rows)), [labels[row["case"]] for row in rows])
        ax.set_yticks([])
        ax.tick_params(length=0, pad=9)
        ax.set_title(title, fontsize=11, loc="left", pad=13)
    fig.suptitle("Execution evidence must belong to the evaluation request", fontsize=14)
    fig.text(.5, .035, "Authored fault/reuse scenarios against unchanged upstream code; no model calls.\nDiagnostic qualification, not a population failure rate or a repair-selector comparison.", ha="center", fontsize=10, color="#444444")
    for extension in ("png", "svg", "pdf"):
        fig.savefig(args.output / f"publication-qualification.{extension}", dpi=180, bbox_inches="tight")
    plt.close(fig)
    result = {"schema": "agentqa.upstream-analysis.v1", "source_cases": len(source["results"]),
              "source_false_attributions": source["false_acceptances"], "bound_checks": len(bound["results"]),
              "bound_matches": sum(row["expected_valid"] == row["verdict"]["valid"] for row in bound["results"]),
              "model_calls": 0, "native_agent_failure": False, "independent_audit": False,
              "verification": "Source hashes/artifact facts checked; bound manifests replayed"}
    (args.output / "analysis.json").write_text(json.dumps(result, indent=2))
    manifest = {"inputs": {str(root / "summary.json"): sha(root / "summary.json") for root in (args.source, args.bound)},
                "script_sha256": sha(Path(__file__)), "outputs": {p.name: sha(p) for p in args.output.iterdir()}}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(result))


if __name__ == "__main__":
    main()
