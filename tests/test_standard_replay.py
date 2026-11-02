import json
from pathlib import Path
import shutil

import pytest

from agentqa.standard_replay import verify_standard_wrapper

SAVED = Path(__file__).resolve().parents[1] / "evidence/standard-wrapper-014"


def test_exact_published_helper_protects_its_entry_boundary():
    result = verify_standard_wrapper(SAVED)
    assert result["cells"] == 24
    assert result["evaluator_processes"] == 48
    assert not result["complete_pr_tested"]
    prior = result["groups"]["pr150_helper--raw"]
    assert prior["inside_invalid_accepted"] == 0
    assert prior["before_invalid_accepted"] == 2
    for key, group in result["groups"].items():
        assert group["positive_preserved"] == group["negative_preserved"] == 1
        if key.endswith("fresh_exit_schema"):
            assert group["incorrect_acceptance"] == 0


@pytest.mark.parametrize("mutation", ("helper", "result", "missing"))
def test_changed_or_incomplete_helper_evidence_is_rejected(tmp_path, mutation):
    root = tmp_path / "copy"
    shutil.copytree(SAVED, root)
    if mutation == "helper":
        (root / "pr150_helper.py").write_text("changed")
    else:
        path = root / "outcomes.json"
        rows = json.loads(path.read_text())
        if mutation == "missing":
            rows.pop()
        else:
            rows[0]["target"]["returncode"] = 0
        path.write_text(json.dumps(rows))
    with pytest.raises(ValueError):
        verify_standard_wrapper(root)
