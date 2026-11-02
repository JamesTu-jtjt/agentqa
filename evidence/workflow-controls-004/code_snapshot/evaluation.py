"""Host-owned evaluation; untrusted policy programs only run in Docker."""

from pathlib import Path

from .agent import run_policy
from .contracts import Scenario, digest
from .environment import TrustedLocalEnvironment
from .families import prepare
from .generated_policy import GeneratedPolicy
from .recorder import replay


def evaluate_program(program: str, scenario: Scenario, trace_path: Path) -> dict:
    with TrustedLocalEnvironment(scenario, trusted_fixture=True) as environment:
        observation = prepare(environment)
        policy = GeneratedPolicy(program)
        error = None
        try:
            verdict = run_policy(environment, observation, policy)
        except RuntimeError as exc:
            error = str(exc)
            verdict = environment.complete(declared=False)
        tip = environment.recorder.save(trace_path)
        assert replay(trace_path, tip) == verdict
        events = environment.recorder.events
        return {"program_hash": digest(program), "scenario_hash": scenario.identity,
                "trace_tip": tip, "error": error,
                "execution_error": any(result["status"] == "infrastructure_error" or result.get("failure_phase") == "startup" or
                                       not result["cleanup_confirmed"] for result in policy.results),
                "visible_runs_including_setup": sum(event["kind"] == "test" and
                    event["payload"]["purpose"] == "visible" for event in events),
                "worker_results": policy.results, **verdict.to_dict()}
