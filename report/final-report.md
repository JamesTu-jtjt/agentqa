# Beyond the Repaired Example

## Metamorphic validation of agent repairs: a controlled pilot

James Tu | Cornell University | Sakana AI research exercise | 2 November 2026

**AI assistance.** Codex implemented the prototype, ran the recorded experiments, analyzed outcomes and assisted report writing. James supplied research direction and resource constraints. No independent human review is claimed.

**Abstract.** Self-improving coding systems need to distinguish a repair that fixes one example from a repair that preserves the underlying reliability obligation. We investigate whether test families organized around stale verification evidence improve selection among model-generated repairs. AgentQA records actual execution, binds passing evidence to a declared content footprint, and grades functional correctness separately from freshness. A three-call GPT-6.1 Sol feasibility pilot produced two source-conditioned policies, but neither failed the development family. We therefore prospectively froze a separately labeled controlled transfer audit rather than searching indefinitely for a favorable pool. Both unchanged repairs passed all nine new cases; the authored parent passed three. All three matched selectors had selected the same repair, yielding zero observed selector advantage. Separately, six authored fault/reuse scenarios reproduced three stale or mixed result attributions through an unchanged pinned ShinkaEvolve scheduler. An authored attempt-bound adapter rejected incomplete evidence in subsequent qualification. The deliverable is a runnable QA prototype, reproducible evidence and an explicitly inconclusive selection result; it is not a completed native-agent evolution study.

## 1. Research question and scope

Can valid metamorphic families built around a known failure mechanism select repairs that transfer better than source-only retesting or generic variation, at matched evaluation budgets? The proposed contribution is selection value under valid transformations. Merely generating variants, adding provenance checks or fixing an authored example would not answer that question.

The initial failure class is **stale verification evidence**: passing tests for one source/test/configuration state are used to justify completion after a relevant change. The QA target is the connection between a claim and its execution evidence. A function can be correct while the evidence supporting completion is stale; conversely, a fresh weak test can pass while the function is wrong.

This pilot targets the reliability infrastructure around agent improvement. It aligns with empirical agent evolution and automated research [1-3], while holding the model-generated candidate pool fixed to isolate selection. The completed controlled audit evaluates cached completion policies after authored repairs. It does not test models autonomously repairing new repositories, discover natural model failure rates, or run a complete Sakana evolutionary search.

**Delivered.** An execution/replay core, isolated generated-program workers, frozen candidate/attempt registries, matched selectors, a bounded editable coding workflow, a real pinned scheduler bridge, source-grounded publication diagnostics, a completed controlled audit, and a self-contained demonstration. No positive result is required or claimed.

<!-- page -->

# 2. Positioning and measurement contract

## Closest work and novelty boundary

The AI Scientist automates stages of the research lifecycle [1]. DGM maintains an archive of agents and empirically evaluates self-modifications [2]; ShinkaEvolve evolves executable programs using feedback [3]. AgentQA concerns the trustworthiness and generalization of acceptance evidence, rather than introducing a new archive sampler or mutation algorithm.

AgentAssay already studies agent metamorphic relations and regression testing [4]. SyncMind studies recovery from evolving collaborative repository states [5], and SWE-Touch injects validated conflicting edits during coding [6]. Thus neither agent metamorphic testing nor shared-workspace changes constitute a new contribution here.

HarnessFix connects failed traces to scoped harness repairs [7]. Self-Harness combines failure mining, candidate harness changes and regression validation [8]. A recent failure-feedback study distinguishes directed repair, transfer and net held-out change [9]. These precedents motivate a common-pool comparison with separate source, selection and audit roles. Agentic Scientist documentation also describes provenance consistency checks [10]. A freshness architecture alone is not a first-in-field claim.

The remaining research hypothesis is that **mechanism-directed, applicability-validated families improve which generated repair is selected**, beyond source-only or generic checks. The present pool does not supply evidence for that hypothesis. The review is targeted, not an exhaustive novelty certification.

## Executable contract

