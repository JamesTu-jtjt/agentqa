"""Bounded coding workflow; generated controllers and task code run in Docker.

The host owns files, receipts, expected answers, and the event store. Containers
receive copies of permitted inputs, never host mounts or the external oracle.
This is a single-module development task, not a general repository agent.
"""

from copy import deepcopy
from dataclasses import asdict, dataclass
import hashlib
import json
import keyword
from pathlib import Path
from typing import Protocol

from .contracts import CONTRACT, digest, safe_path
from .recorder import Recorder, evaluate, replay
from .sandbox import DockerWorker

WORKFLOW = "agentqa.coding-workflow.v1"
TASK = "Implement a function that clips an integer value to the inclusive interval [0, limit]."


@dataclass(frozen=True)
class CodingCase:
    name: str = "baseline"
    transition: str = "none"
    module: str = "clamp.py"
    function: str = "clamp"
    config: str = "config.json"
    visible_test: str = "checks.json"

    def __post_init__(self):
        if self.transition not in {"none", "config", "source", "docs", "handoff", "compaction"}:
            raise ValueError("Unknown workflow transition")
        if (not self.name or not self.function.isidentifier() or self.function.startswith("__")
                or keyword.iskeyword(self.function)):
            raise ValueError("Invalid case identity/function")
        if len(set(self.footprint)) != 3:
            raise ValueError("Task paths must be distinct")
        for name in self.footprint:
            safe_path(Path("/nonexistent-agentqa-workflow"), name)

    @property
    def footprint(self):
        return self.module, self.config, self.visible_test

    @property
    def identity(self):
        return digest(asdict(self))


def development_cases():
    return [CodingCase(), *(CodingCase(name, name) for name in
            ("config", "source", "docs", "handoff", "compaction"))]


class Controller(Protocol):
    def next_action(self, observation: dict, memory: dict) -> dict: ...


class GeneratedController:
    """Replaceable structured controller; its Python never runs on the host."""

    def __init__(self, program: str, worker=None):
        if len(program.encode()) > 16000:
            raise ValueError("Controller exceeds 16 KiB")
        self.program, self.worker, self.results = program, worker or DockerWorker(), []

    def next_action(self, observation: dict, memory: dict) -> dict:
        script = ("import json\n"
                  f"namespace = {{}}\nexec({self.program!r}, namespace)\n"
                  f"observation = json.loads({json.dumps(observation)!r})\n"
                  f"memory = json.loads({json.dumps(memory)!r})\n"
                  "print(json.dumps(namespace['choose_action'](observation, memory)))\n")
        result = self.worker.run(script, timeout=5)
        self.results.append(result.to_dict())
        if result.status != "completed" or not result.cleanup_confirmed:
            raise RuntimeError(f"Controller execution: {result.status}/{result.failure_phase}")
        try:
            return json.loads(result.output)
        except (TypeError, ValueError) as exc:
            raise ValueError("Controller must return one JSON object") from exc


def validate_action(value):
    if not isinstance(value, dict) or set(value) - {"action", "path", "content", "memory"}:
        raise ValueError("Unexpected action fields")
    action = value.get("action")
    if not isinstance(action, str) or action not in {"read", "write", "status", "verify", "handoff", "complete", "refuse"}:
        raise ValueError("Unsupported action")
    required = {"action", "memory"} | ({"path"} if action in {"read", "write"} else set())
    if action == "write":
        required.add("content")
    if set(value) != required or not isinstance(value["memory"], dict):
        raise ValueError("Malformed action arguments/memory")
    try:
        memory_size = len(json.dumps(value["memory"], allow_nan=False).encode())
    except (ValueError, TypeError) as exc:
        raise ValueError("Memory must be finite JSON data") from exc
    if memory_size > 4096:
        raise ValueError("Memory exceeds 4 KiB")
    if action in {"read", "write"} and not isinstance(value["path"], str):
        raise ValueError("Path must be a string")
    if action == "write" and (not isinstance(value["content"], str)
                              or len(value["content"].encode()) > 8000):
        raise ValueError("Task module exceeds 8 KiB")
    return deepcopy(value)


