# 50% checkpoint

2 November 2026. Overall progress is **approximately 50%**, assessed by remaining deliverable effort, not by test count, number of TODO boxes, or evidence that the hypothesis is true. James requested work through this checkpoint; implementation stops here pending his next instruction. This is not a final research result or submission package.

## What earns the checkpoint

| Deliverable area | Approximate project share | Checkpoint evidence |
| --- | ---: | --- |
| Research specification, measurement, families, isolation, accounting, registry and evolution/evaluation adapters | 40% complete | M0–M4 acceptance checks, methods notes, executable oracle, seven family cases, real pinned Shinka scheduler check, resumable matched comparison, and the new stateful workflow. |
| Bounded pilot and feasibility assessment | 10% complete | Three model calls preserved; policy comparison and unseeded probes analyzed; no discriminating generated pool found. |
| Realistic semantic-failure sources and useful candidate pools | 15% remaining | Small deterministic tasks are insufficient evidence about native coding/scientific agents. Natural failure discovery and diagnosis remain open. |
| Final freeze and matched main selection | 10% remaining | No final source pools, analysis freeze or main run yet. |
| Independent audit and research analysis | 15% remaining | Audit unopened; no selector advantage or generalization result established. |
| Final report, demonstration and clean reproduction package | 10% remaining | Intermediate figures and traces exist; final narrative/package not delivered. |

This is an engineering/research effort estimate. Feasibility can change remaining effort substantially. The eight-day timeline is still a relative plan, not elapsed-time evidence.

## New work at this checkpoint

`src/agentqa/workflow.py` adds a bounded, replaceable controller with read/write/status/verify/handoff/completion actions, carried JSON memory, actual task edits and resettable state. Generated controller code and edited task code execute in separate resource-bounded Docker containers. Only accepted module-write actions change the persistent virtual workspace. Tests, configuration, recorder and expected-answer oracle remain outside the editable boundary.

The model generates a controller program once; that program makes subsequent tool decisions. Its actual patch is executed and evaluated. This is a stronger lifecycle test than the previous post-authored-edit policies, while still a limited proxy for a live model reasoning at every step. The workload is a single-module development task, not a full native Sakana agent. The existing Shinka integration continues to evaluate the earlier pure-policy interface; the full Shinka evolution loop has not run.

The predeclared [workflow protocol](workflow-protocol.md), saved prompts, case grid and source snapshots distinguish decisions made before generation from later interpretation.

| Controller | Baseline | Config change | Source change | Unrelated docs | Handoff | Compaction |
| --- | --- | --- | --- | --- | --- | --- |
| Authored reference | Verified | Verified | Verified | Verified | Verified | Verified |
| Authored stale control | Verified | Stale evidence | Stale evidence | Verified | Verified | Verified |
| GPT-6.1 Sol generated controller | Verified | Verified | Verified | Verified | Verified | Verified |

There are 18 trials, one per cell. All tasks were functionally correct at completion; the two stale-control failures lack fresh visible verification. All 152 worker invocations confirmed cleanup; no infrastructure-inconclusive outcome occurred in this new workflow run. Worker wall time totaled 109.13 seconds.

The generated controller made a real source edit in all six cases. In the configuration case it performed nine actions and two visible verifications. In the source-comment case it rewrote the module back to the exact previously verified content and reused that receipt: eight actions, two edits, one visible verification. This is valid under the pre-existing exact-restoration rule. It does not establish that reverting external edits is acceptable in a broader task with preservation obligations. No scoring code changed after observing this behavior.

## Scientific interpretation

The apparatus distinguishes stale evidence from valid unchanged-footprint reuse and exact restoration. However, the generated controller again succeeded uniformly. Together with the earlier uniformly successful generated repairs, this leaves the main hypothesis untested: we still lack a generated pool where source-only, generic and mechanism-guided selectors make meaningfully different choices. The earlier 60-trial development comparison selected the same candidate under every method.

There is **no confirmed naturally occurring stale-evidence failure**, no held-out repair-transfer result, and no evidence that the proposed selector outperforms baselines. The authored stale control is a measurement check, not a discovered bug. The next research step needs a realistically grounded failure source, rather than repetitions of this easy deterministic template. A separately labeled controlled study remains an option; it must not be presented as natural failure discovery.

## Artifacts and checks

- [Authored workflow results](../evidence/workflow-controls-004/summary.json) and [generated controller results](../evidence/stateful-controller-005/summary.json), including all traces, code snapshots and inference output.
- [Workflow outcomes](../report/figures/workflow-003/workflow-outcomes.png) and [recorded actions](../report/figures/workflow-003/workflow-actions.png), with SVG/PDF versions, replayed analysis and hash manifest. The earlier `workflow-002` export is an intermediate layout, preserved separately.
- **86 offline tests passed**, three opt-in Docker cases skipped. The primitive was exercised by the new 18-case end-to-end run; its three Docker boundary tests also appear in checkpoint verification.
- All **143 recorded trial traces** replay with expected tips and matching verdicts, including originals with infrastructure issues. New workflow analysis verifies program/case/plan/source-snapshot identities and worker-result hashes.
- The [verification export](../evidence/checkpoint-050.json) records tests, accounting, replay and scope facts. The durable ledger contains exactly three completed calls: **27,232 input / 2,458 output tokens**. Remaining inference allowance: **zero**. Subscription dollars are unavailable.

New TODO completions: **S14, A40, A41**. B51/B52 remain open for realistically grounded natural-failure discovery and diagnosis; B54 remains open for a feasible, funded final study size. No independent audit, remote publication or final submission has occurred. Neuroevolution artifacts were preserved.