A footprint hashes the declared source, visible tests, configuration and runtime identity. Fresh evidence requires an actual passing visible execution whose before/after footprint equals the final footprint. Functional correctness comes from evaluator-owned assertions. The primary endpoint is:

```
verified = declared completion AND functional correctness AND fresh evidence
```

Refusal is not successful completion. Failed tests and modified-during-test executions cannot become passing evidence because a model prints a success message. Exact restoration of tested content can reuse its receipt in the bounded deterministic world; unrelated documentation does not invalidate it. This contract does not cover undeclared external services, hidden dependencies, arbitrary environment nondeterminism or concurrent histories beyond observed states.

Host-owned, hash-chained records retain state, actual test status and completion. Replay checks integrity against frozen trace tips, not authenticity against an attacker replacing the entire store. Generated policy/controller code and generated task modules run only in Docker without host mounts, network or credentials, with bounded CPU/memory/processes/output/time. Trusted local subprocess fixtures execute authored code only. The boundary and oracle are separate from candidate-editable resources.

<!-- page -->

# 3. Design and prospective controls

## Feasibility before the audit

Three serial subscription inference calls used GPT-6.1 Sol with a 120-second bound per invocation. The first generated two completion-policy repairs from an authored always-complete parent and one authored clamp failure. Both policies inspect verification provenance. One unseeded policy and one stateful controller were generated in the remaining calls. No naturally observed semantic freshness failure was confirmed. Three original worker timeouts were preserved as infrastructure-inconclusive; an unchanged-program diagnostic later passed after startup and execution timing were separated.

The stateful workflow supports source edits, actual execution, configuration changes, compaction and handoff. Its generated controller passed six cases; an authored stale control failed two. The model generated a controller program once, not a new inference at every action. These feasibility outcomes do not establish realistic agent repair performance.

![Stateful workflow outcomes](figures/workflow-003/workflow-outcomes.png)

**Workflow figure.** Six cases per controller: the generated controller and authored reference pass all six; the authored stale control passes four. These are bounded deterministic workflows, not fresh model reasoning at every step.

## Matched selection on a common pool

The frozen pool contains the authored parent and both generated repairs. Every candidate received six selection slots per method and the same two unchanged-footprint regression controls. Eligibility requires no regression relative to the parent; ranking uses verified completion, then incremental API cost, then candidate ID. Parent retention is allowed. All three methods selected repair 00.

| Selector | Six selection slots per candidate |
| --- | --- |
| Source-only | Source identity repeated six times |
| Generic | Identity, consistent renaming and irrelevant observations, twice each |
| Failure-family | Identity, renaming, noise, compaction, handoff and cached evidence |

Repeated deterministic inputs equalize slots, not independent model samples. The 60 development trials and unfavorable lack of repair diversity remain preserved.

## Controlled transfer amendment C1

The exhausted allowance was not reset. C1 narrowed the next experiment to unchanged cached policies on three separately authored templates: text normalization, discounted integer-cent totals and blocked-node graph reachability. Each has a source repair after weak passing tests, a configuration change after verification, and an unrelated-documentation control: nine cases total. Templates differ from clamp, while the provenance interface and failure mechanism remain shared.

Before executing any new case, all development traces were replayed and selector decisions recomputed. The plan froze programs, decisions, templates, contract, analysis, dependencies, runtime/image, limits and retry rules. Commit **7ae8dd0** was pushed privately before outcomes existed. The three candidates and a nonselectable authored rerun reference produce 36 trials. Reservations precede execution; completed trials are replayed on resume, and interrupted unknown trials cannot silently resample. All declared slots are required; unreconciled infrastructure prevents comparison.

The paired unit is the **one source pool**. The three templates are not three generation pools. Cases receive equal weights; no interval is reported with this sample size. The same implementer authored both splits, so separation is procedural, not human blinding.

<!-- page -->

# 4. Controlled transfer results

