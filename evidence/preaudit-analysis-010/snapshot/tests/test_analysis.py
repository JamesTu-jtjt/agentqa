from copy import deepcopy

import pytest

from agentqa.analysis import AnalysisError, analyze_audit
from agentqa.contracts import digest


def fixture(pool_sizes=(1, 9)):
    pools, rows = [], []
    for index, size in enumerate(pool_sizes):
        pool_id = f"pool-{index}"
        candidates = {name: digest({"pool": pool_id, "candidate": name}) for name in ("parent", "repair")}
        slots = [{"slot_id": f"c{n}", "case_id": f"case-{n}", "repeat": 0} for n in range(size)]
        pools.append({"pool_id": pool_id, "pool_hash": digest(pool_id), "candidates": candidates,
            "parent": "parent", "decisions": {"source-only": "parent", "generic": "parent", "failure-family": "repair"},
            "audit_slots": slots})
        for candidate, candidate_hash in candidates.items():
            for slot in slots:
                passed = candidate == "repair" and index == 0
                rows.append({"pool_id": pool_id, "candidate": candidate, "candidate_hash": candidate_hash,
                    "slot_id": slot["slot_id"], "completed": True, "functional": passed, "fresh": passed,
                    "verified": passed, "refusal": False, "infrastructure_error": False, "api_cost_usd": None})
    plan = {"schema": "agentqa.audit-analysis-plan.v1", "status": "selection_frozen", "pools": pools,
            "scope": "Synthetic unit-test data only"}
    return {**plan, "plan_hash": digest(plan)}, rows


def refreeze(plan):
    plan["plan_hash"] = digest({key: value for key, value in plan.items() if key != "plan_hash"})


def test_source_pools_not_trial_counts_define_paired_unit():
    plan, rows = fixture()
    result = analyze_audit(plan, rows)
    assert result["audit_trial_count"] == 20
    assert result["selector_macro"]["failure-family"]["verified"] == .5
    assert result["family_minus_baseline"]["source-only"]["difference"] == .5
    assert result["family_minus_baseline"]["source-only"]["interval"] is None
    assert not result["cost_all_audited_candidates"]["complete"]
    assert result["cost_all_audited_candidates"]["unknown_cost_trials"] == 20


def test_repeats_are_averaged_within_cases_before_pool_mean():
    plan, rows = fixture((2,))
    for repeat in range(1, 5):
        slot = {"slot_id": f"repeat-{repeat}", "case_id": "case-0", "repeat": repeat}
        plan["pools"][0]["audit_slots"].append(slot)
        for candidate in ("parent", "repair"):
            row = deepcopy(next(row for row in rows if row["candidate"] == candidate and row["slot_id"] == "c0"))
            row["slot_id"] = slot["slot_id"]
            rows.append(row)
    second = next(row for row in rows if row["candidate"] == "repair" and row["slot_id"] == "c1")
    second.update(verified=False, functional=False, fresh=False)
    refreeze(plan)
    result = analyze_audit(plan, rows)
    assert result["selector_macro"]["failure-family"]["verified"] == .5


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "candidate_hash", "infrastructure", "contradictory"])
def test_incomplete_or_untrustworthy_outcomes_cannot_produce_primary_effect(mutation):
    plan, rows = fixture()
    if mutation == "missing": rows.pop()
    elif mutation == "duplicate": rows.append(rows[0])
    elif mutation == "candidate_hash": rows[0]["candidate_hash"] = "0" * 64
    elif mutation == "infrastructure": rows[0]["infrastructure_error"] = True
    else: rows[0]["verified"] = True
    with pytest.raises(AnalysisError):
        analyze_audit(plan, rows)


def test_audit_does_not_choose_winners_or_accept_unfrozen_selection():
    plan, rows = fixture()
    plan["status"] = "draft"
    refreeze(plan)
    with pytest.raises(AnalysisError, match="frozen"):
        analyze_audit(plan, rows)
    plan["status"] = "selection_frozen"
    plan["pools"][0]["decisions"]["generic"] = "unseen"
    refreeze(plan)
    with pytest.raises(AnalysisError, match="out-of-pool"):
        analyze_audit(plan, rows)


def test_costs_are_separate_from_success_and_unknown_is_not_zero():
    plan, rows = fixture((1,))
    rows[0]["api_cost_usd"] = "0.25"
    result = analyze_audit(plan, rows)
    assert result["cost_all_audited_candidates"]["known_api_cost_usd"] == "0.25"
    assert result["cost_all_audited_candidates"]["unknown_cost_trials"] == 1
    rows[0]["api_cost_usd"] = "NaN"
    with pytest.raises(AnalysisError):
        analyze_audit(plan, rows)


def test_intervals_resample_pools_and_are_reproducible():
    plan, rows = fixture((1,)*5)
    first = analyze_audit(plan, rows, bootstrap_samples=200)
    second = analyze_audit(plan, list(reversed(rows)), bootstrap_samples=200)
    assert first["family_minus_baseline"] == second["family_minus_baseline"]
    assert first["family_minus_baseline"]["generic"]["interval"] is not None


def test_refusals_are_not_inferred_from_incomplete_episodes():
    plan, rows = fixture((1,))
    rows[1].update(completed=False, verified=False, functional=False, fresh=False, refusal=True)
    result = analyze_audit(plan, rows)
    assert result["selector_macro"]["failure-family"]["verified"] == 0
    assert result["selector_macro"]["failure-family"]["refusal"] == 1
