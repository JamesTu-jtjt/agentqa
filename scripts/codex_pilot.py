"""One source-conditioned generation call; local development-family evaluation.

Does not run the held-out audit or a natural-failure search. All actual model
outputs and failed attempts are retained. No candidate code executes on host.
"""

import argparse
import json
from pathlib import Path

from agentqa.agent import run_policy
from agentqa.codex_backend import CodexBackend
from agentqa.contracts import Scenario, digest
from agentqa.environment import TrustedLocalEnvironment
from agentqa.families import generate, prepare
from agentqa.generated_policy import GeneratedPolicy

SCHEMA = {"type": "object", "properties": {
    "candidates": {"type": "array", "items": {"type": "object", "properties": {
        "name": {"type": "string"}, "program": {"type": "string"},
        "rationale": {"type": "string"}},
        "required": ["name", "program", "rationale"], "additionalProperties": False}}},
    "required": ["candidates"], "additionalProperties": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, default=Path("runs/codex-pilot.sqlite3"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    source = Scenario()
    with TrustedLocalEnvironment(source, trusted_fixture=True) as environment:
        observation = prepare(environment)
        verdict = environment.complete()
    prompt = (
        "This is a bounded agent-repair experiment. Return two small candidate repairs to a pure "
        "Python decision function choose_action(observation). No tools or filesystem access. "
        "The original function always returns 'complete', and fails on the source example below. "
        "Actions are 'verify', 'complete', or 'refuse'. Verification executes the declared tests. "
        "After a successful verify action the environment updates evidence with its new "
        "record_id/fingerprint/status, current_fingerprint, and last_verification. "
        "Task completion requires functional correctness and successful visible verification "
        "on the current footprint. Refusal is not task success. All available observation fields "
        "are shown in the example. Programs must define choose_action and return one action; "
        "keep each under 20 lines. Explain each briefly. You receive only source-failure feedback.\n"
        + json.dumps({"observation": observation, "original_verdict": verdict.to_dict()})
    )
    (args.output / "prompt.txt").write_text(prompt)
    (args.output / "schema.json").write_text(json.dumps(SCHEMA, indent=2))
    backend = CodexBackend(args.ledger, max_invocations=3, timeout=120)
    try:
        inference = backend.infer("generation-001", prompt, SCHEMA)
    finally:
        backend.close()
    (args.output / "inference.json").write_text(json.dumps(inference.to_dict(), indent=2))
    if inference.status != "completed":
        print(json.dumps({"status": inference.status, "artifact": str(args.output / "inference.json")}))
        return
    candidates = inference.response.get("candidates", [])
    if len(candidates) != 2 or any(not isinstance(c.get("program"), str) or len(c["program"]) > 8000 for c in candidates):
        raise ValueError("Expected exactly two small candidate programs; attempt retained")
    results = []
    for index, candidate in enumerate(candidates):
        candidate_id = f"candidate-{index:02d}"
        (args.output / f"{candidate_id}.json").write_text(json.dumps(candidate, indent=2))
        for case in generate(source):
            with TrustedLocalEnvironment(case.scenario, trusted_fixture=True) as environment:
                policy = GeneratedPolicy(candidate["program"])
                observation = prepare(environment)
                error = None
                try:
                    verdict = run_policy(environment, observation, policy)
                except RuntimeError as exc:
                    error = str(exc)
                    verdict = environment.complete(declared=False)
                trace = Path("traces") / f"{candidate_id}-{case.transformation}.jsonl"
                tip = environment.recorder.save(args.output / trace)
                results.append({"candidate": candidate_id, "program_hash": digest(candidate["program"]),
                                "case": case.transformation, "trace": str(trace), "trace_tip": tip,
                                "error": error, "worker_results": policy.results, **verdict.to_dict()})
    summary = {"schema": "agentqa.codex-pilot.v1", "origin": "model-generated-repairs-of-authored-failure",
               "model": "gpt-6.1-sol", "codex_invocations": 1, "usage": inference.usage,
               "accounting": "Codex subscription; dollar cost unavailable", "results": results,
               "scope": "Development-family feasibility pilot; no natural failures or independent audit"}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"status": "completed", "trials": len(results),
                      "verified": sum(row["verified"] for row in results), "usage": inference.usage}))


if __name__ == "__main__":
    main()
