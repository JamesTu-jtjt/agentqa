# Beyond the Repaired Example

**Metamorphic Validation of Self-Improving Coding Agents**  
Research proposal for Sakana AI's open-ended exercise · Draft, 1 November 2026

**Research question:** Can test families that preserve a known failure mechanism select agent modifications that generalize better than retesting the original failure or generating generic task variations, at a comparable evaluation budget?

**Proposed scope:** A runnable proof of concept studying stale verification evidence in coding agents, accompanied by a research report and reproducible artifacts. This document proposes work; it contains no experimental results.

## 1. Motivation and proposed contribution

A coding agent runs tests, changes relevant code, and subsequently reports completion using the earlier passing result. A self-modification makes that example pass by adding a reminder to rerun a particular command. Has the agent learned to keep verification evidence current, or has it patched one recognizable example?

This project studies that distinction. Starting from a confirmed agent failure, it constructs executable families of related scenarios that preserve the failure's defining conditions while varying incidental details. Candidate agent modifications are evaluated on these families before selection. An independent audit then measures whether the selected modifications repair unseen instances without preventing legitimate task completion.

The intended contribution is a **method for constructing valid failure families and evidence that those families improve repair selection**. The project connects metamorphic testing to quality assurance for self-improvement: what evidence justifies believing that a modified agent has addressed a recurring failure?

The work is motivated by DGM's empirical selection of self-modifications [1]. A bounded ShinkaEvolve integration supplies candidate harness edits [2]. The original contribution would be the testing and selection method, rather than running either framework unchanged.

## 2. Fit with the exercise and the applicant

The supplied exercise asks for study of the relevant Sakana work, an original and interesting contribution, and a report explaining the work. It explicitly accepts proof-of-concept results and takes resource constraints into account. It does not specify a report length, minimum benchmark score, model budget, or submission-file format in the provided pages.

This proposal addresses the research themes of agentic coding and sample-efficient self-improvement. It builds on the applicant's experience in metamorphic testing, coding-agent evaluation, and production QA, with a particular focus on whether workflow state preserves the information needed for correct behavior.

The report would briefly relate the project to the assigned reading: the AI Scientist's research workflow, ShinkaEvolve's program evolution, DGM's agent archive, and Digital Red Queen's changing competitive pressures. Detailed experimental dependence is limited to the coding-agent setting and ShinkaEvolve. The proof of concept does not require reproducing all these systems.

## 3. Closest work and the novelty boundary

| Existing work | Relevant overlap | Contribution this project must establish |
| --- | --- | --- |
| DGM [1] | Agents modify their code and are selected using empirical evaluation. | Whether a particular form of repair evidence improves the choice among modifications. |
| ShinkaEvolve [2] | Evolves programs using executable evaluations. | A new evaluation method for agent reliability, rather than a new evolutionary search algorithm. |
| Does Failure Feedback Direct Agent Self-Modification? [3] | Separates target repair, transfer, and held-out net improvement; analyzes DGM and controlled revisions. | An executable method for constructing mechanism-preserving test families and testing their selection value. Merely measuring generalization is insufficient. |
| AgentAssay [4] | Statistical agent regression testing, metamorphic relations, and comparisons across agent versions. | Failure-conditioned family construction, validated applicability, and comparison against equally budgeted generic transformations. |
| HarnessFix [5] | Uses trace evidence to diagnose and repair harness defects. | Assessing the generality of candidate repairs, with candidate generation held fixed in the main comparison. |
| Self-Harness [6] | Mines weaknesses, proposes harness modifications, and checks regressions. | Whether failure families supply useful evidence beyond ordinary regression validation. |

**Working novelty claim, subject to further checking:** Executable transformations that preserve a confirmed failure mechanism can make candidate selection more predictive of unseen repair success than source-only retesting or generic variations. This is a hypothesis, not a claim that metamorphic agent testing or repair generalization is new.

## 4. Concrete failure class: stale verification evidence

The minimum study focuses on one mechanism: **an agent treats a successful test result as evidence about a repository state that the test did not verify**.

