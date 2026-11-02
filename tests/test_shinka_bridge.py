import json

import pytest

from agentqa import shinka_bridge


def test_candidate_is_read_as_data_and_bad_fitness_is_not_an_interface_error(tmp_path, monkeypatch):
    marker = tmp_path / "must-not-be-created"
    program = f"from pathlib import Path\nPath({str(marker)!r}).write_text('host import')\n"
    candidate = tmp_path / "candidate.py"
    candidate.write_text(program)
    calls = []
    def fake_evaluation(source, scenario, trace):
        calls.append(source)
        return {"error": None, "verified": False, "reason": "missing_fresh_evidence"}
    monkeypatch.setattr(shinka_bridge, "evaluate_program", fake_evaluation)
    output = tmp_path / "out"
    artifact = shinka_bridge.evaluate(candidate, output)
    assert calls == [program]
    assert not marker.exists()
    assert artifact["correct"]["correct"] is True
    assert artifact["metrics"]["combined_score"] == 0
    assert json.loads((output / "metrics.json").read_text())["trial_count"] == 1
    with pytest.raises(ValueError):
        shinka_bridge.evaluate(candidate, output)


def test_invalid_candidate_is_retained_as_failed_evaluation(tmp_path):
    candidate = tmp_path / "candidate.py"
    candidate.write_text(" ")
    artifact = shinka_bridge.evaluate(candidate, tmp_path / "out")
    assert artifact["correct"]["correct"] is False
    assert artifact["metrics"]["combined_score"] == 0
    assert artifact["correct"]["error"]
