"""Pre-audit analysis of normalized, externally verified coding outcomes.

The sampling unit is a frozen source pool. Repeats are averaged within cases,
then cases within pools, then pools equally. This module does not open audit
fixtures or authenticate traces; an eventual audit runner must verify those.
"""

from collections import defaultdict
from decimal import Decimal, InvalidOperation
import random
import re
from statistics import mean

from .contracts import digest

METHODS = ("source-only", "generic", "failure-family")
METRICS = ("verified", "completed", "functional", "fresh", "refusal", "stale_completion")


class AnalysisError(ValueError):
    pass


def _identity(value):
    return isinstance(value, str) and re.fullmatch("[a-f0-9]{64}", value)


def validate_plan(envelope):
    plan = {key: value for key, value in envelope.items() if key != "plan_hash"}
    if digest(plan) != envelope.get("plan_hash") or plan.get("schema") != "agentqa.audit-analysis-plan.v1":
        raise AnalysisError("Invalid frozen analysis plan")
    if plan.get("status") != "selection_frozen":
        raise AnalysisError("Selection decisions must be frozen before audit analysis")
    pools = {}
    for pool in plan.get("pools", []):
        name = pool["pool_id"]
        candidates = pool["candidates"]
        references = pool.get("references", {})
        if (name in pools or not name or not candidates or pool["parent"] not in candidates
                or set(candidates) & set(references) or not _identity(pool.get("pool_hash"))
                or not all(_identity(value) for value in [*candidates.values(), *references.values()])):
            raise AnalysisError("Invalid pool/candidate identities")
        decisions = pool["decisions"]
        if set(decisions) != set(METHODS) or any(selected not in candidates for selected in decisions.values()):
            raise AnalysisError("Unfrozen or out-of-pool selector decision")
        coordinates, slots = set(), set()
        for slot in pool["audit_slots"]:
            coordinate = (slot["case_id"], slot["repeat"])
            if (not slot["slot_id"] or not slot["case_id"] or type(slot["repeat"]) is not int
                    or slot["repeat"] < 0 or coordinate in coordinates or slot["slot_id"] in slots):
                raise AnalysisError("Invalid/duplicate audit slot")
            coordinates.add(coordinate)
            slots.add(slot["slot_id"])
        if not slots:
            raise AnalysisError("Empty audit suite")
        pools[name] = pool
    if not pools:
        raise AnalysisError("No source pools")
    return plan, pools


def _cost_summary(rows):
    known, unknown = Decimal("0"), 0
    for row in rows:
        value = row.get("api_cost_usd")
        if value is None:
            unknown += 1
        else:
            try:
                amount = Decimal(str(value))
                if not amount.is_finite() or amount < 0:
                    raise InvalidOperation
                known += amount
            except InvalidOperation as exc:
                raise AnalysisError("Invalid API cost") from exc
    return {"known_api_cost_usd": str(known), "unknown_cost_trials": unknown,
            "complete": unknown == 0, "includes_generation": False}


def _score(rows, slots):
    by_case = defaultdict(list)
    for row in rows:
        data = {key: row[key] for key in METRICS if key != "stale_completion"}
        data["stale_completion"] = row["completed"] and not row["fresh"]
        by_case[slots[row["slot_id"]]["case_id"]].append(data)
    metrics = {key: mean(mean(item[key] for item in values) for values in by_case.values()) for key in METRICS}
    return {"metrics": metrics, "trials": len(rows), "cases": len(by_case),
            "raw_counts": {key: sum((row["completed"] and not row["fresh"]) if key == "stale_completion"
                else row[key] for row in rows) for key in METRICS}, "cost": _cost_summary(rows)}


def _paired_interval(deltas, *, samples, seed):
    # A minimum of five pools is a conservative reporting rule, not a power claim.
    if len(deltas) < 5:
        return {"interval": None, "reason": "fewer_than_five_source_pools"}
    rng = random.Random(seed)
    draws = sorted(mean(rng.choices(deltas, k=len(deltas))) for _ in range(samples))
    return {"interval": [draws[int(.025 * (samples - 1))], draws[int(.975 * (samples - 1))]],
            "method": "percentile bootstrap of paired source-pool differences", "samples": samples,
            "seed": seed, "caution": "Descriptive interval; no significance claim or population representativeness implied."}