Each small, executable repository has a declared verification footprint: relevant source files, tests, and configuration. The task explicitly requires successful verification of the final footprint before completion. A test result is associated with the footprint fingerprint at execution time. Subsequent changes within that footprint invalidate it; unrelated files outside it do not. Dependencies and nondeterministic external services are fixed for this bounded study.

This is an explicit task contract, not a universal assertion that every edit in every real repository requires all tests to be rerun.

**Illustrative source failure:**

1. Tests pass on footprint `v1`.
2. A relevant edit produces footprint `v2`.
3. The agent continues through a summary or a handoff containing the earlier passing result.
4. It declares completion without obtaining passing evidence for `v2`.

The independent evaluator records file changes, test execution fingerprints, exit status, and completion events. It checks both functional correctness and evidence freshness. A structured completion action makes the verdict executable; an LLM judge is not the primary oracle.

A change that always refuses to finish is not a successful repair. A change that always reruns the required tests can be valid and must receive credit; its additional cost is reported separately.

## 5. Method: construct and validate failure families

**Input:** A reproducible source failure, its trace, the relevant harness code, and an independently specified behavioral contract.

**Failure specification:** Record the invalidating event, the old evidence, the missing or ignored provenance, the later decision that consumes that evidence, and the transformation preconditions. For the initial study, a human specifies the failure class once and reviews source diagnoses. The project does not claim unrestricted automatic causal discovery.

**Family construction:** A generator instantiates and composes transformations from a small executable operator library. It varies repository structure, evidence presentation, and distances between invalidation and consumption. Generated cases retain machine-checkable provenance. The generator cannot change the oracle or invent applicability conditions merely to make a candidate fail.

| Transformation | Preconditions and expected relationship |
| --- | --- |
| Consistent renaming | Update paths, imports, and test entry points consistently. The task remains executable and the freshness obligation is unchanged. |
| Insert irrelevant observations | Preserve the repository and all necessary evidence; remain within the stated context budget. Successful completion must still satisfy the same contract. |
| Move a history-compaction boundary | Preserve access to the information required to establish freshness through the supported interface. Test whether the agent's own memory policy retains or recovers it. |
| Vary the carrier of old evidence | Present genuine old results through a supported transcript, cache, or handoff, with recoverable provenance. The result must not become valid merely because its presentation changes. |
| Matched invalidation control | Compare otherwise matched histories with and without a relevant footprint change. Existing evidence is usable only in the unchanged case; the changed case needs fresh passing verification. |

The first four transformations preserve the relevant obligation. The last is a contrastive relation: a controlled state change must alter which evidence is sufficient. Correct traces need not be identical, and rerunning tests in the unchanged case remains permissible.

**Validity checks:** Execute transformed fixtures, verify their footprint mappings and event histories, confirm that necessary information is available, and run a reference controller capable of completing the task correctly. Reject invalid transformations before measuring candidate performance. Keep invalid-generation counts and manual review effort as results.

These checks establish bounded validity under the fixture model, not arbitrary natural-language equivalence. Passing the source task alone is never used to establish a relation's validity.

**Selection:** Evaluate the same frozen candidate pool under alternative selectors. Select by mean verified task completion, subject to the same regression gate. For the minimum study, a candidate must have at least as many verified completions and no more contract violations than the parent on each common regression scenario across the repeated runs. This is a fixed empirical screening rule, not a statistical guarantee. Break ties by measured execution cost, then a fixed candidate identifier. Include the parent agent as an option; if no candidate qualifies, retain it. Freeze this rule before the final audit.

## 6. Sakana integration and editable boundaries

Use ShinkaEvolve to propose bounded changes to a coding agent's editable harness module: memory serialization, evidence bookkeeping, and verification/completion policy. Pin the upstream revision and record the integration changes. Candidate generation receives source-failure feedback only, so all selectors see the same proposed repairs.

