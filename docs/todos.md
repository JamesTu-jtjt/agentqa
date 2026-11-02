# Implementation TODOs

Owner: Codex unless explicitly marked James. Unchecked items may be planned or partial; consult `status.md` for work in progress. Mark an item complete only after recording evidence in `status.md` or a linked run manifest. Task IDs are stable across sessions.

## M0 — Planning and repository boundary

- [x] **P00** Preserve `proposal.md` in an independent AgentQA Git repository on `james-tu/agentqa`.
- [x] **P01** Write timeline, executable work backlog, execution runbook, status/decisions, and agent instructions.
- [x] **P02** Exclude AgentQA from the surrounding repository and add navigation links without modifying Neuroevolution artifacts.

## M1 — Development specification · Day 1

- [x] **S10** Read the closest papers' relevant methods and inspect upstream interfaces/licenses. Acceptance: a source-linked novelty/overlap matrix identifies what the experiment can distinguish; required Sakana reading is accounted for without claiming unperformed replication.
- [x] **S11** Write `docs/protocol.md`. Acceptance: source failure, verification footprint, successful completion, missing evidence, timeouts, test failures, infrastructure errors, repeated runs, regression gate, and tie-breaking all have executable definitions.
- [x] **S12** Specify artifact schemas and isolation. Acceptance: scenario, event, test record, trial, candidate, family, and split records have IDs/version fields; the editable boundary cannot mutate the oracle or its trace store.
- [x] **S13** Write one source scenario and matched invalidation control on paper. Acceptance: trace states make clear which evidence is usable and what a valid controller must do; unrelated edits and restored-state semantics are addressed explicitly.
- [x] **S14** Define a bounded pilot and spending worksheet. Acceptance: separate allowances for discovery, candidate generation, selection, audit, references, retries, and contingency; no invented model pricing.

## M2 — Environment and oracle · Day 2 · depends on S11–S13

- [x] **E20** Initialize a minimal package, test setup, and isolated dependencies. Acceptance: a clean local install and test command work; nothing depends on Neuroevolution's environment.
- [x] **E21** Implement small executable coding fixtures and resettable workspaces. Acceptance: task state is reproducible; the declared dependency footprint covers relevant source/tests/configuration; unrelated files are distinguishable.
- [x] **E22** Implement the trusted external recorder and actual test-execution wrapper. Acceptance: records contain trial IDs, sequence IDs, footprint fingerprints, process results, and completion events; forged stdout cannot become a trusted passing result.
- [x] **E23** Implement the oracle and reference controllers. Acceptance: real passing evidence for the final footprint is accepted; stale, failing, missing, wrong-trial, and mismatched evidence is rejected. Refusal cannot count as task completion.
- [x] **E24** Test state changes and trace integrity. Acceptance: cover relevant edits, irrelevant edits, test/config edits, failed/timeout tests, reruns, state restoration under the declared contract, and attempted writes outside the editable workspace.
- [x] **E25** Add deterministic offline replay. Acceptance: saved traces reproduce verdicts and an explanation of evidence freshness without invoking a model.

## M3 — Families and controls · Day 3 · depends on E21–E25

- [x] **F30** Implement consistent renaming and unrelated-observation operators. Acceptance: transformed code still executes and relevant contract semantics are preserved.
- [x] **F31** Implement supported compaction/handoff and evidence-carrier transformations. Acceptance: provenance remains recoverable through the permitted interfaces; impossible-information scenarios are rejected.
- [x] **F32** Implement contrastive footprint-invalidation pairs. Acceptance: changed and unchanged cases differ in the validity of prior evidence; both remain solvable.
- [x] **F33** Build the family validator. Acceptance: applicability, mapping consistency, reachability, and reference-controller checks run before candidate evaluation; invalid generation attempts are logged.
- [x] **F34** Build the generic-variation baseline using the same representation/validator. Acceptance: it does not get mechanism-guided transformations or less reliable fixtures than the proposed method.
- [x] **F35** Exercise narrow patches, an always-rerun policy, and a refusing policy as labeled measurement controls. Acceptance: the evaluator credits valid reruns, penalizes refusal, and exposes a documented narrow repair; these controls are not reported as naturally evolved discoveries.

## M4 — Agent, evolution adapter, and accounting · Day 4 · depends on E/F tasks

