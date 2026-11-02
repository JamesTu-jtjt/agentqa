# Checkpoint 2: integration and development comparison

2 November 2026. Development work and feasibility findings; not a final submission or independent audit.

## Engineering delivered

- Immutable candidate/attempt registry: parent lineage, origin labels, program hashes, failed-attempt retention and frozen pools.
- Matched-suite runner: six selection slots per selector, two shared regression controls, plan/code hashes, persistent trial identities, trace-validated resume and no silent resampling.
- Real ShinkaEvolve external-evaluator bridge: the pinned upstream `JobScheduler` launched AgentQA's evaluator and received correct fitness for identity and compaction cases. Candidate code was never imported into the trusted host process.
- Separate integration environment and dependency lock. Core dependency pins were preserved.
- Separate Docker startup and execution clocks, with a trusted readiness signal before executing candidate code.

The integration scope is pure decision-policy programs. Full multi-module evolution and an end-to-end model-driven coding agent remain outside the implemented scope.

## Matched comparison

The frozen pool contains an authored always-complete parent and both repairs from the first Codex pilot. Each candidate received 18 selection slots and two shared regression cases: **60 trials**, with **zero additional inference calls**.

| Candidate | Source-only | Generic | Failure-family | Shared regression |
| --- | ---: | ---: | ---: | ---: |
| Authored parent | 0/6 | 0/6 | 0/6 | 2/2 |
| repair-00 | 6/6 | 6/6 | 6/6 | 2/2 |
| repair-01 | 6/6 | 6/6 | 6/6 | 2/2 |

All three selectors chose `repair-00`, using the frozen completion/cost/ID ordering. There is **no demonstrated selector advantage**. Repeated deterministic inputs are budget controls, not independent task discoveries or stochastic model repetitions.

All **96 worker invocations** confirmed cleanup. Their total recorded wall time was approximately **197 seconds**, including startup and cleanup. A second runner invocation reused all 60 trials and returned identical decisions without executing candidates again.

The [pool](../evidence/frozen-pool-001/pool.json), [plan](../evidence/development-comparison-001/plan.json), [results](../evidence/development-comparison-001/summary.json), and hashed [source snapshot](../evidence/development-comparison-001/code_snapshot.json) are preserved. This development runner rejects an audit phase.

## Unseeded probe and infrastructure diagnosis

The [predeclared probe](discovery-protocol.md) used one Codex invocation to generate a policy from the interface and intended task requirements. It supplied no buggy policy, previous repair, failed trace or transformation names. This is an **unseeded policy on authored fixtures**, not production-agent behavior.

The original [seven attempted trials](../evidence/unseeded-policy-002/summary.json) contained four verified completions and three worker timeouts. One timeout lacked cleanup confirmation at the immediate check; no workers remained when the engine was subsequently checked. Inspection showed that the policy checked record identity, passing status and current fingerprint. These worker failures did not substantiate a semantic freshness bug.

The old clock included container startup in the execution allowance. The updated worker records Python readiness and separates bounded startup from candidate execution. A single [diagnostic rerun](../evidence/unseeded-worker-recheck-003/summary.json) of the unchanged cached policy completed **7/7** cases. Its manifest links the original outcomes and worker hash. Original attempts remain intact. Workload and timing also changed, so this is diagnostic evidence, not a controlled causal estimate of the fix's effect.

No confirmed semantic failure emerged. Do not count the original infrastructure-inconclusive attempts as agent bugs or replace them in the original denominator.

## Usage and interpretation

Two of the three allowed Codex invocations have been consumed. Together they report **17,978 input tokens** and **796 output tokens**. Subscription dollar cost is unavailable. Local comparison, integration and diagnostic runs made no inference calls.

The fixture exposes relevant fingerprints directly, making a general repair straightforward. That limits its value for evaluating repair selection. The prototype supports the intended comparison, but the scientific contribution remains unestablished.

Next: implement a more realistic stateful coding-agent workflow and obtain evidence of a recurring, repairable semantic failure. Preserve all three selectors and an independent final audit. Do not make a brittle parent merely to favor the method or scale the original 1,572-episode estimate from this non-discriminating pilot.

## Figures and checks

- [Development outcomes](../report/figures/comparison-001/development-comparison.png): identical rankings across selectors.
- [Worker timing](../report/figures/comparison-001/worker-timing.png): startup versus remaining wall time, not model inference latency.

PNG/SVG/PDF versions and a source/input manifest are included. Every scored trace is replayed before plotting.

Final checks: **68 offline tests passed**, with three opt-in Docker tests skipped. The Docker file separately passed **7 tests** (four overlap the offline suite). All **125** recorded trial traces replayed with expected hashes and matching verdicts. The code snapshot matches the frozen comparison hash.