| Policy | Verified / cases | Functional | Fresh | Refusals |
| --- | ---: | ---: | ---: | ---: |
| Authored parent | 3 / 9 | 9 / 9 | 3 / 9 | 0 |
| Generated repair 00 | 9 / 9 | 9 / 9 | 9 / 9 | 0 |
| Generated repair 01 | 9 / 9 | 9 / 9 | 9 / 9 | 0 |
| Authored rerun reference | 9 / 9 | 9 / 9 | 9 / 9 | 0 |

![Controlled transfer: one source pool](figures/controlled-transfer-012/controlled-transfer.png)

**Figure 1.** Each template contributes two freshness-sensitive cases and one unchanged control. The reference is authored and not selectable. Counts describe this fixed controlled suite, not population rates.

Both repairs reached the ceiling. Source-only, generic and failure-family selection had all chosen repair 00 before audit execution. Failure-family minus either baseline is therefore **0 percentage points**. Equal outcomes do not establish equivalence, and the identical selected ID prevents this pool from identifying selection value.

The parent's six failures separate correctness from evidence: the authored implementations passed functional checks, but completion reused old visible receipts. In the text case, repair 00 instead verified the changed implementation before completing. In a documentation control it completed immediately with a still-current receipt. Each generated repair requested six fresh verifications; the authored rerun reference requested nine. Including setup, those are 15 versus 18 visible executions, a local tool-count observation rather than a realistic efficiency estimate.

All 36 trials were retained, with no retries, exclusions or infrastructure-inconclusive slots. They used 57 completed Docker workers, 59.54 summed worker seconds and confirmed cleanup. Each trace replayed before normalization. No additional inference was used. The result supports narrow completion-policy transfer after authored repairs; it does not support a mechanism-guided selector advantage.

<!-- page -->

# 5. Grounded result-attribution case

## Existing scheduler behavior, a separate endpoint

The upstream diagnostic uses unchanged ShinkaEvolve code at revision **8adc053a2ce4511ad2ac310e004c530a73fb974a**. Fixed authored evaluators submit actual local jobs. A prior job publishes score 1 and correctness true; a changed request then reuses or replaces the result directory. The endpoint is valid attribution to the current request, not coding-agent verified completion.

| Authored scenario | Observed scheduler result | Attribution |
| --- | --- | --- |
| Exit 7; reuse old directory | Prior success and score 1 | Stale |
| Exit 7; fresh directory | No prior success available | Rejected |
| Exit 0; no publication; reuse | Prior success and score 1 | Stale |
| Metrics only; reuse | New score 0.25 plus old correctness | Mixed |
| Complete publication; reuse | New success and score 0.25 | Current |
| Complete publication; fresh | New success and score 0.25 | Current |

![Source attribution and attempt-bound adapter](figures/upstream-004/publication-qualification.png)

**Publication figure.** The pinned source diagnostic and four current authored adapter checks use distinct result-attribution endpoints. Broader twenty-case qualification is reported separately below.

Result files are loaded independently and lack an attempt binding at this public scheduler boundary. A return-code-only guard would address exit 7 but miss zero-exit nonpublication and partial publication. The scenarios demonstrate mechanism-level counterexamples to a narrow guard; they are not model-generated repair comparisons.

Three of six deliberately selected scenarios violated the attribution contract. This is not a prevalence estimate, an observed model reasoning error, a security exploit, or evidence that published Sakana results are invalid. Normal exclusive proposal directories reduce exposure. Full native evolution, restart reachability and database promotion were not reproduced. Source copies, hashes and license attribution are preserved.

## Authored attempt-bound adapter

The local adapter creates a fresh attempt directory and binds a host receipt to request identity, declared input hashes, runtime, exact launch-command hash, actual process status and complete publication artifacts. It rejects nonzero, absent, partial, malformed, changed-input and tampered evidence. A complete negative evaluation can remain valid evidence; validity and correctness are distinct.

Four real scheduler checks matched their contracts. A broader fixed qualification added 20 authored cases spanning positive/negative results, publication ordering, invalid score types/duplicate keys, input changes and absent output, across two layouts. All 20 contracts matched and all ten renamed pairs preserved verdicts. These are qualification cases from an authored producer, not independent source pools or an audit of model agents.

