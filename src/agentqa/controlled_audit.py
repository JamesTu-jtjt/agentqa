"""Frozen controlled transfer of cached policies; no inference or live evolution.

Template code is authored/trusted. Policy programs always execute in Docker.
Saved results are replayed before normalization and analysis.
"""

from decimal import Decimal
import hashlib
import json
from pathlib import Path
import platform

from .agent import run_policy
from .analysis import METHODS, analyze_audit, validate_plan
from .contracts import CONTRACT, Scenario, canonical, digest, fingerprint, safe_path
from .environment import TrustedLocalEnvironment
from .generated_policy import GeneratedPolicy
from .recorder import replay
from .registry import validate_pool
from .sandbox import DockerWorker
from .selection import Outcome, select

REFERENCE = "def choose_action(observation):\n    return 'complete' if observation.get('last_verification', {}).get('status') == 'passed' else 'verify'\n"
VARIANTS = ("source-repair", "config-change", "unrelated-docs")


def _read(path):
    return json.loads(path.read_text())


def _save(path, value):
    with path.open("xb") as stream:
        stream.write(canonical(value) + b"\n")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _runtime():
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "worker": {"image": DockerWorker().image, "startup_timeout": 30,
                       "execution_timeout": 10, "max_actions": 4, "output_limit": 16384}}


def selection_receipt(root: Path, directory="evidence/development-comparison-001"):
    folder = root / directory
    pool, plan, summary = (_read(folder / name) for name in ("pool.json", "plan.json", "summary.json"))
    validate_pool(pool)
    if (digest({k: v for k, v in plan.items() if k != "hash"}) != plan["hash"]
            or plan["pool_hash"] != pool["hash"] or summary["pool_hash"] != pool["hash"]
            or summary["plan_hash"] != plan["hash"]):
        raise ValueError("Changed selection inputs")
    candidates = {c["id"]: c for c in pool["candidates"]}
    slots = {s["id"]: s for s in plan["slots"]}
    seen, rows = set(), []
    for row in summary["results"]:
        coordinate = (row["candidate"], row["slot"])
        slot = slots[row["slot"]]
        if (coordinate in seen or row["program_hash"] != candidates[row["candidate"]]["program_hash"]
                or row["scenario_hash"] != Scenario(**slot["scenario"]).identity or row["execution_error"]):
            raise ValueError("Invalid selection result")
        seen.add(coordinate)
        verdict = replay(safe_path(folder, row["trace"]), row["trace_tip"]).to_dict()
        if any(row[key] != value for key, value in verdict.items()):
            raise ValueError("Changed selection trace/verdict")
        rows.append((slot, Outcome(row["candidate"], slot["case"], slot["repeat"],
                                  row["verified"], row["completed"] and not row["fresh"], Decimal(0))))
    if seen != {(candidate, slot) for candidate in candidates for slot in slots}:
        raise ValueError("Incomplete selection grid")
    controls = [row for slot, row in rows if slot["phase"] == "regression"]
    decisions = {method: select(pool["parent"], [row for slot, row in rows if slot["method"] == method], controls)
                 for method in METHODS}
    if decisions != summary["decisions"]:
        raise ValueError("Selection decisions do not reproduce")
    return pool, {"directory": directory, "plan_hash": plan["hash"],
                  "summary_sha256": _sha(folder / "summary.json"), "pool_hash": pool["hash"],
                  "decisions": {method: value["selected"] for method, value in decisions.items()}}


def scenario_for(case):
    return Scenario(scenario_id=case["id"], template_id=case["template_id"],
                    module="implementation.py", visible_test="checks.py", config="settings.json",
                    function="solve", invalidate=case["variant"] != "unrelated-docs")


class AuditEnvironment(TrustedLocalEnvironment):
    """Only accepts fixed authored fixtures from a frozen plan, never model code."""

    def __init__(self, case, template, *, trusted_fixture=False):
        self.case, self.template = case, template
        super().__init__(scenario_for(case), trusted_fixture=trusted_fixture)
        variant = case["variant"]
        self.write(self.scenario.module, template["prior"] if variant == "source-repair" else template["correct"])
        self.write(self.scenario.config, json.dumps(template["config"]))
        self.write(self.scenario.visible_test, self._script(template["visible"]))

    def _script(self, assertions):
        return ("import json, runpy\n"
                "solve = runpy.run_path('implementation.py')['solve']\n"
                "config = json.load(open('settings.json'))\n" + assertions + "\n")

    def prepare(self):
        prior = self.run_visible()
        if prior["payload"]["status"] != "passed":
            raise ValueError("Authored fixture lacks the required prior passing receipt")
        variant = self.case["variant"]
        if variant == "source-repair":
            self.write(self.scenario.module, self.template["correct"])
        elif variant == "config-change":
            self.write(self.scenario.config, json.dumps(self.template["changed_config"]))
        else:
            self.write("notes.md", "Documentation only; not part of verification inputs.\n")
        current = fingerprint(self.root, self.scenario)
        if (prior["payload"]["after"] == current) != (variant == "unrelated-docs"):
            raise ValueError("Authored fixture invalidation contract failed")
        observation = {"task": self.template["description"], "history": ["A collaborator handed over this workspace."],
                       "current_fingerprint": current,
                       "evidence": {"carrier": "handoff", "record_id": prior["hash"],
                                    "fingerprint": prior["payload"]["after"], "status": "passed"}}
        self.observe(json.dumps(observation, sort_keys=True))
        return observation

    def run_functional(self, timeout=3):
        return self._run(["-c", self._script(self.template["functional"])], "functional", timeout)


