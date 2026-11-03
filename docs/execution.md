# Implementation and experiment runbook

This document translates the proposal into implementation responsibilities and reproducible execution rules. It specifies planned behavior; the components and commands below do not exist yet unless their TODOs are marked complete with evidence.

## Ownership and boundaries

Codex implements the code, tests, fixtures, experiment runners, analysis, report, and reproducibility package. James leads overall research direction, system design, experimental exploration and refinement, and supplies deadlines and model/resource choices. Routine implementation decisions within the agreed scope belong to Codex. Review requests should concern a concrete unresolved choice or completed result rather than repeated permission to perform ordinary development.

James authorized implementation and subsequently use of his Codex account with low usage. The route is saved ChatGPT authentication via Codex CLI, exact model `gpt-6.1-sol`, serial, with three persisted invocations and a 120-second runtime bound per invocation. All three have completed: repair generation, an unseeded-policy probe and a stateful-controller probe. The pilot allowance is exhausted. Dollar cost is unavailable for subscription use. A separate API route would require a monetary allowance; credentials alone do not authorize that route.

The repository is `/Users/james.tu/workspace/Interviews/Sakana/AgentQA`. It has its own `.git`, branch namespace, dependencies, artifacts and history. James explicitly authorized private GitHub publication at the 80% stage; the verified destination is `JamesTu-jtjt/agentqa`. The parent repository excludes it. Never stage or repair unrelated changes in the parent or Neuroevolution project as part of this work.

## Proposed component layout

Use a small Python package and standard test tooling, with concrete runtime/dependency versions chosen and pinned during M2/M4. Avoid a web interface or distributed service for the minimum study.

| Planned path | Responsibility | Key verification |
| --- | --- | --- |
| `src/agentqa/contracts.py` | Scenario, footprint, completion, and verdict definitions. | Relevant changes invalidate evidence under the declared contract; unrelated changes do not. |
| `src/agentqa/recorder.py` | External ordered events and trusted execution records. | Candidate text cannot create a trusted test result or rewrite events. |
| `src/agentqa/environment.py` | Resettable repository fixtures, tool execution, resource limits. | Independent trials do not share mutable state; out-of-scope writes fail. |
| `src/agentqa/agent.py` | Model/tool loop and structured completion action. | Bounded actions, failures/timeouts represented, offline mock support. |
| `src/agentqa/families/` | Transformation operators, preconditions, validity checks, generic baseline. | Executability, provenance mappings, available information, reference success. |
| `src/agentqa/evolution/` | Pinned ShinkaEvolve adapter and candidate registry. | Editable module boundary, immutable parent, complete candidate provenance. |
| `src/agentqa/selection.py` | Source-only, generic, and failure-family selection. | Same pools, common gate, declared budgets, reproducible tie rules. |
| `src/agentqa/runner.py` | Trial scheduling, checkpoints, cost and retry accounting. | Safe resume, no duplicate completed trials, stop at declared limits. |
| `src/agentqa/analysis.py` | Metrics, paired comparisons, plots and report tables. | Synthetic outcomes produce expected calculations and grouping. |
| `tests/` | Unit, integration, fixture, and replay checks. | Boundary failures tested, not merely mirrored implementation behavior. |
| `configs/`, `fixtures/`, `manifests/` | Versioned development inputs and frozen experiment identities. | Split/template integrity and full input hashes. |
| `evidence/`, `report/`, `demo/` | Selected sanitized artifacts, final narrative, replay. | Every reported result traces back to a frozen run. |

Audit fixtures are stored outside the candidate-visible workspace even if they are eventually included in a final reproduction bundle. During runs, the evaluator mounts only the active task inputs. The editor sees development failures, never audit outcomes or audit fixture contents.

Implemented path mapping at the 50% checkpoint: family operators are in `families.py`; registry and upstream adapter are `registry.py` and `shinka_bridge.py`; the resumable development scheduler is `comparison.py`. `agent.py` implements the earlier verification-only policy loop. `workflow.py` now implements the editable coding loop and structured controller interface, with separate controller/task containers and a host-owned virtual workspace. Containers receive serialized task copies rather than host mounts. Analysis/plotting entry points are in `scripts/`; final independent-audit analysis is still pending. See `docs/workflow-protocol.md` for the precise new boundary.

## First end-to-end slice

Before integrating any live model, complete one local slice: create an executable repository; record passing tests; change a relevant file; simulate completion with stale evidence; reject that completion; run fresh tests and accept a correct result. Replay the evidence from disk. Add an unchanged-footprint control and an unrelated-file edit.

Then exercise a deliberately narrow repair and a reference policy across a valid transformed pair. These are measurement controls. They establish that the infrastructure can distinguish behaviors, not that real agent repair generalizes or that the research hypothesis holds.

## Contract decisions to resolve in M1

- Specify whether footprint identity means current content identity or a version/event lineage. Under content identity, restoring the exact footprint may make earlier evidence usable in a fixed deterministic environment; under a stricter lineage contract it may not. Pick one, justify it, and test it consistently.
- Include declared test/config inputs and fixed dependency state in the verification semantics; do not silently equate source hashes with all behavior-affecting inputs.
- Separate functional correctness from evidence freshness. Fresh passing execution of a weak visible suite alone does not establish that the requested repair is correct; the evaluator also uses the task's independently specified functional checks.
- Define missing, partial, failing, timed-out, and fabricated verification records; none are successful verification.
- State the information-access assumptions for compaction and handoffs. A transformation that irretrievably hides a fact required for correctness is not a valid robustness test under an information-preserving claim.