The adapter is a local proof of concept, not an upstream merged fix or a sandbox for arbitrary evaluators. Before/after hashing cannot prove the absence of transient changes that are restored, and undeclared inputs remain outside the guarantee. This diagnostic motivates stronger acceptance contracts but does not turn the null selector result into a positive one.

<!-- page -->

# 6. Interpretation, resources and conclusion

## What the evidence supports

The prototype can separate functional failure, stale evidence, refusal and infrastructure uncertainty; execute cached generated policies in isolation; preserve candidate ancestry and all attempts; and freeze/replay a complete selection-to-audit chain. The controlled audit shows that the two generated policies transfer across these small authored templates. The pinned scheduler diagnostic demonstrates an existing public-API attribution behavior under specified fault/reuse conditions, and the authored adapter qualifies one concrete remedy.

**The original selection hypothesis remains inconclusive.** Explicit fingerprints make the completion decision easy, both repairs reach the ceiling, and every selector chooses the same candidate. Neither more deterministic repetitions nor relabeling authored controls as generated repairs would resolve this limitation. No source-conditioned native-agent pool with useful behavioral variation was obtained within the allowance.

## Limits and conditions for a larger study

The pilot has one authored source, one model backbone and generated programs making deterministic actions. Fixtures, repairs to task implementations and audit templates are authored. It lacks natural semantic source failures, live model reasoning per tool step, multiple real repositories, independent human diagnosis, long-run evolution and a complete native Sakana run. Strong functional oracles here do not solve test adequacy in realistic projects. The recorded audit is now opened and cannot be reused for tuning while retaining a held-out claim.

A larger study would need a separately bounded discovery/generation allowance, realistic qualified source failures, unchanged common repair pools, all three matched selectors and a new audit sealed before selection. Generation failures and unsuccessful candidates must remain; no positive result is required. This is future work, not silently completed work or additional spending authorization.

## Resource and reproducibility accounting

| Stage | Recorded resource |
| --- | --- |
| All experimental inference | 3 Codex subscription calls; no separately billed API calls |
| Reported tokens | 27,232 input; 2,458 output; reasoning field recorded separately |
| Subscription dollar cost | Unavailable, not zero |
| Stateful workflow | 18 trials; 152 workers; 109.13 worker seconds |
| C1 controlled audit | 36 trials; 57 workers; 59.54 worker seconds |
| Retained replay coverage | 179 coding traces; 28 publication receipts |

Worker sums exclude orchestration/fixture/analysis time. Original infrastructure-inconclusive attempts remain. Offline tests and clean noneditable wheel reproduction validate implementation; they are not independent scientific replications. Exact package versions, image digest, upstream revision, input/output/code hashes, scripts and recorded evidence accompany the private repository.

**Conclusion.** This completed pilot delivers a reproducible QA apparatus and a concrete result-attribution diagnostic. Its central comparison found no observed selector advantage. The appropriate next scientific question is whether mechanism-directed selection adds value on realistic, behaviorally diverse agent repairs; the present evidence does not answer it.

<!-- page -->

# References

Primary sources checked 2 November 2026. Versioned papers are cited where available. This is a targeted review; no exhaustive novelty certification is claimed.

