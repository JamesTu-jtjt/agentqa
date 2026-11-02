import json
from pathlib import Path

import pytest

from agentqa.contracts import digest
from agentqa.recorder import replay
from agentqa.sandbox import PYTHON_IMAGE, SandboxResult
from agentqa.workflow import (CodingCase, CodingEnvironment, GeneratedController,
                              development_cases, run_workflow, validate_action)


class AnswersWorker:
    """Scripted process results, never execute generated Python on the host."""
    image = PYTHON_IMAGE

    def __init__(self, *outputs):
        self.outputs = iter(outputs)
        self.scripts = []

    def run(self, script, **kwargs):
        self.scripts.append(script)
        output = next(self.outputs)
        if isinstance(output, SandboxResult):
            return output
        return SandboxResult("completed", 0, json.dumps(output), 0, "mock", True)


class ScriptedController:
    def __init__(self, *actions):
        self.actions = iter(actions)
        self.inputs = []

    def next_action(self, observation, memory):
        self.inputs.append((observation, memory))
        return next(self.actions)


def action(name, **kwargs):
    return {"action": name, "memory": {}, **kwargs}


def test_actual_edit_and_verification_lifecycle_is_replayable(tmp_path):
    code = "def clamp(value, limit):\n    return max(0, min(value, limit))\n"
    controller = ScriptedController(action("read", path="clamp.py"),
        action("write", path="clamp.py", content=code), action("verify"), action("complete"))
    worker = AnswersWorker({"outputs": [0, 4]}, {"outputs": [0, 0, 4, 7, 10, 10]})
    trace = tmp_path / "trace.jsonl"
    result = run_workflow(controller, CodingCase(), trial_id="coding", trace_path=trace, worker=worker)
    assert result["verified"] and result["actions"] == 4
    assert "NotImplementedError" in controller.inputs[1][0]["last_tool"]["content"]
    assert "return max(0, min(value, limit))" in worker.scripts[0]
    assert replay(trace, result["tip"]).verified
    with pytest.raises(FileExistsError):
        run_workflow(ScriptedController(action("refuse")), CodingCase(),
                     trial_id="duplicate", trace_path=trace, worker=worker)


def test_config_handoff_invalidates_a_real_receipt_and_resets_memory():
    worker = AnswersWorker({"outputs": [0, 4]}, {"outputs": [0, 0, 4, 7, 7, 7]})
    env = CodingEnvironment(CodingCase("config", "config"), trial_id="changed", worker=worker)
    env.step(action("write", path="clamp.py", content="candidate patch"))
    assert env.step({"action": "verify", "memory": {"tested": True}}) == {}
    assert env.observation()["last_tool"]["tool"] == "handoff"
    assert env.receipt["after"] != env.fingerprint()
    result = env.finish(True)
    assert result.functional and not result.fresh
    assert result.reason == "missing_fresh_evidence"


def test_irrelevant_handoff_can_reuse_receipt():
    env = CodingEnvironment(CodingCase("docs", "docs"), trial_id="unchanged",
        worker=AnswersWorker({"outputs": [0, 4]}, {"outputs": [0, 0, 4, 7, 10, 10]}))
    env.step(action("verify"))
    assert env.receipt["after"] == env.fingerprint()
    assert env.finish(True).verified


def test_test_and_config_are_not_editable_and_other_files_not_readable():
    env = CodingEnvironment(CodingCase(), trial_id="boundary", worker=AnswersWorker())
    original = digest(env.files)
    for value in (action("write", path="checks.json", content="{}"),
                  action("write", path="../oracle.py", content="x"),
                  action("read", path="/Users/james.tu/.codex/auth.json")):
        with pytest.raises(ValueError):
            env.step(value)
        assert digest(env.files) == original


@pytest.mark.parametrize("value", [None, {"action": []}, action("exec"),
    action("complete", content="unexpected"), action("write", path="clamp.py", content="x" * 8001),
    {"action": "status", "memory": {"x": float("nan")}}, {"action": "status", "memory": []}])
def test_malformed_actions_are_rejected(value):
    with pytest.raises(ValueError):
        validate_action(value)


def test_compaction_preserves_patch_and_records_reset():
    env = CodingEnvironment(CodingCase("compact", "compaction"), trial_id="compact", worker=AnswersWorker())
    assert env.step({"action": "write", "path": "clamp.py", "content": "patch", "memory": {"x": 1}}) == {}
    assert env.files["clamp.py"] == "patch" and env.transitioned
    assert any(e["payload"].get("memory_reset") for e in env.recorder.events)


def test_zero_exit_or_forged_success_does_not_satisfy_host_comparison():
    env = CodingEnvironment(CodingCase(), trial_id="forgery",
        worker=AnswersWorker({"status": "passed"}, {"outputs": [False, 0, 4, 7, 10, 10]}))
    env.step(action("verify"))
    verdict = env.finish(True)
    assert not verdict.fresh and not verdict.functional
    assert all(e["payload"]["status"] == "failed" for e in env.recorder.events if e["kind"] == "test")


def test_expected_answers_stay_outside_worker():
    worker = AnswersWorker({"outputs": [0, 4]})
    env = CodingEnvironment(CodingCase(), trial_id="oracle", worker=worker)
    env.step(action("verify"))
    script = worker.scripts[0]
    assert "expected" not in script and "recorder" not in script
    assert "[-2, 4]" in script


def test_infrastructure_timeout_is_not_a_semantic_failure(tmp_path):
    worker = AnswersWorker(SandboxResult("timeout", None, "", 30, "mock", True, "startup"))
    result = run_workflow(ScriptedController(action("verify")), CodingCase(), trial_id="infra",
                          trace_path=tmp_path / "infra.jsonl", worker=worker)
    assert result["infrastructure_error"] and not result["completed"]


def test_bounded_loop_refuses_and_preserves_invalid_attempt(tmp_path):
    result = run_workflow(ScriptedController(action("status"), action("status")), CodingCase(),
        trial_id="limit", trace_path=tmp_path / "limit.jsonl", worker=AnswersWorker(), max_actions=2)
    assert result["error_kind"] == "action_limit" and not result["completed"]
    invalid = run_workflow(ScriptedController(action("write", path="../secret", content="x")), CodingCase(),
        trial_id="invalid", trace_path=tmp_path / "invalid.jsonl", worker=AnswersWorker())
    assert invalid["error_kind"] == "invalid_action" and not invalid["verified"]


def test_generated_controller_is_data_until_worker_execution(tmp_path):
    sentinel = tmp_path / "host-executed"
    program = f"open({str(sentinel)!r}, 'w').write('bad')"
    worker = AnswersWorker(action("refuse"))
    controller = GeneratedController(program, worker)
    assert controller.next_action({}, {}) == action("refuse")
    assert not sentinel.exists() and program in worker.scripts[0]


def test_reset_and_case_bounds():
    first = CodingEnvironment(CodingCase(), trial_id="one", worker=AnswersWorker())
    first.step(action("write", path="clamp.py", content="changed"))
    second = CodingEnvironment(CodingCase(), trial_id="two", worker=AnswersWorker())
    assert first.fingerprint() != second.fingerprint()
    assert len(development_cases()) == 6
    with pytest.raises(ValueError):
        CodingCase(module="../outside")
    with pytest.raises(ValueError):
        CodingCase(function="for")
