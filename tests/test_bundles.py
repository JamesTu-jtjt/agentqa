import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest

from agentqa.bundles import parse_result, run_bound_job, verify_bundle
from agentqa.contracts import digest


class AuthoredScheduler:
    def __init__(self, evaluator):
        self.evaluator = evaluator
        self.config = SimpleNamespace(eval_program_path=str(evaluator))
        self.calls = 0

    def submit_async(self, program, results):
        self.calls += 1
        return subprocess.Popen(self._build_command(program, results),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def get_job_results(self, process, results):
        return {"returncode": process.returncode}

    def _build_command(self, program, results):
        return [sys.executable, "-I", "-B", str(self.evaluator), program, results]


@pytest.fixture
def setup(tmp_path):
    program = tmp_path / "program.json"
    program.write_text('{"score": 1}')
    evaluator = tmp_path / "evaluate.py"
    return program, evaluator, AuthoredScheduler(evaluator)


def publish_source(extra="", correctness="True"):
    return ("import json, pathlib, sys\n"
            "program, root = map(pathlib.Path, sys.argv[1:])\n"
            "state = json.loads(program.read_text())\n"
            "(root/'metrics.json').write_text(json.dumps({'combined_score':state['score']}))\n"
            f"(root/'correct.json').write_text(json.dumps({{'correct':{correctness}}}))\n" + extra)


def invoke(setup, output, **kwargs):
    program, evaluator, scheduler = setup
    return run_bound_job(scheduler, program, evaluator, output, trusted_evaluator=True,
                         runtime_identity={"python": sys.version.split()[0]}, **kwargs)


def test_fresh_execution_and_negative_result_are_distinct_from_invalidity(setup, tmp_path):
    program, evaluator, scheduler = setup
    evaluator.write_text(publish_source())
    first = invoke(setup, tmp_path / "first")
    assert first["verdict"] == {"valid": True, "correct": True, "score": 1, "reason": "bound_result"}
    assert verify_bundle(tmp_path / "first", expected_request_hash=first["request_hash"],
                         expected_receipt_hash=first["receipt_hash"]).valid
    evaluator.write_text(publish_source(correctness="False"))
    second = invoke(setup, tmp_path / "second")
    assert second["verdict"]["valid"] and not second["verdict"]["correct"]
    assert first["request_hash"] != second["request_hash"]
    with pytest.raises(FileExistsError):
        invoke(setup, tmp_path / "first")
    assert scheduler.calls == 2


@pytest.mark.parametrize("source, reason", [
    ("raise SystemExit(7)", "execution_not_successful"),
    ("# zero exit; no publication", "incomplete_or_invalid_publication"),
    ("import pathlib,sys\n(pathlib.Path(sys.argv[2])/'metrics.json').write_text('{\"combined_score\":1}')",
     "incomplete_or_invalid_publication"),
    (publish_source() + "raise SystemExit(7)\n", "execution_not_successful")])
def test_missing_mixed_or_failed_publication_never_binds_old_results(setup, tmp_path, source, reason):
    _, evaluator, _ = setup
    old = tmp_path / "old-results"
    old.mkdir()
    (old / "correct.json").write_text('{"correct":true}')
    (old / "metrics.json").write_text('{"combined_score":99}')
    evaluator.write_text(source)
    result = invoke(setup, tmp_path / "attempt")
    assert result["verdict"]["reason"] == reason and not result["verdict"]["valid"]
    assert json.loads((old / "metrics.json").read_text())["combined_score"] == 99


def test_inputs_changed_during_execution_invalidates_even_successful_publication(setup, tmp_path):
    _, evaluator, _ = setup
    evaluator.write_text(publish_source("program.write_text('{\"score\":2}')\n"))
    result = invoke(setup, tmp_path / "changed")
    assert result["verdict"]["reason"] == "inputs_changed"


def test_frozen_identity_detects_result_receipt_and_cross_attempt_substitution(setup, tmp_path):
    _, evaluator, _ = setup
    evaluator.write_text(publish_source())
    result = invoke(setup, tmp_path / "bound")
    def check():
        return verify_bundle(tmp_path / "bound", expected_request_hash=result["request_hash"],
                             expected_receipt_hash=result["receipt_hash"])
    metrics = tmp_path / "bound/results/metrics.json"
    metrics.write_text('{"combined_score":1000}')
    assert check().reason == "artifact_mismatch"
    metrics.write_text('{"combined_score":1}')
    receipt_path = tmp_path / "bound/receipt.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["returncode"] = 7
    receipt_path.write_text(json.dumps(receipt))
    assert check().reason == "manifest_mismatch"
    assert not verify_bundle(tmp_path / "bound", expected_request_hash="0"*64,
                             expected_receipt_hash=digest(receipt)).valid


def test_symlink_artifacts_cannot_redirect_host_reads(setup, tmp_path):
    _, evaluator, _ = setup
    sentinel = tmp_path / "outside.json"
    sentinel.write_text('{"correct":true}')
    evaluator.write_text("import pathlib,sys\nroot=pathlib.Path(sys.argv[2])\n"
        "(root/'metrics.json').write_text('{\"combined_score\":1}')\n"
        f"(root/'correct.json').symlink_to({str(sentinel)!r})\n")
    result = invoke(setup, tmp_path / "links")
    assert not result["verdict"]["valid"]
    assert result["verdict"]["reason"] == "incomplete_or_invalid_publication"


@pytest.mark.parametrize("metrics, correctness", [
    ('{"combined_score":NaN}', '{"correct":true}'),
    ('{"combined_score":true}', '{"correct":true}'),
    ('{"combined_score":1,"combined_score":2}', '{"correct":true}'),
    ('{"combined_score":1}', '{"correct":"true"}')])
def test_ambiguous_result_json_is_rejected(tmp_path, metrics, correctness):
    (tmp_path / "metrics.json").write_text(metrics)
    (tmp_path / "correct.json").write_text(correctness)
    with pytest.raises(ValueError):
        parse_result(tmp_path)


def test_timeout_is_preserved_and_no_implicit_retry(setup, tmp_path):
    _, evaluator, scheduler = setup
    evaluator.write_text("import time\ntime.sleep(5)\n")
    result = invoke(setup, tmp_path / "timeout", timeout=.1)
    receipt = json.loads((tmp_path / "timeout/receipt.json").read_text())
    assert receipt["status"] == "timeout" and scheduler.calls == 1
    assert not result["verdict"]["valid"]


def test_local_adapter_requires_explicit_trusted_evaluator(setup, tmp_path):
    program, evaluator, scheduler = setup
    evaluator.write_text(publish_source())
    with pytest.raises(ValueError, match="fixed authored"):
        run_bound_job(scheduler, program, evaluator, tmp_path / "refused")
    assert scheduler.calls == 0 and not (tmp_path / "refused").exists()


def test_scheduler_cannot_silently_use_another_evaluator(setup, tmp_path):
    _, evaluator, scheduler = setup
    evaluator.write_text(publish_source())
    scheduler.config.eval_program_path = str(tmp_path / "other.py")
    with pytest.raises(ValueError, match="declared evaluator"):
        invoke(setup, tmp_path / "mismatched")
    assert scheduler.calls == 0