[1] Lu et al. **Towards end-to-end automation of AI research.** Nature 651, 914-919 (2026). [Version of record](https://www.nature.com/articles/s41586-026-10265-5); [open full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC13017497/).

[2] Zhang et al. **Darwin Godel Machine: Open-Ended Evolution of Self-Improving Agents.** arXiv:2505.22954v3. [Paper](https://arxiv.org/html/2505.22954v3).

[3] Lange, Imajuku and Cetin. **ShinkaEvolve: Towards Open-Ended And Sample-Efficient Program Evolution.** arXiv:2509.19349v1. [Paper](https://arxiv.org/html/2509.19349v1).

[4] **AgentAssay: Token-Efficient Regression Testing for Non-Deterministic AI Agent Workflows.** Technical report, arXiv:2603.02601v1, section 6.1. [Paper](https://arxiv.org/html/2603.02601v1).

[5] Guo et al. **SyncMind: Measuring Agent Out-of-Sync Recovery in Collaborative Software Engineering.** arXiv:2502.06994v2. [Paper](https://arxiv.org/html/2502.06994v2).

[6] Tan et al. **Benchmarking Coding Agents When Users Touch the Code.** arXiv:2608.02499v1. [Paper](https://arxiv.org/html/2608.02499v1).

[7] Chen et al. **From Failed Trajectories to Reliable LLM Agents: Diagnosing and Repairing Harness Flaws.** arXiv:2606.06324v2. [Paper](https://arxiv.org/html/2606.06324v2).

[8] Zhang et al. **Self-Harness: Harnesses That Improve Themselves.** arXiv:2606.09498v3. [Paper](https://arxiv.org/html/2606.09498v3).

[9] He. **Does Failure Feedback Direct Agent Self-Modification?** arXiv:2610.14662v1. [Paper](https://arxiv.org/html/2610.14662v1).

[10] Sakana AI. **AI-Scientist-v3 usage guide.** Source-evidence consistency and review handling; accessed 2 November 2026. [Official documentation](https://github.com/SakanaAI/AI-Scientist-v3/blob/main/docs/usage.md).

## Implementation source and attribution

The grounded diagnostic preserves unmodified relevant files from the official [ShinkaEvolve repository](https://github.com/SakanaAI/ShinkaEvolve) at the exact revision in section 5. The Apache license and file-level hashes are included under `evidence/upstream-source-006/upstream-source/` and `third_party/`. No upstream code was changed or submitted.

## AI assistance disclosure

James Tu supplied research direction and resource constraints. Codex implemented the prototype, orchestrated experiments, analyzed records and assisted report writing. The three experimental inference calls are separately logged; ordinary coding/report work is not misreported as additional experimental subjects. No independent human review, external submission or peer review is claimed.

<!-- page -->

# Appendix: audit and artifact map

## Frozen identities

C1 plan hash:

```
fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3
```

Candidate-pool hash:

```
3984309eae4921b0679c4807a2ed56b584193b498e11defaf228baa4a5d7c34e
```

Freeze commit `7ae8dd0` contains the plan and snapshots but no audit trials. It was pushed before execution. Candidate generation predates template authorship. All methods selected repair 00 before opening outcomes. Current manifests preserve historical snapshots rather than pretending subsequent code changes were part of an earlier freeze.

## Generated repair 00, unchanged

```
def choose_action(observation):
    evidence = observation.get('evidence') or {}
    current = observation.get('current_fingerprint')
    if (current and evidence.get('fingerprint') == current
            and evidence.get('status') == 'passed'):
        return 'complete'
    return 'verify'
```

## Reproduction entry points

```
agentqa verify-evidence --root .
python -m pytest
python scripts/build_repro_bundle.py --output dist/my-reproduction.zip
```

These commands verify saved evidence and package files; the tests use authored fixtures. No new inference is required. Docker is needed for new generated-program execution, not saved replay. The lifetime experimental allowance is exhausted; cloning or deleting a ledger does not reset it. Exact CLI/environment setup is in `docs/reproduction.md`.

| Artifact | Repository path |
| --- | --- |
| Controlled plan, snapshots, full grid | `evidence/controlled-transfer-012/` |
| Development selection and frozen pool | `evidence/development-comparison-001/` |
| Source diagnostic and adapter checks | `evidence/upstream-source-006/`, `evidence/bound-shinka-008/` |
| Broader publication qualification | `evidence/publication-qualification-011/` |
| Measured figures, CSV and tables | `report/figures/` |
| Final recorded demonstration | `report/demo-final/index.html` |
| Full procedure and accounting | `docs/reproduction.md`, `docs/budget.md` |

Private repository: [JamesTu-jtjt/agentqa](https://github.com/JamesTu-jtjt/agentqa). The original native-agent main study remains unperformed.