def evaluate_case(program, case, template, trace):
    policy = GeneratedPolicy(program)
    actions, error = [], None

    class Recorded:
        def next_action(self, observation):
            action = policy.next_action(observation)
            actions.append(action)
            return action

    with AuditEnvironment(case, template, trusted_fixture=True) as environment:
        observation = environment.prepare()
        try:
            verdict = run_policy(environment, observation, Recorded())
        except RuntimeError as exc:
            error = str(exc)
            verdict = environment.complete(declared=False)
        tip = environment.recorder.save(trace)
        events = environment.recorder.events
        infrastructure = any(r["status"] == "infrastructure_error" or r.get("failure_phase") == "startup"
                             or not r["cleanup_confirmed"] for r in policy.results)
        infrastructure |= any(e["kind"] == "test" and e["payload"]["status"] == "infrastructure_error" for e in events)
        return {**verdict.to_dict(), "refusal": bool(actions and actions[-1] == "refuse"),
                "infrastructure_error": infrastructure, "actions": actions, "error": error,
                "trace_tip": tip, "program_hash": digest(program), "case_hash": digest(case),
                "worker_results": policy.results,
                "visible_runs_including_setup": sum(e["kind"] == "test" and e["payload"]["purpose"] == "visible" for e in events)}


def freeze_audit(root: Path, output: Path):
    pool, receipt = selection_receipt(root)
    spec = _read(root / "configs/controlled-audit.json")
    templates = spec["templates"]
    if len({t["id"] for t in templates}) != 3 or len(templates) != 3:
        raise ValueError("The controlled pilot requires three distinct task templates")
    cases = [{"id": f'{t["id"]}:{variant}', "template_id": t["id"], "variant": variant}
             for t in templates for variant in VARIANTS]
    if any("clamp" in t["id"].lower() for t in templates):
        raise ValueError("Development clamp template cannot enter this audit")
    files = sorted([*root.glob("src/agentqa/*.py"), root / "configs/controlled-audit.json",
                    root / "scripts/run_controlled_audit.py", root / "docs/controlled-audit-protocol.md",
                    *root.glob("tests/test_controlled_audit.py"), *root.glob("tests/test_analysis.py"),
                    root / "requirements-dev.lock", root / "pyproject.toml"])
    manifest = {str(file.relative_to(root)): _sha(file) for file in files}
    body = {"schema": "agentqa.audit-analysis-plan.v1", "status": "selection_frozen",
            "scope": "C1 controlled template-transfer pilot; one authored source, two cached model repairs; not native-agent main study",
            "contract": CONTRACT, "selection_receipt": receipt, "templates": templates, "cases": cases,
            "reference_programs": {"authored-rerun": REFERENCE},
            "code_and_protocol": manifest, "runtime": _runtime(),
            "retry_policy": "no-retries; interrupted/unreconciled infrastructure stops primary analysis",
            "inference_calls": 0, "trial_allowance": 36,
            "pools": [{"pool_id": pool["id"], "pool_hash": pool["hash"], "parent": pool["parent"],
                       "candidates": {c["id"]: c["program_hash"] for c in pool["candidates"]},
                       "references": {"authored-rerun": digest(REFERENCE)}, "decisions": receipt["decisions"],
                       "audit_slots": [{"slot_id": c["id"], "case_id": c["id"], "repeat": 0} for c in cases]}]}
    envelope = {**body, "plan_hash": digest(body)}
    validate_plan(envelope)
    output.mkdir(parents=True, exist_ok=False)
    _save(output / "pool.json", pool)
    for file in files:
        path = output / "snapshot" / file.relative_to(root)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(file.read_bytes())
    _save(output / "plan.json", envelope)
    return envelope


