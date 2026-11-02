"""Bounded authored transformations; this module does not infer arbitrary MRs."""

from dataclasses import asdict, dataclass, replace

from .contracts import Scenario, fingerprint
from .environment import TrustedLocalEnvironment, module_source


@dataclass(frozen=True)
class FamilyCase:
    source_hash: str
    transformation: str
    relation: str
    scenario: Scenario

    def to_dict(self):
        return asdict(self)


def transform(source: Scenario, operator: str) -> FamilyCase:
    changes = {
        "identity": {},
        "rename": {"module": "src/value.py", "function": "bound_value",
                   "visible_test": "checks/verify.py", "config": "settings/limits.json"},
        "noise": {"noise": 8},
        "compaction": {"compact": True},
        "handoff": {"carrier": "handoff", "compact": True},
        "cache": {"carrier": "cache"},
        "unchanged": {"invalidate": False},
    }
    if operator not in changes:
        raise ValueError(f"Unknown transformation: {operator}")
    if not source.invalidate:
        raise ValueError("Families require a source with an invalidating edit")
    target = replace(source, scenario_id=f"{source.scenario_id}:{operator}", **changes[operator])
    return FamilyCase(source.identity, operator,
                      "contrastive" if operator == "unchanged" else "preserve-obligation", target)


def generate(source: Scenario, *, generic: bool = False) -> list[FamilyCase]:
    operators = ("identity", "rename", "noise") if generic else (
        "identity", "rename", "noise", "compaction", "handoff", "cache", "unchanged")
    return [transform(source, name) for name in operators]


def prepare(environment: TrustedLocalEnvironment) -> dict:
    """Create a real old passing record and a supported agent-visible state."""
    scenario = environment.scenario
    old = environment.run_visible()
    if old["payload"]["status"] != "passed":
        raise ValueError("Source verification did not execute successfully")
    if scenario.invalidate:
        environment.write(scenario.module, module_source(scenario, correct=True))
    history = ["Required verification completed successfully."]
    if scenario.invalidate:
        history.append("Relevant code was edited after verification.")
    history += [f"Unrelated observation {i}." for i in range(scenario.noise)]
    if scenario.compact:
        history = ["Compacted task history; consult available evidence provenance."]
    observation = {
        "history": history,
        "evidence": {"carrier": scenario.carrier, "record_id": old["hash"],
                     "fingerprint": old["payload"]["after"], "status": "passed"},
        "current_fingerprint": fingerprint(environment.root, scenario),
        "verification_entrypoint": scenario.visible_test,
    }
    environment.observe(str(observation))
    return observation


def validate_case(source: Scenario, case: FamilyCase) -> dict:
    if case.source_hash != source.identity:
        raise ValueError("Family refers to a different source")
    expected = transform(source, case.transformation)
    if case != expected:
        raise ValueError("Case is not an instance of its declared transformation")
    with TrustedLocalEnvironment(case.scenario, trusted_fixture=True) as environment:
        observation = prepare(environment)
        old_current = (observation["evidence"]["fingerprint"] ==
                       observation["current_fingerprint"])
        if old_current == case.scenario.invalidate:
            raise ValueError("Invalidation relation does not match executed state")
        environment.run_visible()
        verdict = environment.complete()
        if not verdict.verified:
            raise ValueError(f"Reference cannot complete transformed fixture: {verdict.reason}")
        return {"valid": True, "source_hash": source.identity,
                "target_hash": case.scenario.identity, "transformation": case.transformation,
                "prior_evidence_current": old_current, "reference_verdict": verdict.to_dict()}
