"""Frozen, matched development suites with resumable local trial accounting."""

from dataclasses import asdict
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import sqlite3

from .contracts import Scenario, canonical, digest
from .evaluation import evaluate_program
from .families import transform
from .recorder import replay
from .registry import validate_pool
from .selection import Outcome, select


def development_slots() -> list[dict]:
    source = Scenario()
    operators = {
        "source-only": ("identity",) * 6,
        "generic": ("identity", "rename", "noise") * 2,
        "failure-family": ("identity", "rename", "noise", "compaction", "handoff", "cache"),
    }
    slots = []
    for method, names in operators.items():
        for index, name in enumerate(names):
            slots.append({"id": f"{method}:{index}", "method": method, "phase": "selection",
                          "case": str(index), "repeat": 0, "operator": name,
                          "scenario": asdict(transform(source, name).scenario)})
    # Two legitimate-completion controls. These are shared across all selectors.
    for index, base in enumerate((source, transform(source, "rename").scenario)):
        slots.append({"id": f"regression:{index}", "method": "shared", "phase": "regression",
                      "case": str(index), "repeat": 0, "operator": "unchanged",
                      "scenario": asdict(transform(base, "unchanged").scenario)})
    return slots


def freeze_plan(pool: dict, slots: list[dict]) -> dict:
    validate_pool(pool)
    ids = [slot["id"] for slot in slots]
    if not slots or len(ids) != len(set(ids)):
        raise ValueError("Plan requires unique trial-slot IDs")
    methods = {slot["method"] for slot in slots if slot["phase"] == "selection"}
    if methods != {"source-only", "generic", "failure-family"}:
        raise ValueError("Plan requires all three selectors")
    counts = {method: sum(slot["phase"] == "selection" and slot["method"] == method for slot in slots)
              for method in methods}
    if len(set(counts.values())) != 1:
        raise ValueError("Selectors must have matched rollout allowances")
    coordinates = [(slot["phase"], slot["method"], slot["case"], slot["repeat"]) for slot in slots]
    if len(coordinates) != len(set(coordinates)) or not any(slot["phase"] == "regression" for slot in slots):
        raise ValueError("Plan requires unique trial coordinates and common regression controls")
    for slot in slots:
        if slot["phase"] not in ("selection", "regression"):
            raise ValueError("This runner is development-only; independent audit needs a separate freeze")
        Scenario(**slot["scenario"])
    package = Path(__file__).parent
    code = {str(path.relative_to(package)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(package.rglob("*.py"))}
    body = {"schema": "agentqa.comparison-plan.v1", "scope": "development-only",
            "pool_hash": pool["hash"], "code_hash": digest(code), "slots": slots,
            "candidate_ids": [candidate["id"] for candidate in pool["candidates"]],
            "retry_policy": "no-automatic-retries", "incremental_evaluation_inference_calls": 0}
    return {**body, "hash": digest(body)}


def _validate_result(row: dict, trace_path: Path, candidate: dict, scenario: Scenario):
    if row["program_hash"] != candidate["program_hash"] or row["scenario_hash"] != scenario.identity:
        raise ValueError("Saved trial does not match the frozen inputs")
    verdict = replay(trace_path, row["trace_tip"])
    if any(row[key] != value for key, value in verdict.to_dict().items()):
        raise ValueError("Saved verdict differs from trace replay")


def run_comparison(pool: dict, output: Path, *, evaluator=evaluate_program) -> dict:
    plan = freeze_plan(pool, development_slots())
    if len(plan["slots"]) * len(pool["candidates"]) > 180:
        raise ValueError("Development comparison exceeds local trial envelope")
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / "plan.json"
    if manifest_path.exists():
        if json.loads(manifest_path.read_text()) != plan:
            raise ValueError("Resume refused: frozen plan, code, or candidate pool changed")
    else:
        manifest_path.write_bytes(canonical(plan) + b"\n")
        (output / "pool.json").write_bytes(canonical(pool) + b"\n")
    db = sqlite3.connect(output / "trials.sqlite3", isolation_level=None, timeout=10)
    db.execute("CREATE TABLE IF NOT EXISTS trials (id TEXT PRIMARY KEY, status TEXT NOT NULL)")
    results = []
    try:
        for candidate in pool["candidates"]:
            for slot in plan["slots"]:
                trial_id = digest({"plan": plan["hash"], "candidate": candidate["id"], "slot": slot["id"]})
                scenario = Scenario(**slot["scenario"])
                path = Path("trials") / trial_id
                saved = output / path / "result.json"
                trace = output / path / "trace.jsonl"
                existing = db.execute("SELECT status FROM trials WHERE id=?", (trial_id,)).fetchone()
                if existing:
                    if not saved.exists():
                        raise ValueError("Interrupted trial has no finalized result; reconcile without silent retry")
                    row = json.loads(saved.read_text())
                    if row.get("candidate") != candidate["id"] or row.get("slot") != slot["id"]:
                        raise ValueError("Saved trial identity differs from frozen slot")
                    _validate_result(row, trace, candidate, scenario)
                    if existing[0] != "completed":
                        db.execute("UPDATE trials SET status='completed' WHERE id=?", (trial_id,))
                else:
                    db.execute("INSERT INTO trials VALUES (?, 'reserved')", (trial_id,))
                    row = {"candidate": candidate["id"], "slot": slot["id"],
                           "trace": str(path / "trace.jsonl"),
                           **evaluator(candidate["program"], scenario, trace)}
                    _validate_result(row, trace, candidate, scenario)
                    with saved.open("x") as stream:
                        json.dump(row, stream, indent=2)
                    db.execute("UPDATE trials SET status='completed' WHERE id=?", (trial_id,))
                if row["execution_error"]:
                    raise RuntimeError("Infrastructure failure retained; reconcile before computing selection decisions")
                results.append(row)
    finally:
        db.close()
    by_slot = {slot["id"]: slot for slot in plan["slots"]}
    def outcome(row):
        slot = by_slot[row["slot"]]
        # These are local pure-policy executions: no incremental inference calls.
        # Shared generation subscription cost remains unavailable, not priced here.
        return Outcome(row["candidate"], slot["case"], slot["repeat"], row["verified"],
                       row["completed"] and not row["fresh"], Decimal("0"))
    controls = [outcome(row) for row in results if by_slot[row["slot"]]["phase"] == "regression"]
    decisions = {}
    for method in ("source-only", "generic", "failure-family"):
        selection = [outcome(row) for row in results if by_slot[row["slot"]]["method"] == method]
        decisions[method] = select(pool["parent"], selection, controls)
    summary = {"schema": "agentqa.comparison.v1", "scope": "development-only-not-independent-audit",
               "plan_hash": plan["hash"], "pool_hash": pool["hash"], "trial_count": len(results),
               "decisions": decisions, "results": results,
               "inference_calls": 0, "generation_subscription_cost_usd": None}
    summary_path = output / "summary.json"
    encoded = json.dumps(summary, indent=2) + "\n"
    if summary_path.exists() and json.loads(summary_path.read_text()) != summary:
        raise ValueError("Existing summary conflicts with replayed results")
    if not summary_path.exists():
        summary_path.write_text(encoded)
    return summary
