"""Actual local execution of authored controls, not a live research experiment."""

import json
from pathlib import Path

from .agent import ControlPolicy, run_policy
from .contracts import Scenario
from .environment import TrustedLocalEnvironment
from .families import generate, prepare, validate_case


def run_demo(output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=False)
    source = Scenario()
    results = []
    validation = []
    policies = ("trust_old", "narrow_reminder", "always_rerun", "provenance", "refuse")
    cases = generate(source)
    for case in cases:
        validation.append(validate_case(source, case))
        for policy in policies:
            with TrustedLocalEnvironment(case.scenario, trusted_fixture=True) as environment:
                observation = prepare(environment)
                verdict = run_policy(environment, observation, ControlPolicy(policy))
                trace = Path("traces") / f"{case.transformation}--{policy}.jsonl"
                tip = environment.recorder.save(output / trace)
                events = environment.recorder.events
                visible_runs = sum(e["kind"] == "test" and e["payload"]["purpose"] == "visible"
                                   for e in events)
                results.append({"case": case.transformation, "policy": policy,
                                "scenario_hash": case.scenario.identity,
                                "trace": str(trace), "trace_tip": tip,
                                "visible_runs_including_setup": visible_runs,
                                **verdict.to_dict()})
    summary = {"schema": "agentqa.demo.v1", "origin": "authored-controls",
               "claim": "Local measurement demonstration, not evidence of model repair generalization",
               "model_calls": 0, "api_cost_usd": 0,
               "source": source.scenario_id, "validation": validation, "results": results}
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