- [x] **A40** Implement the coding-agent loop and replaceable model interface. Acceptance: bounded tool calls, structured completion, state reset, and an offline mock model exercise the full lifecycle. Evidence: `workflow.py`, 18 new offline checks and 18 real workflow trials; program-generated controllers, not per-step live LLM inference.
- [x] **A41** Implement candidate isolation. Acceptance: candidates can change only the designated harness module and task workspace; hidden fixtures, host secrets, recorder, and oracle are inaccessible from candidate execution. Evidence: separate controller/task containers, host-owned virtual workspace, module-only accepted edits, external expected-answer comparison; `docs/workflow-protocol.md` states the scope and limits.
- [x] **A42** Integrate ShinkaEvolve at a pinned revision. Acceptance: an offline adapter test submits an editable harness program and receives evaluation output; local changes and license/attribution are recorded. Verify actual upstream APIs before implementing.
- [x] **A43** Implement candidate registry and frozen-pool evaluation. Acceptance: parent ID, diff/hash, generation feedback, attempted candidates, invalid candidates, and all selector decisions are preserved. No selector gets its own better candidate pool.
- [x] **A44** Implement the trial ledger, checkpoints, and budget enforcement. Acceptance: unique trial IDs, cost/usage records, bounded retries, reserve checks before calls, and resume without duplicate completed calls; mocked limits stop execution correctly.
- [x] **A45** Implement three selectors and the shared regression gate. Acceptance: synthetic outcomes verify parent retention, candidate eligibility, ordering, ties, and equivalent rollout allowances.
- [x] **A46** Resolve live-run inputs with James. Acceptance: record provider/model access, a pilot cap, and a total cap or an explicit pilot-only allowance in status. James supplies resource choices; Codex prepares options and cost estimates and reuses prior authorization.

## M5 — Pilot · Day 5 · depends on A40–A46

- [x] **B50** Run a small live integration smoke within the pilot allowance. Acceptance: an actual model episode and bounded candidate edit produce trustworthy artifacts; report both successes and failures.
- [ ] **B51** Search for natural source failures within a declared attempt cap. Acceptance: every attempt is recorded, confirmed failures include replayable traces, and natural/seeded origins are labeled.
- [ ] **B52** Validate diagnoses and transformation applicability. Acceptance: independently checked footprint/event facts support the diagnosis; manual review effort is logged; unsupported causal claims are excluded.
- [x] **B53** Check candidate variation and feasibility. Acceptance: a pilot memo reports source repair, behavior differences, narrow/robust controls, and whether the main comparison can discriminate candidates.
- [ ] **B54** Measure cost and select final study size. Acceptance: projected expense includes parent/reference runs, failures, retries, generation, and audit; fits the recorded cap with reserve. Update proposal deviations before final execution.
- [x] **B55** Qualify a grounded upstream evaluator source within a fixed local search. Acceptance: unchanged pinned code, declared fault/reuse conditions, real jobs, positive/negative counterfactuals, source/artifact hashes and precise natural-versus-authored labels. Evidence: `evidence/upstream-source-006/`, `docs/upstream-source-diagnosis.md`. This does not close B51's native model-agent discovery gap.
- [x] **B56** Implement and qualify an attempt-bound publication adapter. Acceptance: no previous result overwrite/reuse; external request/process/artifact binding; validity separate from reported correctness; actual upstream scheduler checks and boundary tests. Evidence: `bundles.py`, 15 offline tests, `evidence/bound-shinka-007/` and `008/`. Only fixed authored local evaluators; generated code remains in Docker.
- [x] **B57** Implement pre-audit analysis on synthetic data. Acceptance: source-pool pairing, complete-grid checks, frozen decisions, separate failure types, small-sample limits and unknown-cost preservation. Evidence: `analysis.py`, 11 tests, `docs/analysis-protocol.md`, `evidence/preaudit-analysis-010/`. Final audit/plan freeze remains open under X60/X61.
- [x] **B58** Broaden publication qualification before packaging. Acceptance: fixed bounded process cases, positive/negative evidence, program/config changes and renamed-layout counterparts; all attempts preserved and labeled development-only. Evidence: `evidence/publication-qualification-011/`, twenty actual processes, twenty contract matches and ten invariant pairs.