The agent may repair its internal provenance tracking or add a freshness check. It cannot edit the external event recorder, hidden tests, task contracts, fixtures, or audit data. An external recorder measures behavior but does not silently repair it for the agent.

The main comparison uses frozen candidate pools from the same parent for each source failure. This isolates selection quality. It supports a claim about one-step repair selection, not sustained open-ended evolution. A short sequential evolution run is an extension only if the core comparison warrants it.

## 7. Research questions and comparisons

**RQ1 — Detection:** Among modifications that repair the source example, do the proposed families expose additional failures on the same mechanism?

**RQ2 — Selection:** Do these families select modifications with higher verified completion on independent audit scenarios than equally budgeted alternatives?

**RQ3 — Tradeoffs:** Are gains accompanied by extra test execution, legitimate-task refusal, unrelated regressions, or substantial family-generation cost?

Three main selectors share candidate pools, generation feedback, a small regression suite, execution limits, and a common selection rule:

| Selector | Evidence used within its selection budget |
| --- | --- |
| Source-only | Repeated executions of the original failing task. |
| Generic variations | Original task plus valid renamings, paraphrases, and unrelated-context variations, without failure-mechanism-directed construction. |
| Failure-family method | Original task plus validated variations targeted at the known evidence-invalidation mechanism. |

The generic baseline uses the same underlying scenario representation, oracle, and validity checks. This avoids giving only the proposed method trustworthy fixtures. Every method has the same rollout allowance and per-rollout ceilings; actual tokens, latency, and generation costs are also reported because equal rollout counts do not imply equal expense.

Include the unchanged parent and a hand-engineered freshness-tracking policy as reference points. The latter tests whether an inexpensive explicit rule already solves the chosen class. It is not counted as a discovered repair. If it dominates every generated candidate, report that clearly.

## 8. Evaluation design and resource envelope

**Illustrative minimum study, to be finalized after a cost-only pilot:**

- Four independently confirmed source failures, preferably from distinct small repositories or workflow configurations.
- Four candidate modifications per source: 16 candidates in total, retaining all failed and ineffective proposals in the accounting.
- Six selection-case slots per candidate per selector, with three independent runs per slot. Source-only spends its slots on further source repetitions.
- Two common regression scenarios per candidate, with three runs each; these results are shared across selectors.
- Twelve independent audit scenarios, split between stale-evidence challenges and legitimate-completion controls, with three runs per candidate.

This amounts to approximately 1,572 execution episodes: 864 selection, 96 common regression, 576 candidate audit, and 36 parent audit episodes. Parent selection and regression runs, source-failure discovery, reference-controller checks, the hand-engineered reference, candidate generation, and pilot runs are additional and must be budgeted explicitly. This is a planning estimate, not authorization to spend or a required Sakana budget. Measure pilot episode costs before setting a monetary cap; reduce candidate breadth before sacrificing the independent audit.

**Separation:** Source failures and visible selection variants are development data. Independently authored audit repositories, scenario templates, and transformation compositions are sealed before candidate evaluation. Splits are made by repository/template family, not by randomly dividing near-duplicate variants. Audit results are never returned to the editor or family generator. Audit executability is checked independently before unsealing, with all exclusions documented.

**Natural versus seeded failures:** First seek naturally occurring failures in instrumented agent runs. Controlled harness defects and deliberately narrow patches are useful for checking that the measurement apparatus works, but are labeled and analyzed separately. If naturally occurring failures are too sparse, report a controlled study and narrow the claims rather than mixing seeded failures into a purported natural-failure result.

**Measurements:**

- Primary: independent-audit verified completion of the agent selected by each method, compared within the same source-failure pool.
- Source repair rate and same-mechanism audit performance, reported separately.
- Unsupported completion claims, task failures, unnecessary refusals, and unrelated regressions.
- Relationship between selection scores and audit outcomes across all candidates, including rejected ones.
- Valid transformation yield, human review effort, tokens, tool calls, wall time, and monetary cost.

