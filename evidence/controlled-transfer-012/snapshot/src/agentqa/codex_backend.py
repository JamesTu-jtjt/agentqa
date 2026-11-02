"""Small serial inference jobs through the user's existing Codex login.

Dollar cost is unavailable for subscription usage. Durable invocation counts,
runtime limits, and reported token usage bound/describe the pilot instead.
"""

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import signal
import sqlite3
import subprocess
import tempfile
import time

from .contracts import digest


class CodexLimitError(RuntimeError):
    pass


@dataclass(frozen=True)
class CodexResult:
    status: str
    response: dict | None
    usage: dict
    returncode: int | None
    duration_seconds: float
    stderr: str
    events: list[dict]

    def to_dict(self):
        return asdict(self)


class CodexBackend:
    def __init__(self, ledger: Path, *, max_invocations: int = 3,
                 model: str = "gpt-6.1-sol", timeout: float = 120):
        if not 1 <= max_invocations <= 6 or not 0 < timeout <= 180:
            raise ValueError("Codex pilot limits exceed the small-run envelope")
        ledger.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(ledger, timeout=10, isolation_level=None)
        self.db.execute("CREATE TABLE IF NOT EXISTS limits (id INTEGER PRIMARY KEY, calls INTEGER, model TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS invocations (id TEXT PRIMARY KEY, prompt_hash TEXT, status TEXT, result TEXT)")
        self.db.execute("INSERT OR IGNORE INTO limits VALUES (1, ?, ?)", (max_invocations, model))
        if self.db.execute("SELECT calls, model FROM limits WHERE id=1").fetchone() != (max_invocations, model):
            raise CodexLimitError("Cannot silently change model or invocation allowance")
        self.model, self.max_invocations, self.timeout = model, max_invocations, timeout

    def close(self):
        self.db.close()

    def infer(self, invocation_id: str, prompt: str, schema: dict) -> CodexResult:
        if not invocation_id or len(prompt.encode()) > 12000:
            raise ValueError("Invocation identity/prompt exceeds pilot bounds")
        self.db.execute("BEGIN IMMEDIATE")
        try:
            if self.db.execute("SELECT 1 FROM invocations WHERE id=?", (invocation_id,)).fetchone():
                raise CodexLimitError("Invocation already exists; inspect saved result rather than retrying")
            if self.db.execute("SELECT COUNT(*) FROM invocations").fetchone()[0] >= self.max_invocations:
                raise CodexLimitError("Codex invocation allowance exhausted")
            self.db.execute("INSERT INTO invocations VALUES (?, ?, 'reserved', NULL)",
                            (invocation_id, digest({"prompt": prompt, "schema": schema})))
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        started = time.monotonic()
        events = []
        response, code, usage = None, None, {}
        status = "infrastructure_error"
        error = ""
        with tempfile.TemporaryDirectory(prefix="agentqa-codex-") as directory:
            root = Path(directory)
            (root / "schema.json").write_text(json.dumps(schema))
            command = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--skip-git-repo-check",
                       "--sandbox", "read-only", "--json", "--color", "never", "--model", self.model,
                       "--output-schema", str(root / "schema.json"),
                       "--output-last-message", str(root / "response.json"),
                       "-c", 'model_reasoning_effort="low"', "-c", 'web_search="disabled"',
                       "-c", 'forced_login_method="chatgpt"',
                       "-c", 'developer_instructions="Return only the requested structured answer. Use no tools. This is an experiment inference call."',
                       "-C", directory]
            for feature in ("shell_tool", "apps", "plugins", "hooks", "multi_agent", "goals",
                            "browser_use", "computer_use", "image_generation", "view_image",
                            "code_mode_host", "shell_snapshot", "unbounded_connection_retries"):
                command += ["--disable", feature]
            command.append("-")
            environment = dict(os.environ)
            for variable in ("OPENAI_API_KEY", "CODEX_API_KEY"):
                environment.pop(variable, None)
            with tempfile.TemporaryFile() as output, tempfile.TemporaryFile() as errors:
                try:
                    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=output,
                                               stderr=errors, cwd=root, env=environment,
                                               start_new_session=True)
                    try:
                        process.communicate(prompt.encode(), timeout=self.timeout)
                        code = process.returncode
                        status = "completed" if code == 0 else "infrastructure_error"
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.communicate()
                        status = "timeout"
                    output.seek(0)
                    raw = output.read(2_000_001)
                    errors.seek(0)
                    error = errors.read(8192).decode(errors="replace")
                    if len(raw) > 2_000_000:
                        status = "output_limit"
                    else:
                        events = [json.loads(line) for line in raw.decode().splitlines() if line.strip()]
                    for event in events:
                        if event.get("type") == "turn.completed":
                            usage = event.get("usage", {})
                    tool_types = {"command_execution", "file_change", "mcp_tool_call", "web_search"}
                    if any(event.get("item", {}).get("type") in tool_types for event in events):
                        status = "unexpected_tool_use"
                    if status == "completed":
                        response = json.loads((root / "response.json").read_text())
                        if not isinstance(response, dict):
                            status = "invalid_response"
                except (OSError, ValueError) as exc:
                    status = "infrastructure_error"
                    error += str(exc)
        result = CodexResult(status, response, usage, code, time.monotonic() - started, error, events)
        self.db.execute("UPDATE invocations SET status=?, result=? WHERE id=?",
                        (status, json.dumps(result.to_dict()), invocation_id))
        return result
