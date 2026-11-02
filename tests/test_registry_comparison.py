import json
import sqlite3

import pytest

from agentqa.agent import ControlPolicy, run_policy
from agentqa.comparison import development_slots, freeze_plan, run_comparison
from agentqa.contracts import Scenario
from agentqa.environment import TrustedLocalEnvironment
from agentqa.families import prepare
from agentqa.registry import CandidateRegistry, RegistryError, validate_pool


def make_pool(path):
    registry = CandidateRegistry(path)
    source = Scenario().identity
    registry.add("parent", "trust_old", parent=None, source_hash=source,
                 origin="authored-control", provenance={})
    registry.add("child", "provenance", parent="parent", source_hash=source,
                 origin="authored-control", provenance={})
    return registry, registry.freeze("pool", ["parent", "child"], parent="parent")


def test_registry_preserves_lineage_failed_attempts_and_freezes(tmp_path):
    registry = CandidateRegistry(tmp_path / "registry.db")
    source = Scenario().identity
    registry.add("parent", "def f(): pass", parent=None, source_hash=source,
                 origin="authored-control", provenance={})
    registry.begin_attempt("failed", parent="parent", source_hash=source, details={"call": 1})
    with pytest.raises(RegistryError):
        registry.freeze("premature", ["parent"], parent="parent")
    registry.finish_attempt("failed", "failed", {"reason": "invalid code"})
    manifest = registry.freeze("final", ["parent"], parent="parent")
    assert manifest["attempts"][0]["status"] == "failed"
    validate_pool(manifest)
    with pytest.raises(RegistryError):
        registry.finish_attempt("failed", "completed", {})
    with pytest.raises(sqlite3.IntegrityError):
        registry.db.execute("UPDATE candidates SET program='changed' WHERE id='parent'")
    with pytest.raises(RegistryError):
        registry.freeze("final", ["parent"], parent="parent")
    registry.close()


def test_missing_parent_duplicate_and_manifest_tampering_are_rejected(tmp_path):
    registry, pool = make_pool(tmp_path / "registry.db")
    with pytest.raises(RegistryError):
        registry.add("missing", "p", parent="unknown", source_hash=Scenario().identity,
                     origin="authored-control", provenance={})
    with pytest.raises(RegistryError):
        registry.freeze("duplicate", ["parent", "parent"], parent="parent")
    pool["candidates"][0]["program"] = "changed"
    with pytest.raises(RegistryError):
        validate_pool(pool)
    registry.close()


def test_plan_requires_matched_methods_and_does_not_accept_audit_data(tmp_path):
    registry, pool = make_pool(tmp_path / "registry.db")
    slots = development_slots()
    assert len(slots) == 20
    assert {method: sum(slot["method"] == method for slot in slots)
            for method in ("source-only", "generic", "failure-family")} == {
                "source-only": 6, "generic": 6, "failure-family": 6}
    with pytest.raises(ValueError):
        freeze_plan(pool, slots[:-3])
    slots[0] = {**slots[0], "phase": "audit"}
    with pytest.raises(ValueError):
        freeze_plan(pool, slots)
    registry.close()


def trusted_test_evaluator(program, scenario, trace):
    # Authored controls avoid Docker in the scheduler unit test. Real code uses evaluate_program.
    with TrustedLocalEnvironment(scenario, trusted_fixture=True) as environment:
        verdict = run_policy(environment, prepare(environment), ControlPolicy(program))
        tip = environment.recorder.save(trace)
        from agentqa.contracts import digest
        return {"program_hash": digest(program), "scenario_hash": scenario.identity,
                "trace_tip": tip, "error": None, "execution_error": False, **verdict.to_dict()}


def test_resume_reuses_every_completed_trial_and_selects_from_same_pool(tmp_path):
    registry, pool = make_pool(tmp_path / "registry.db")
    calls = []
    def evaluator(program, scenario, trace):
        calls.append(program)
        return trusted_test_evaluator(program, scenario, trace)
    output = tmp_path / "comparison"
    result = run_comparison(pool, output, evaluator=evaluator)
    assert len(calls) == 40
    assert result["trial_count"] == 40
    assert all(decision["selected"] == "child" for decision in result["decisions"].values())
    assert run_comparison(pool, output, evaluator=evaluator) == result
    assert len(calls) == 40
    files = sorted((output / "trials").glob("*/result.json"))
    saved = json.loads(files[0].read_text())
    saved["candidate"] = "wrong"
    files[0].write_text(json.dumps(saved))
    with pytest.raises(ValueError):
        run_comparison(pool, output, evaluator=evaluator)
    registry.close()


def test_interrupted_trial_is_not_silently_resampled(tmp_path):
    registry, pool = make_pool(tmp_path / "registry.db")
    calls = []
    def fail(program, scenario, trace):
        calls.append(program)
        raise OSError("injected interruption before result")
    output = tmp_path / "comparison"
    with pytest.raises(OSError):
        run_comparison(pool, output, evaluator=fail)
    with pytest.raises(ValueError):
        run_comparison(pool, output, evaluator=fail)
    assert len(calls) == 1
    registry.close()
