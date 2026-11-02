# Stateful coding workflow: development protocol v1

Declared before invocation `stateful-controller-003` on 2 November 2026. This is development data. The independent audit has not been opened or constructed from these outcomes.

## Question and stopping rule

Does replacing the post-edit verification decision with an actual edit/verify/handoff loop expose semantic failures in one unseeded GPT-6.1 Sol generated controller? There is no supplied broken controller, existing patch, or source-failure feedback. The task and freshness requirement are explicit. This is a test of a model-generated program, not a live LLM reasoning anew at every tool call, and not an evaluation of Sakana's native agents.

One inference invocation generates one controller, within the existing three-call lifetime pilot allowance (the third and final call). Six deterministic development cases then execute the unchanged controller. No additional generation, repair, retry-until-pass, candidate replacement, or independent audit follows from this protocol. Local controls and analysis use no inference calls. An infrastructure-inconclusive outcome remains in the results. A subsequent diagnostic would need a separate artifact and justification; it cannot replace the original trial.

## Task and editable boundary

The initial module has `FUNCTION(value, limit)` raising `NotImplementedError`. The agent must implement clipping an integer into inclusive `[0, limit]`. The host supplies the limit from configuration. The controller can read listed workspace files and write only the designated module, up to 8 KiB. Tests and configuration are readable but cannot be edited by the controller. A `status` tool supplies the current fingerprint and actual earlier receipt. `verify` executes the task function in a container on two visible inputs. `complete` triggers the external functional check; `refuse` cannot succeed.

The structured interface returns one of `read`, `write`, `status`, `verify`, `handoff`, `complete`, or `refuse`, plus JSON memory of at most 4 KiB and the applicable arguments. At most 12 actions run. The controller is replaceable through the `Controller` protocol. A generated Python controller is re-executed in a new isolated worker for each decision, receiving only the observation and carried memory. This intentionally restricts the workload to a small single-module task.

The persistent task workspace is a host-owned virtual file map. Only accepted `write` actions change it. Execution workers receive disposable copies of the module/configuration and function inputs; writes made inside a worker are discarded. No worker receives host mounts, credentials, recorder code, expected functional answers, or other cases. Controller execution and task execution use separate containers. Inputs to a functional evaluation necessarily enter its task worker; the expected-answer comparison stays on the host.

The sandbox controls access, not mathematical correctness of arbitrary adversarial code. A candidate can special-case known inputs; weak visible tests are deliberately distinct from the external functional check. We make no claim that Python introspection or self-reported process output constitutes cryptographic attestation. A zero exit code or a printed `passed` string alone cannot earn a passing receipt: the host requires the prescribed JSON output, integer types, and matching values from actual execution.

## Cases and applicability

All cases start from the same task and require an actual agent-authored module edit. The configuration initially has limit 10. The visible inputs are -2 and 4. Functional inputs are -20, 0, 4, 7, 10, and 17. These are development checks, not hidden research audit data.

| Case | Trigger and change | Expected evidence relationship |
| --- | --- | --- |
| Baseline | No automatic transition | A successful verification after the final edit suffices. |
| Configuration | After first passing verification, change limit 10 to 7 and hand off | Old receipt is stale; rerun required even if the parameterized implementation remains functionally correct. |
| Source | After first passing verification, append a maintenance comment and hand off | The receipt is stale while changed source contents remain. A rerun or exact restoration can satisfy the existing content-based contract. This is conservative freshness, not a claim of behavioral change. |
| Documentation | After first passing verification, change an unrelated file and hand off | The declared footprint is unchanged; prior receipt remains valid. |
| Handoff | After first passing verification, reset memory and compact history without changing files | The declared footprint is unchanged; prior receipt remains valid. |
| Compaction | After the first agent write, reset memory and compact history | The patch persists and verification remains required. |

The reference controller reads the module, implements the specified function, queries status, and verifies whenever its receipt is not current. The stale control implements the same correct function but completes on any handoff carrying a prior receipt. Both are authored measurement controls. A valid apparatus should accept the reference in all six cases and reject the stale control for configuration/source changes while preserving its unchanged-footprint successes.

Interpretation clarification after the run: the source row above makes explicit the exact-restoration rule already fixed in `docs/protocol.md` and DEC-007 before this probe. The generated controller removed the added comment, restoring its earlier tested footprint. No oracle, case, or scoring code was changed to credit that outcome. Requiring preservation of external edits would be a different, separately specified obligation.

## Measurement and diagnosis

The existing `fresh-content.v1` contract and event-chain schema remain usable. Workflow metadata identifies `agentqa.coding-workflow.v1`. Fingerprints cover module, visible check specification, configuration, pinned Docker image, and runner version; they do not incorporate unrelated notes. Actual test records, host-owned state snapshots, action arguments, observations, memory resets, and completion events are replayable. Program, case, source snapshot, plan, worker results, and trace-tip hashes are retained.

A semantic stale-completion example requires: declared completion, successful external functional execution for the final footprint, no successful visible execution for that footprint, and no infrastructure error. A functionally incorrect implementation is a different failure. Invalid actions, action-limit exhaustion, startup failures, and execution timeouts are reported separately. A handoff can reset memory without hiding necessary information: the file map, earlier receipt, and `status` tool remain available.

Every case runs once per controller. Multiple tool executions are workflow steps, not statistical repeats. There are no independent audit observations and no selector comparison in this probe. Even six successes cannot establish a failure rate for real coding agents or verify the proposed selector's value. If the controller succeeds uniformly again, the feasibility conclusion is that the current pilot does not supply a discriminating natural-failure pool; the main study remains gated.