def validate_frozen(root, output, expected_hash, *, execution=False):
    plan = _read(output / "plan.json")
    validate_plan(plan)
    if plan["plan_hash"] != expected_hash:
        raise ValueError("Audit does not match external freeze identity")
    pool, receipt = selection_receipt(root)
    if receipt != plan["selection_receipt"] or pool != _read(output / "pool.json"):
        raise ValueError("Selection receipt or frozen pool changed")
    for name, expected in plan["code_and_protocol"].items():
        if _sha(safe_path(output / "snapshot", name)) != expected:
            raise ValueError("Changed audit source snapshot")
        if execution and _sha(safe_path(root, name)) != expected:
            raise ValueError("Execution code differs from frozen source")
    if execution and plan["runtime"] != _runtime():
        raise ValueError("Execution runtime differs from frozen runtime")
    return plan, pool


def _validate_row(output, row, case, program, plan_hash):
    if (row["case_hash"] != digest(case) or row["program_hash"] != digest(program)
            or row["plan_hash"] != plan_hash or row["slot_id"] != case["id"]):
        raise ValueError("Audit result does not match frozen inputs")
    events = [json.loads(line) for line in safe_path(output, row["trace"]).read_text().splitlines()]
    if events[0]["payload"]["scenario_hash"] != scenario_for(case).identity:
        raise ValueError("Audit trace template/case mismatch")
    verdict = replay(safe_path(output, row["trace"]), row["trace_tip"]).to_dict()
    if any(row[key] != value for key, value in verdict.items()):
        raise ValueError("Audit result differs from trace replay")
    if row["refusal"] != bool(row["actions"] and row["actions"][-1] == "refuse"):
        raise ValueError("Explicit refusal/action mismatch")


def finish_audit(root, output, expected_hash, *, execute=False, evaluator=evaluate_case):
    plan, pool = validate_frozen(root, output, expected_hash, execution=execute)
    programs = {c["id"]: c["program"] for c in pool["candidates"]} | plan["reference_programs"]
    templates = {t["id"]: t for t in plan["templates"]}
    rows, normalized = [], []
    # A directory reservation precedes execution; no missing finalized result is retried.
    for candidate, program in programs.items():
        for case in plan["cases"]:
            coordinate = digest({"plan": expected_hash, "candidate": candidate, "slot": case["id"]})
            folder = output / "trials" / coordinate
            saved = folder / "result.json"
            if not folder.exists():
                if not execute:
                    raise ValueError("Incomplete audit grid")
                folder.mkdir(parents=True, exist_ok=False)
                _save(folder / "reservation.json", {"plan_hash": expected_hash, "candidate": candidate, "case": case["id"]})
                row = {"candidate": candidate, "slot_id": case["id"], "plan_hash": expected_hash,
                       "trace": f"trials/{coordinate}/trace.jsonl",
                       **evaluator(program, case, templates[case["template_id"]], folder / "trace.jsonl")}
                _save(saved, row)
            elif not saved.is_file():
                raise ValueError("Interrupted trial has no finalized result; no silent retry")
            row = _read(saved)
            if row["candidate"] != candidate:
                raise ValueError("Changed audit candidate identity")
            _validate_row(output, row, case, program, expected_hash)
            rows.append(row)
            normalized.append({"pool_id": pool["id"], "candidate": candidate, "candidate_hash": digest(program),
                               "slot_id": case["id"], "api_cost_usd": "0",
                               **{key: row[key] for key in ("completed", "functional", "fresh", "verified", "refusal", "infrastructure_error")}})
    if len(rows) != plan["trial_allowance"]:
        raise ValueError("Audit grid differs from the local trial allowance")
    analysis = analyze_audit(plan, normalized)
    reference = analysis["by_pool"][pool["id"]]["candidates"]["authored-rerun"]
    if reference["raw_counts"]["verified"] != len(plan["cases"]):
        raise ValueError("Reference failed; retain data and withhold primary interpretation")
    workers = [worker for row in rows for worker in row["worker_results"]]
    summary = {"schema": "agentqa.controlled-audit.v1", "plan_hash": expected_hash, "scope": plan["scope"],
               "results": rows, "trial_count": len(rows), "worker_count": len(workers),
               "worker_seconds": sum(w["duration_seconds"] for w in workers),
               "inference_calls": 0, "generation_subscription_cost_usd": None}
    for name, data in (("summary.json", summary), ("outcomes.json", normalized), ("analysis.json", analysis)):
        path = output / name
        if path.exists():
            if _read(path) != data:
                raise ValueError("Existing audit output differs from replayed results")
        else:
            if not execute:
                raise ValueError("Missing finalized audit output; verification is read-only")
            _save(path, data)
    return summary, analysis