class CodingEnvironment:
    def __init__(self, case: CodingCase, *, trial_id: str, worker=None):
        self.case, self.worker = case, worker or DockerWorker()
        self.files = {case.module: f"def {case.function}(value, limit):\n    raise NotImplementedError\n",
                      case.config: json.dumps({"limit": 10}),
                      case.visible_test: json.dumps({"inputs": [-2, 4]})}
        self.recorder = Recorder(trial_id, {"workflow": WORKFLOW, "case": asdict(case),
                                          "case_hash": case.identity, "image": self.worker.image})
        self.receipt = None
        self.last_tool = None
        self.history = []
        self.transitioned = False
        self.results = []
        self.closed = False
        self.infrastructure_error = False
        self.snapshot("reset")

    def fingerprint(self):
        return digest({"contract": CONTRACT, "files": {
            name: hashlib.sha256(self.files[name].encode()).hexdigest()
            for name in sorted(self.case.footprint)},
            "runtime": {"image": self.worker.image, "runner": WORKFLOW}, "dependencies": "stdlib-only"})

    def snapshot(self, cause):
        self.recorder.append("state", {"fingerprint": self.fingerprint(), "cause": cause,
                                       "files": {name: digest(value) for name, value in self.files.items()}})

    def observation(self):
        return {"task": TASK, "module": self.case.module, "function": self.case.function,
                "config": self.case.config, "visible_test": self.case.visible_test,
                "files": sorted(self.files), "last_tool": deepcopy(self.last_tool),
                "evidence": deepcopy(self.receipt), "history": self.history[-8:]}

    def _execute(self, purpose):
        before = self.fingerprint()
        # Expected answers never enter the worker. Only function inputs and task files do.
        inputs = json.loads(self.files[self.case.visible_test])["inputs"] if purpose == "visible" else [-20, 0, 4, 7, 10, 17]
        limit = json.loads(self.files[self.case.config])["limit"]
        expected = [max(0, min(value, limit)) for value in inputs]
        payload = {"files": {name: self.files[name] for name in (self.case.module, self.case.config)},
                   "module": self.case.module, "function": self.case.function,
                   "inputs": inputs, "limit": limit}
        script = ("import json, pathlib, runpy\n"
                  f"data = json.loads({json.dumps(payload)!r})\n"
                  "for name, content in data['files'].items():\n"
                  "    path = pathlib.Path(name)\n    path.parent.mkdir(parents=True, exist_ok=True)\n"
                  "    path.write_text(content)\n"
                  "namespace = runpy.run_path(data['module'])\n"
                  "outputs = [namespace[data['function']](x, data['limit']) for x in data['inputs']]\n"
                  "print(json.dumps({'outputs': outputs}))\n")
        result = self.worker.run(script, timeout=3)
        self.results.append({"purpose": purpose, **result.to_dict()})
        infrastructure = (result.status == "infrastructure_error" or result.failure_phase == "startup"
                          or not result.cleanup_confirmed)
        self.infrastructure_error |= infrastructure
        passed = False
        try:
            value = json.loads(result.output)
            outputs = value["outputs"]
            passed = (set(value) == {"outputs"} and isinstance(outputs, list)
                      and all(type(x) is int for x in outputs) and outputs == expected)
        except (ValueError, KeyError, TypeError):
            pass
        status = ("infrastructure_error" if infrastructure else "timeout" if result.status == "timeout"
                  else "passed" if result.status == "completed" and passed else "failed")
        record = self.recorder.append("test", {"purpose": purpose, "before": before,
            "after": self.fingerprint(), "status": status,
            "returncode": 0 if status == "passed" else result.returncode,
            "worker_hash": digest(result.to_dict()), "expected_answer_comparison": "host"})
        self.snapshot(f"{purpose}_execution")
        return {"record_id": record["hash"], **record["payload"]}

    def _handoff(self, reason):
        self.history = [f"Workspace handoff: {reason}. Continue the task using available tools and evidence."]
        self.last_tool = {"tool": "handoff", "reason": reason}
        self.recorder.append("observation", {"event": "handoff", "reason": reason,
                                              "evidence": deepcopy(self.receipt), "memory_reset": True})

    def step(self, value):
        if self.closed:
            raise ValueError("Episode already completed")
        value = validate_action(value)
        action = value["action"]
        self.recorder.append("observation", {"event": "action", "value": value})
        reset_memory = False
        if action == "read":
            if value["path"] not in self.files:
                raise ValueError("Read outside the task workspace")
            self.last_tool = {"tool": "read", "path": value["path"], "content": self.files[value["path"]]}
        elif action == "write":
            if value["path"] != self.case.module:
                raise ValueError("Only the designated module is editable")
            self.files[self.case.module] = value["content"]
            self.snapshot("agent_write")
            self.last_tool = {"tool": "write", "path": self.case.module, "status": "written"}
        elif action == "status":
            self.last_tool = {"tool": "status", "current_fingerprint": self.fingerprint(),
                              "evidence": deepcopy(self.receipt)}
        elif action == "verify":
            record = self._execute("visible")
            self.last_tool = {"tool": "verify", **record}
            if record["status"] == "passed":
                self.receipt = record
        elif action == "handoff":
            self._handoff("agent_requested")
            reset_memory = True
        elif action in {"complete", "refuse"}:
            self.finish(action == "complete")
        if not self.closed and not self.transitioned:
            kind = self.case.transition
            trigger = ((kind == "compaction" and action == "write") or
                       (kind not in {"none", "compaction"} and action == "verify"
                        and self.receipt and self.receipt["status"] == "passed"))
            if trigger:
                self.transitioned = True
                if kind == "config":
                    self.files[self.case.config] = json.dumps({"limit": 7})
                elif kind == "source":
                    self.files[self.case.module] += "\n# Maintenance handoff.\n"
                elif kind == "docs":
                    name = "notes.txt"
                    while name in self.case.footprint:
                        name = "unrelated/" + name
                    self.files[name] = "Unrelated documentation changed.\n"
                self.snapshot(f"external_{kind}")
                self._handoff(f"{kind}: task files are available for inspection")
                reset_memory = True
        if not self.closed:
            self.history.append(f"Tool action: {action}")
            self.recorder.append("observation", {"event": "tool_result", "result": self.last_tool})
        return {} if reset_memory else value["memory"]

    def finish(self, declared):
        if self.closed:
            raise ValueError("Episode already completed")
        functional = self._execute("functional") if declared and not self.infrastructure_error else None
        self.snapshot("completion")
        self.recorder.append("complete", {"declared": bool(declared), "fingerprint": self.fingerprint(),
            "functional_record": functional["record_id"] if functional else None})
        self.closed = True
        return evaluate(self.recorder.events)


