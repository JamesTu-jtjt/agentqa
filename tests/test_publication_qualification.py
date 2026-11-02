import json
from pathlib import Path
import shutil

import pytest

from agentqa.publication_qualification import validate_qualification

SAVED = Path(__file__).resolve().parents[1] / "evidence/publication-qualification-011"


def test_actual_qualification_replays_including_negative_results():
    result = validate_qualification(SAVED)
    assert result["cases"] == result["contract_matches"] == 20
    assert result["renaming_pairs_invariant"] == result["renaming_pairs"] == 10
    summary = json.loads((SAVED / "summary.json").read_text())
    negatives = [row for row in summary["results"] if row["case"]["mode"] == "negative"]
    assert all(row["verdict"]["valid"] and not row["verdict"]["correct"] for row in negatives)


@pytest.mark.parametrize("mutation", ("missing", "case", "publisher", "result"))
def test_drift_or_incomplete_real_evidence_is_rejected(tmp_path, mutation):
    root = tmp_path / "copy"
    shutil.copytree(SAVED, root)
    path = root / "summary.json"
    summary = json.loads(path.read_text())
    if mutation == "missing":
        summary["results"].pop()
    elif mutation == "case":
        summary["results"][0]["case"]["expected_valid"] = False
    elif mutation == "publisher":
        (root / summary["results"][0]["publisher"]).write_text("changed")
    else:
        (root / summary["results"][0]["bundle"] / "results/metrics.json").write_text('{"combined_score":99}')
    path.write_text(json.dumps(summary))
    with pytest.raises(ValueError):
        validate_qualification(root)