## Candidate execution and experimental independence

Use disposable isolated workspaces for generated code. Select and verify a practical sandbox during implementation; do not claim that a directory allowlist alone contains arbitrary Python. Candidate tools receive only the intended task data. Keep evaluator state, host credentials, audit material, and experiment metadata outside their accessible execution context. If model access is needed from candidate code, mediate it through the host-side interface rather than providing raw provider credentials to the worker.

The external evaluator observes and grades; it does not silently force every candidate to rerun tests. A candidate may itself add a deterministic freshness check, which is a valid repair and should receive credit.

Candidate generation is held fixed for the main comparison. Record every proposed edit, including invalid and ineffective candidates; apply the predeclared rule for how failed generations consume the candidate allowance. Never resample failed candidates selectively for one method. All three selectors evaluate identical candidate hashes and may retain the parent.

One implementer can author both development and audit fixtures, so the study cannot claim author blinding. Independence here means separate repository/template families, frozen definitions, no audit feedback during development or selection, and no candidate access. State this limitation plainly. Additional human review is useful where available; do not represent Codex's self-review as independent human validation.

## Budgeting and stop conditions

The proposal's illustrative main study allocates:

| Work | Episode calculation | Episodes |
| --- | --- | ---: |
| Three selectors | 16 candidates × 3 selectors × 6 slots × 3 repeats | 864 |
| Shared regression | 16 candidates × 2 cases × 3 repeats | 96 |
| Candidate audit | 16 candidates × 12 cases × 3 repeats | 576 |
| Parent audit | 12 cases × 3 repeats | 36 |
| Subtotal | Excludes additional work below | 1,572 |

Add discovery, model/candidate generation, pilot runs, parent selection/regression runs, the hand-engineered reference, infrastructure retries, and contingency. An episode may contain many model calls. Price the full observed distribution of calls/tokens and tool time after a bounded pilot; do not multiply an assumed single-call price by the episode count.

Record provider, exact model ID, pricing source/date, per-call/per-episode ceilings, maximum concurrency, total cap, pilot allowance, and reserved audit budget. The runner must reserve a conservative upper bound before launching calls, including concurrent calls, then reconcile actual usage. If usage is unavailable, retain a conservative estimate and label it. Stop before starting work that would exceed the cap.

An exhausted pilot allowance stops discovery. A missing or exhausted total allowance stops additional paid execution; Codex can still analyze completed data and improve local documentation. An oracle/integrity defect stops dependent experiments regardless of remaining budget.

## Artifact and trial ledger

Each run records a unique run/trial ID; protocol version; code and input hashes; source/template/family IDs; candidate and parent hashes; selector; model settings; randomness controls where supported; tool limits; start/end times; event trace; verdict; error category; actual/estimated resource use; and retry linkage.

Model-visible task failure is a result, not an infrastructure error. Freeze a bounded retry policy for transport/runtime failures before the main run. Preserve the original failed attempt, reason, and cost. Never rerun a stochastic failure until it passes and then report only the passing attempt.

Local `runs/` contains large/transient execution outputs and is ignored by Git. Copy selected sanitized evidence and manifests into `evidence/` for the submission. Required final artifacts must not exist only in ignored directories. Store secrets only outside versioned artifacts; redact them from logs without changing empirical outcomes.

## Freeze, audit, and analysis sequence

1. Validate development and independent audit fixture executability using fixed references. Keep audit outcomes out of tuning feedback.
2. Freeze the contracts, split membership, transformation rules, limits, selection rule, exclusions, retry rules, and analysis implementation. Record hashes in a manifest.
3. Generate/freeze candidate pools using source-only feedback. Record all attempts and the rule for invalid candidates.
4. Complete selection and common regression evaluation; record selected candidate IDs before opening audit outcomes.
5. Audit all candidates and references, including rejected candidates. This separates generation quality from selection quality.
6. Generate tables and figures with the prewritten analysis. Report paired source-pool differences, raw counts, and resource costs; acknowledge limited power.
7. Explain failures with traces. Any post-audit change is a documented protocol amendment or exploratory result, not a retroactive improvement of the primary result.

No outcome is required to favor the proposed method. The generic baseline may be sufficient, a hand-engineered policy may dominate, or candidate pools may offer no discriminating choices. These are reportable findings.

## Resuming and delivering

At session start: check the repository root, read `status.md`, identify the next incomplete TODO and its dependencies, and inspect existing work before editing. At session end: record completed task IDs with evidence, tests run, spend/remaining allowance, protocol deviations, and the exact next action. Do not mark model-dependent milestones complete from mocked results.

Before delivery: verify a clean install/export, offline demonstration, result regeneration, report claims, link integrity, and artifact provenance. Provide James the report, runnable code, reproduction bundle, replay, actual cost, and limitations. Publication, remote hosting, and submission are separate actions when requested.
