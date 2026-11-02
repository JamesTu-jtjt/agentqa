"""Bounded offline model interface and explicit authored measurement controls."""

from typing import Protocol

from .environment import TrustedLocalEnvironment
from .contracts import fingerprint


class Policy(Protocol):
    def next_action(self, observation: dict) -> str: ...


class ControlPolicy:
    """Authored controls, never labeled as evolved/model-generated repairs."""

    def __init__(self, name: str):
        if name not in ("trust_old", "narrow_reminder", "always_rerun", "provenance", "refuse"):
            raise ValueError(f"Unknown control policy: {name}")
        self.name = name
        self.did_verify = False

    def next_action(self, observation: dict) -> str:
        if self.name == "refuse":
            return "refuse"
        should_verify = (
            self.name == "always_rerun"
            or (self.name == "narrow_reminder" and any(
                "edited after verification" in line for line in observation["history"]))
            or (self.name == "provenance" and observation["evidence"]["fingerprint"]
                != observation["current_fingerprint"])
        )
        if should_verify and not self.did_verify:
            self.did_verify = True
            return "verify"
        return "complete"


def run_policy(environment: TrustedLocalEnvironment, observation: dict,
               policy: Policy, *, max_actions: int = 4):
    if max_actions < 1:
        raise ValueError("Action limit must be positive")
    for _ in range(max_actions):
        action = policy.next_action(observation)
        if action == "verify":
            result = environment.run_visible()
            observation = {**observation, "last_verification": result["payload"]}
            observation["current_fingerprint"] = fingerprint(environment.root, environment.scenario)
            if result["payload"]["status"] == "passed":
                observation["evidence"] = {"carrier": "transcript", "record_id": result["hash"],
                                           "fingerprint": result["payload"]["after"], "status": "passed"}
        elif action in ("complete", "refuse"):
            return environment.complete(declared=action == "complete")
        else:
            environment.observe(f"Unsupported action: {action!r}")
            return environment.complete(declared=False)
    environment.observe("Action budget exhausted")
    return environment.complete(declared=False)
