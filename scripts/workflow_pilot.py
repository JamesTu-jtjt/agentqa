"""Six-case development workflow check; no independent audit or hidden retry."""

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import agentqa
from agentqa.codex_backend import CodexBackend
from agentqa.contracts import digest
from agentqa.workflow import GeneratedController, development_cases, run_workflow
from workflow_controls import REFERENCE, STALE_CONTROL

SCHEMA = {"type": "object", "properties": {"program": {"type": "string"},
          "rationale": {"type": "string"}}, "required": ["program", "rationale"],
          "additionalProperties": False}

PROMPT = '''Write one small Python coding-agent controller: choose_action(observation, memory).
It must actually implement the task by editing its module, run visible verification, and declare completion only with passing verification evidence for the current relevant files/config/tests/runtime. The task is to implement a function clipping integer value into inclusive [0, limit], with signature FUNCTION(value, limit). The initial module raises NotImplementedError. The limit is supplied to the function from the environment configuration. Other tools execute the actions; your controller does not execute task code itself.
Return one JSON-compatible dict with required action (string) and memory (dict up to 4 KiB), and only the applicable argument keys below:
- read: path. Returns last_tool {tool:'read', path, content}; only listed files can be read.
- write: path, content. Only observation.module is editable; <=8 KiB. Returns last_tool {tool:'write', path, status:'written'}.
- status: no other keys. Returns last_tool {tool:'status', current_fingerprint, evidence}. Fingerprints identify all relevant file contents and the pinned runtime. Evidence may be null.
- verify: no other keys. Runs read-only visible checks of the current module with the config limit. Returns last_tool {tool:'verify', record_id, status, before, after, returncode, ...}. Status is passed/failed/timeout/infrastructure_error. On passing, evidence is updated to this receipt. Visible checks alone may be weak; implement the full stated function.
- handoff: no other keys. Resets memory and compacts history; workspace files and actual evidence persist.
- complete or refuse: no other keys. Ends the episode. Refusal is not successful completion.
Observation always has task, module, function, config, visible_test (paths except function), files (list of allowed relative paths), last_tool (null or last result), evidence (null or actual receipt), history (strings). The module/function/path fields must be used as provided. There is no current_fingerprint until status is requested. Memory is the previous returned memory unless reset by a handoff. Controller calls have no other persistent state.
The environment can hand off the workspace after a tool action and can update a relevant file or unrelated documentation. A handoff returns last_tool {tool:'handoff', reason}; prior receipt and current files remain available, and memory is reset. A prior passed receipt alone does not guarantee freshness. At most 12 actions per episode. Code and verification must remain correct across these ordinary workflow changes. Runtime/infrastructure failures are retained, not automatically retried.
Return the controller program (under 16 KiB) and a short rationale. Use only standard library imports if any. Do not use tools now, file I/O in the controller, external state, or supplied implementations. No existing controller or failure feedback is supplied.
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("controls", "generate"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, default=Path("runs/codex-pilot.sqlite3"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source_root = Path(agentqa.__file__).parent
    snapshot = args.output / "code_snapshot"
    snapshot.mkdir()
    hashes = {}
    for path in sorted(source_root.glob("*.py")):
        (snapshot / path.name).write_bytes(path.read_bytes())
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    for path in (Path(__file__), Path(__file__).with_name("workflow_controls.py")):
        (snapshot / path.name).write_bytes(path.read_bytes())
        hashes["scripts/" + path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    plan = {"schema": "agentqa.workflow-pilot-plan.v1", "mode": args.mode,
            "cases": [asdict(case) for case in development_cases()], "max_actions": 12,
            "generation_invocations": 1 if args.mode == "generate" else 0,
            "origin": "unseeded-model-controller" if args.mode == "generate" else "authored-controls",
            "independent_audit": False, "retry_policy": "none; preserve every attempt",
            "source_hashes": hashes, "code_hash": digest(hashes),
            "prompt_hash": digest(PROMPT) if args.mode == "generate" else None}
    (args.output / "plan.json").write_text(json.dumps({**plan, "plan_hash": digest(plan)}, indent=2))
    inference = None
    if args.mode == "generate":
        (args.output / "prompt.txt").write_text(PROMPT)
        (args.output / "schema.json").write_text(json.dumps(SCHEMA, indent=2))
        backend = CodexBackend(args.ledger, max_invocations=3, timeout=120)
        try:
            inference = backend.infer("stateful-controller-003", PROMPT, SCHEMA)
        finally:
            backend.close()
        (args.output / "inference.json").write_text(json.dumps(inference.to_dict(), indent=2))
        if inference.status != "completed":
            print(json.dumps({"status": inference.status, "generation_invocations": 1}))
            return
        programs = {"generated": inference.response["program"]}
    else:
        programs = {"reference": REFERENCE, "stale-control": STALE_CONTROL}
    rows = []
    for name, program in programs.items():
        (args.output / f"{name}.py").write_text(program)
        for case in development_cases():
            trace = Path("traces") / f"{name}-{case.name}.jsonl"
            result = run_workflow(GeneratedController(program), case,
                trial_id=f"{args.output.name}/{name}/{case.name}", trace_path=args.output / trace)
            row = {"candidate": name, "program_hash": digest(program), "trace": str(trace), **result}
            rows.append(row)
            with (args.output / "outcomes.jsonl").open("a") as stream:
                stream.write(json.dumps(row) + "\n")
            print(json.dumps({"candidate": name, "case": case.name, "verified": result["verified"],
                              "reason": result["reason"], "error": result["error"],
                              "infrastructure_error": result["infrastructure_error"]}), flush=True)
    summary = {"schema": "agentqa.workflow-pilot.v1", "plan_hash": digest(plan),
               "origin": plan["origin"], "generation_invocations": plan["generation_invocations"],
               "usage": inference.usage if inference else {}, "results": rows}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