Report paired differences by source family and the raw outcome counts. Treat correlated variants as members of a family, not independent discoveries. Three repeats provide an initial estimate of stochastic behavior, not a certification of reliability; four source pools give weak statistical power. Any uncertainty intervals must respect grouping, and a small study should emphasize effect sizes and individual cases rather than broad significance claims.

## 9. What would count as an informative result?

The hypothesis is supported if family-based selection consistently chooses candidates with better independent-audit verified completion than the generic-variation baseline, within comparable resources and without simply refusing more tasks.

It is weakened if ordinary variations perform equally well, if source success already predicts transfer, if transformation validation consumes disproportionate resources, or if all candidate modifications behave alike. A pool containing no broadly useful repair cannot establish the value of a selector; report candidate availability explicitly.

The result should explain at least one selection decision through an executable trace: what a narrow repair handled, which valid variation exposed its limitation, and whether the independent audit confirmed that distinction. A negative finding with a valid benchmark and clear accounting still provides a technically meaningful proof of concept; it must not be presented as evidence that the proposed selector works.

## 10. Proposed submission deliverables

These are recommended ways to satisfy the exercise's original-work, proof-of-concept, and report expectations. Page counts and packaging are proposal choices, not requirements stated in the supplied brief.

| Deliverable | Concrete contents |
| --- | --- |
| Research report | Approximately 6–8 main pages: motivation, related work and novelty boundary, method, validity assumptions, comparative results, costs, limitations, and conclusions. Appendix for contracts and scenario details. |
| Runnable proof of concept | Small coding-agent environment, ShinkaEvolve adapter, family generator, validity checks, executable oracle, selectors, and audit runner, with pinned dependencies and a quick-start command. |
| Reproduction bundle | Scenario/split manifests, source traces, candidate diffs, model settings, seeds where supported, raw results, analysis scripts, and complete resource accounting. Cached traces allow inspection without new model calls. |
| Demonstration | One short replay showing a source failure, an apparently successful narrow repair, a valid related case that exposes its limitation, and the independent audit outcome. Use actual outcomes, including negative ones. |

The report's central figures would compare source repair with unseen repair transfer, compare the three selectors on verified completion and cost, and show one trace-level explanation. This is sufficient for a focused research submission without a broad product interface or a full benchmark reproduction.

## 11. Scope and principal limitations

The minimum contribution concerns one bounded class of coding-agent reliability failures. It does not establish general agent safety, universal causal diagnosis, or long-run self-improvement. An executable oracle for this class is a strength for measurement, but does not eliminate the oracle problem in open-ended tasks.

The main unresolved novelty question is whether validated, mechanism-directed family construction adds enough beyond existing regression and metamorphic testing. The matched generic baseline is essential to answering it. Full autonomous relation discovery, multi-agent co-evolution, additional languages, and a second failure mechanism are possible later extensions rather than minimum deliverables.

## References

1. [Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents](https://arxiv.org/abs/2505.22954). [Official implementation](https://github.com/jennyzzt/dgm).
2. [ShinkaEvolve: Towards Open-Ended and Sample-Efficient Program Evolution](https://arxiv.org/abs/2509.19349). [Official implementation](https://github.com/SakanaAI/ShinkaEvolve).
3. [Does Failure Feedback Direct Agent Self-Modification?](https://arxiv.org/abs/2610.14662), October 2026 preprint.
4. [AgentAssay: Token-Efficient Regression Testing for Non-Deterministic AI Agent Workflows](https://arxiv.org/abs/2603.02601), technical report; especially its metamorphic relations and cross-version regression discussion.
5. [From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws](https://arxiv.org/abs/2606.06324).
6. [Self-Harness: Harnesses That Improve Themselves](https://arxiv.org/abs/2606.09498).
7. [Towards end-to-end automation of AI research](https://www.nature.com/articles/s41586-026-10265-5).
8. [The Agentic Scientist](https://pub.sakana.ai/agentic-scientist/).
9. [Digital Red Queen: Adversarial Program Evolution in Core War with LLMs](https://arxiv.org/abs/2601.03335).