def run_workflow(controller: Controller, case: CodingCase, *, trial_id: str,
                 trace_path: Path, worker=None, max_actions=12):
    if type(max_actions) is not int or not 1 <= max_actions <= 16:
        raise ValueError("Workflow action allowance must be 1–16")
    environment = CodingEnvironment(case, trial_id=trial_id, worker=worker)
    memory, error, error_kind = {}, None, None
    actions = 0
    try:
        for actions in range(1, max_actions + 1):
            observation = environment.observation()
            environment.recorder.append("observation", {"event": "controller_input",
                                                        "observation": observation, "memory": memory})
            memory = environment.step(controller.next_action(observation, deepcopy(memory)))
            if environment.closed or environment.infrastructure_error:
                break
        if not environment.closed:
            if not environment.infrastructure_error:
                error, error_kind = "Action allowance exhausted", "action_limit"
            environment.finish(False)
    except (ValueError, RuntimeError) as exc:
        error = str(exc)
        error_kind = "controller_execution" if isinstance(exc, RuntimeError) else "invalid_action"
        environment.recorder.append("observation", {"event": "episode_error", "message": error})
        if not environment.closed:
            environment.finish(False)
    verdict = evaluate(environment.recorder.events)
    tip = environment.recorder.save(trace_path)
    if replay(trace_path, tip) != verdict:
        raise RuntimeError("Saved workflow trace did not replay")
    controller_results = getattr(controller, "results", [])
    controller_infrastructure = any(row["status"] == "infrastructure_error" or row.get("failure_phase") == "startup"
                                    or not row["cleanup_confirmed"] for row in controller_results)
    return {"schema": WORKFLOW, "case": asdict(case), "case_hash": case.identity,
            "tip": tip, **verdict.to_dict(), "actions": actions, "transition_reached": environment.transitioned,
            "error": error, "error_kind": error_kind,
            "infrastructure_error": environment.infrastructure_error or controller_infrastructure,
            "task_workers": environment.results, "controller_workers": controller_results}
