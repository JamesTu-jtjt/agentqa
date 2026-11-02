import json
from pathlib import Path
import subprocess

import pytest

from agentqa.codex_backend import CodexBackend, CodexLimitError
from agentqa.generated_policy import GeneratedPolicy
from agentqa.sandbox import SandboxResult


def fake_process(monkeypatch, *, tool_use=False, returncode=0):
    calls = []

    class Process:
        def __init__(self, command, **kwargs):
            calls.append((command, kwargs))
            self.command, self.kwargs, self.returncode = command, kwargs, returncode

        def communicate(self, prompt, timeout):
            assert b"example" in prompt
            path = Path(self.command[self.command.index("--output-last-message") + 1])
            path.write_text('{"action":"verify"}')
            events = [{"type": "turn.completed", "usage": {"input_tokens": 9, "output_tokens": 3}}]
            if tool_use:
                events.append({"type": "item.completed", "item": {"type": "command_execution"}})
            for event in events:
                self.kwargs["stdout"].write((json.dumps(event) + "\n").encode())

    monkeypatch.setattr(subprocess, "Popen", Process)
    return calls


def test_saved_auth_route_model_and_usage_are_explicit(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "not-a-real-key")
    monkeypatch.setenv("CODEX_API_KEY", "also-not-a-key")
    calls = fake_process(monkeypatch)
    backend = CodexBackend(tmp_path / "calls.sqlite3", max_invocations=1)
    result = backend.infer("one", "example", {"type": "object"})
    assert result.status == "completed"
    assert result.response == {"action": "verify"}
    assert result.usage == {"input_tokens": 9, "output_tokens": 3}
    command, kwargs = calls[0]
    assert command[command.index("--model") + 1] == "gpt-6.1-sol"
    assert "--ignore-user-config" in command and "--ephemeral" in command
    assert "OPENAI_API_KEY" not in kwargs["env"] and "CODEX_API_KEY" not in kwargs["env"]
    assert not Path(kwargs["cwd"]).exists()  # Isolated prompt directory is removed.
    backend.close()


def test_call_cap_and_ids_persist_across_restarts(tmp_path, monkeypatch):
    calls = fake_process(monkeypatch, returncode=1)
    path = tmp_path / "calls.sqlite3"
    backend = CodexBackend(path, max_invocations=1)
    assert backend.infer("one", "example", {}).status == "infrastructure_error"
    backend.close()
    backend = CodexBackend(path, max_invocations=1)
    with pytest.raises(CodexLimitError):
        backend.infer("one", "example", {})
    with pytest.raises(CodexLimitError):
        backend.infer("two", "example", {})
    assert len(calls) == 1
    backend.close()


def test_unexpected_tool_use_is_an_invalid_trial(tmp_path, monkeypatch):
    fake_process(monkeypatch, tool_use=True)
    backend = CodexBackend(tmp_path / "calls.sqlite3", max_invocations=1)
    assert backend.infer("one", "example", {}).status == "unexpected_tool_use"
    backend.close()


@pytest.mark.parametrize("output", ['{"action":"read_secret"}', 'noise\n{"action":"complete"}', '{}'])
def test_generated_output_cannot_invent_tool_actions(output):
    class Worker:
        def run(self, script):
            return SandboxResult("completed", 0, output, 0, "mock", True)
    with pytest.raises(RuntimeError):
        GeneratedPolicy("unused", Worker()).next_action({})