def analyze_audit(envelope, outcomes, *, bootstrap_samples=10000, seed=17):
    if type(bootstrap_samples) is not int or not 100 <= bootstrap_samples <= 100000:
        raise AnalysisError("Bootstrap count outside declared bounds")
    plan, pools = validate_plan(envelope)
    indexed = {}
    for row in outcomes:
        try:
            pool = pools[row["pool_id"]]
            candidates = {**pool["candidates"], **pool.get("references", {})}
            slots = {slot["slot_id"]: slot for slot in pool["audit_slots"]}
            coordinate = (row["pool_id"], row["candidate"], row["slot_id"])
            if (coordinate in indexed or row["slot_id"] not in slots
                    or row["candidate_hash"] != candidates[row["candidate"]]):
                raise AnalysisError("Duplicate/unplanned audit outcome or candidate mismatch")
            if any(type(row[key]) is not bool for key in (*METRICS[:-1], "infrastructure_error")):
                raise AnalysisError("Outcome flags must be boolean")
            if row["verified"] != (row["completed"] and row["functional"] and row["fresh"]):
                raise AnalysisError("Verified completion inconsistent with its components")
            if row["refusal"] and row["completed"]:
                raise AnalysisError("Refusal cannot be completed")
            indexed[coordinate] = row
        except (KeyError, TypeError) as exc:
            raise AnalysisError("Unknown or malformed audit coordinate") from exc
    expected = {(name, candidate, slot["slot_id"]) for name, pool in pools.items()
                for candidate in {**pool["candidates"], **pool.get("references", {})}
                for slot in pool["audit_slots"]}
    if set(indexed) != expected:
        raise AnalysisError("Incomplete audit grid; no silent exclusions or missing candidates")
    if any(row["infrastructure_error"] for row in indexed.values()):
        raise AnalysisError("Unreconciled infrastructure outcome; primary comparison withheld")
    by_pool = {}
    for name, pool in pools.items():
        slots = {slot["slot_id"]: slot for slot in pool["audit_slots"]}
        scores = {candidate: _score([indexed[(name, candidate, slot)] for slot in slots], slots)
                  for candidate in {**pool["candidates"], **pool.get("references", {})}}
        by_pool[name] = {"candidates": scores, "parent": pool["parent"], "decisions": pool["decisions"],
            "oracle_best_verified": max(scores[candidate]["metrics"]["verified"] for candidate in pool["candidates"]),
            "oracle_label": "Post-hoc candidate-pool ceiling; not an executable selector"}
    macro = {method: {metric: mean(pool["candidates"][pool["decisions"][method]]["metrics"][metric]
             for pool in by_pool.values()) for metric in METRICS} for method in METHODS}
    paired = {}
    for baseline in ("source-only", "generic"):
        deltas = {name: data["candidates"][data["decisions"]["failure-family"]]["metrics"]["verified"]
                  - data["candidates"][data["decisions"][baseline]]["metrics"]["verified"]
                  for name, data in by_pool.items()}
        paired[baseline] = {"difference": mean(deltas.values()), "by_source_pool": deltas,
            "source_pool_count": len(deltas),
            **_paired_interval(list(deltas.values()), samples=bootstrap_samples, seed=seed)}
    return {"schema": "agentqa.audit-analysis.v1", "plan_hash": envelope["plan_hash"],
            "status": "complete", "source_pool_count": len(pools), "audit_trial_count": len(indexed),
            "weighting": "repeat-within-case, cases-within-pool, equal-source-pool",
            "by_pool": by_pool, "selector_macro": macro, "family_minus_baseline": paired,
            "cost_all_audited_candidates": _cost_summary(list(indexed.values())),
            "scope": plan.get("scope", "Unspecified; no natural/model-origin claim inferred")}
