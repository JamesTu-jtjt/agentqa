"""Protocol tests use addition fixtures, never the new audit task templates."""

from copy import deepcopy
import json
from pathlib import Path

import pytest

from agentqa.agent import ControlPolicy, run_policy
from agentqa.contracts import canonical, digest
from agentqa import controlled_audit as audit

ROOT = Path(__file__).resolve().parents[1]


def fixture_template(name="unit-addition"):
    return {"id": name, "description": "Authored addition unit fixture",
            "prior": "def solve(value, config):\n    return value\n",
            "correct": "def solve(value, config):\n    return value + config['offset']\n",
            "config": {"offset": 0}, "changed_config": {"offset": 3},
            "visible": "assert solve(0, config) == config['offset']",
            "functional": "assert solve(5, config) == 5 + config['offset']"}


@pytest.fixture
def frozen(tmp_path, monkeypatch):
    pool = json.loads((ROOT / "evidence/frozen-pool-001/pool.json").read_text())
    receipt = {"directory": "test-only", "plan_hash": "a" * 64, "summary_sha256": "b" * 64,
               "pool_hash": pool["hash"], "decisions": {method: "repair-00" for method in audit.METHODS}}
    monkeypatch.setattr(audit, "selection_receipt", lambda root: (pool, receipt))
    root = tmp_path / "root"
    for name in ("src/agentqa/controlled_audit.py", "configs/controlled-audit.json",
                 "scripts/run_controlled_audit.py", "docs/controlled-audit-protocol.md",
                 "requirements-dev.lock", "pyproject.toml"):
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text("unit protocol snapshot\n")
    (root / "configs/controlled-audit.json").write_text(json.dumps({
        "templates": [fixture_template(f"unit-addition-{i}") for i in range(3)]}))
    output = tmp_path / "audit"
    plan = audit.freeze_audit(root, output)
    return root, output, plan


def trusted_evaluator(program, case, template, trace):
    # Only fixed authored policies execute locally, never the supplied program.
    with audit.AuditEnvironment(case, template, trusted_fixture=True) as env:
        verdict = run_policy(env, env.prepare(), ControlPolicy("provenance"))
        tip = env.recorder.save(trace)
        return {**verdict.to_dict(), "refusal": False, "infrastructure_error": False,
                "actions": ["verify", "complete"], "error": None, "trace_tip": tip,
                "program_hash": digest(program), "case_hash": digest(case), "worker_results": []}


def test_actual_development_selection_is_replayed_and_matches_frozen_pool():
    pool, receipt = audit.selection_receipt(ROOT)
    assert pool["hash"] == receipt["pool_hash"]
    assert set(receipt["decisions"].values()) == {"repair-00"}


def test_freeze_has_no_outcomes_and_rejects_changed_snapshot_or_identity(frozen):
    root, output, plan = frozen
    assert not (output / "trials").exists()
    assert plan["trial_allowance"] == 36 and plan["inference_calls"] == 0
    with pytest.raises(ValueError, match="external freeze"):
        audit.validate_frozen(root, output, "0" * 64)
    (output / "snapshot/pyproject.toml").write_text("modified")
    with pytest.raises(ValueError, match="snapshot"):
        audit.validate_frozen(root, output, plan["plan_hash"])


def test_changed_live_code_stops_execution_but_preserved_snapshot_still_verifies(frozen):
    root, output, plan = frozen
    (root / "pyproject.toml").write_text("modified")
    audit.validate_frozen(root, output, plan["plan_hash"])
    with pytest.raises(ValueError, match="Execution code"):
        audit.validate_frozen(root, output, plan["plan_hash"], execution=True)


def test_complete_grid_resume_reuses_results_and_tampering_stops_analysis(frozen):
    root, output, plan = frozen
    calls = []
    def evaluate(*args):
        calls.append(1)
        return trusted_evaluator(*args)
    summary, analysis = audit.finish_audit(root, output, plan["plan_hash"], execute=True, evaluator=evaluate)
    assert len(calls) == summary["trial_count"] == analysis["audit_trial_count"] == 36
    def forbidden(*args):
        raise AssertionError("Resume must not rerun candidates")
    assert audit.finish_audit(root, output, plan["plan_hash"], execute=True, evaluator=forbidden) == (summary, analysis)
    file = next((output / "trials").glob("*/result.json"))
    row = json.loads(file.read_text())
    row["fresh"] = not row["fresh"]
    file.write_bytes(canonical(row))
    with pytest.raises(ValueError, match="trace replay"):
        audit.finish_audit(root, output, plan["plan_hash"])


def test_missing_or_interrupted_slots_never_silently_execute(frozen):
    root, output, plan = frozen
    with pytest.raises(ValueError, match="Incomplete audit"):
        audit.finish_audit(root, output, plan["plan_hash"])
    calls = []
    def interrupted(*args):
        calls.append(1)
        raise OSError("injected loss before result publication")
    with pytest.raises(OSError):
        audit.finish_audit(root, output, plan["plan_hash"], execute=True, evaluator=interrupted)
    with pytest.raises(ValueError, match="Interrupted trial"):
        audit.finish_audit(root, output, plan["plan_hash"], execute=True, evaluator=interrupted)
    assert len(calls) == 1


def test_infrastructure_outcome_is_retained_and_prevents_primary_result(frozen):
    root, output, plan = frozen
    def infrastructure(*args):
        return {**trusted_evaluator(*args), "infrastructure_error": True}
    with pytest.raises(ValueError, match="Unreconciled infrastructure"):
        audit.finish_audit(root, output, plan["plan_hash"], execute=True, evaluator=infrastructure)
    assert len(list((output / "trials").glob("*/result.json"))) == 36
    assert not (output / "analysis.json").exists()


def test_authored_unit_fixture_rejects_stale_completion_and_keeps_irrelevant_receipt():
    template = fixture_template()
    for variant in ("config-change", "unrelated-docs"):
        case = {"id": f"unit:{variant}", "template_id": template["id"], "variant": variant}
        with audit.AuditEnvironment(case, template, trusted_fixture=True) as env:
            env.prepare()
            verdict = env.complete()
            assert verdict.functional
            assert verdict.verified == (variant == "unrelated-docs")
    with pytest.raises(ValueError, match="trusted authored"):
        audit.AuditEnvironment(case, template)