## M6 — Freeze and selection · Day 6 · depends on B50–B54

- [ ] **X60** Author independent audit templates/repositories and controls; validate their executability with fixed references. Acceptance: split overlap checks pass, audit outcomes are absent from development feedback, and fixtures are frozen by hash. Document that a single implementer authored the fixtures; do not claim human blinding.
- [ ] **X61** Write analysis code using synthetic data and freeze the protocol. Acceptance: manifest records code, schema, dependencies, models, budgets, split/template hashes, exclusion rules, stopping rules, and analysis revision.

  Partial at 70%: analysis code/specification/snapshot are complete (B57). Final source pools, audit templates and full protocol freeze are not. Do not mark the entire item complete from synthetic inputs.
- [ ] **X62** Generate and freeze the common candidate pools. Acceptance: source-only generation feedback; all proposal attempts and candidates retained; parent/candidate hashes recorded before selection and audit.
- [ ] **X63** Execute matched selection and shared regression trials. Acceptance: complete ledgers, reconciled infrastructure failures, unchanged limits, and recorded selected candidate/parent for each selector and source pool.
- [ ] **X64** Check readiness to open the audit. Acceptance: selected IDs and protocol hashes are recorded; no selector or editor has consumed audit outcomes; budget remains sufficient for the declared audit.

## M7 — Audit and interpretation · Day 7 · depends on X60–X64

- [ ] **R70** Run the sealed audit on all frozen candidates, parent, and references. Acceptance: all declared trial slots accounted for; no candidate tuning or replacements based on results.
- [ ] **R71** Produce primary comparisons. Acceptance: verified completion, source repair versus transfer, refusals, regressions, and resources are reported separately; paired comparisons use source pools as the grouping unit.
- [ ] **R72** Inspect reproducible explanatory cases. Acceptance: traces substantiate why a narrow repair failed and whether selection helped; unfavorable and inconclusive cases are included.
- [ ] **R73** Assess limitations and hypothesis support. Acceptance: distinguish natural/seeded findings, one-step selection versus long-run evolution, small-sample uncertainty, and any protocol deviations. Avoid significance claims unsupported by the design.

## M8 — Delivery · Day 8 · depends on R70–R73

- [ ] **D80** Draft the research report and appendix. Acceptance: all empirical claims link to artifacts; methods/novelty/limitations are clear; no placeholders masquerade as findings. Target 6–8 main pages, not a claimed task requirement.
- [x] **D81** Package the runnable proof of concept. Acceptance: documented install, offline demo, optional live run, and analysis commands are implemented and verified; pinned dependencies and upstream attribution included. Evidence: `docs/reproduction.md`, wheel install, replay/analysis commands, existing pilot/live integration. Complete for the current prototype; future main-study changes need revalidation.
- [x] **D82** Package a sanitized reproduction bundle. Acceptance: manifests, candidate diffs, settings, traces/results, and costs are sufficient to regenerate tables; credentials and unrelated internal data are absent. Evidence: deterministic `build_repro_bundle.py`, explicit publication inventory and clean-export check. This packages completed prototype evidence, not unperformed main-study data.
- [x] **D83** Produce the short demonstration replay. Acceptance: uses actual recorded outcomes and clearly distinguishes an illustrative control from a discovered agent repair. Evidence: `report/demo/index.html`; hashes and four tabs verified; authored/native limitations visible.
- [x] **D84** Verify from a clean temporary checkout/export. Acceptance: meaningful tests pass; offline artifacts regenerate; documentation links and report figures resolve; no dependence on developer-only paths or untracked required files. Evidence: `evidence/clean-reproduction-080.json`; 124 tests, installed wheel, evidence replay, matching analysis and HTML. Repeat after future substantive changes.
- [ ] **D85** Update README/status and hand over the package. Acceptance: precise file links, reproduction instructions, completion status, final spend, and remaining limitations. Remote publication/submission occurs only if separately requested.

## Deferred extensions

- [ ] Sequential evolution with repeated acceptance decisions, after the one-step result is understood.
- [ ] A second failure mechanism such as dropped pending obligations.
- [ ] Additional model backbones, languages, or real-world repositories.
- [ ] Automatically discovered relation programs rather than a bounded operator library.

These items do not block the minimum submission.
