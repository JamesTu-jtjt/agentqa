"""A shared selection rule; suites, not candidate generators, differ by method."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Outcome:
    candidate: str
    case: str
    repeat: int
    verified: bool
    violation: bool
    cost_usd: Decimal = Decimal("0")

    def __post_init__(self):
        if (not self.cost_usd.is_finite() or self.cost_usd < 0 or self.repeat < 0
                or type(self.verified) is not bool or type(self.violation) is not bool):
            raise ValueError("Invalid trial outcome")


def _indexed(outcomes: list[Outcome]) -> dict[str, dict[tuple[str, int], Outcome]]:
    result: dict[str, dict[tuple[str, int], Outcome]] = {}
    for outcome in outcomes:
        rows = result.setdefault(outcome.candidate, {})
        key = (outcome.case, outcome.repeat)
        if key in rows:
            raise ValueError("Duplicate trial slot")
        rows[key] = outcome
    return result


def select(parent: str, selection: list[Outcome], regression: list[Outcome]) -> dict:
    scores = _indexed(selection)
    controls = _indexed(regression)
    if not scores or set(scores) != set(controls) or parent not in scores:
        raise ValueError("Selection/regression candidate pools must match and include parent")
    slots = set(scores[parent])
    regression_slots = set(controls[parent])
    if not slots or not regression_slots:
        raise ValueError("Both suites require observations")
    for candidate in scores:
        if set(scores[candidate]) != slots or set(controls[candidate]) != regression_slots:
            raise ValueError("Unmatched trial slots; incomplete results cannot be selected")
    eligible = []
    excluded = []
    cases = {case for case, _ in regression_slots}
    for candidate in sorted(scores):
        qualifies = True
        for case in cases:
            before = [row for (name, _), row in controls[parent].items() if name == case]
            after = [row for (name, _), row in controls[candidate].items() if name == case]
            if (sum(row.verified for row in after) < sum(row.verified for row in before)
                    or sum(row.violation for row in after) > sum(row.violation for row in before)):
                qualifies = False
        (eligible if qualifies else excluded).append(candidate)
    ordered = sorted(eligible, key=lambda candidate: (
        -sum(row.verified for row in scores[candidate].values()),
        sum((row.cost_usd for row in scores[candidate].values()), Decimal("0")), candidate))
    return {"selected": ordered[0], "eligible": ordered, "excluded": excluded,
            "rule": "verified-completion/cost/id.v1",
            "slot_count": len(slots), "regression_slot_count": len(regression_slots)}
