# Methods reading and implications for AgentQA

Updated 2 November 2026. This is a targeted methods review supporting implementation; no claim of exhaustive novelty certification.

| Work | Method detail checked | Implication for this project |
| --- | --- | --- |
| [AI Scientist Nature publication](https://www.nature.com/articles/s41586-026-10265-5), [author overview](https://sakana.ai/ai-scientist-nature/) | Research lifecycle from ideas through execution, analysis, manuscript and review; template-based and tree-search settings. The version of record was accessed through the [PMC full-text mirror](https://pmc.ncbi.nlm.nih.gov/articles/PMC13017497/), including staged experimentation, execution/plot validation and manuscript generation methods; Nature itself redirected to an identity-cookie endpoint. | Scientific output quality depends on execution evidence. Our prototype targets a narrow verification obligation rather than claiming to validate an entire research paper. |
| [DGM, section 3 and pseudocode](https://arxiv.org/html/2505.22954v3) | Retains an archive, proposes agent modifications, and evaluates coding capabilities empirically. | Preserve ancestry and rejected/failed attempts. A one-step fixed-pool selection comparison cannot establish long-run open-ended improvement. |
| [ShinkaEvolve, sections 3.1–3.3](https://arxiv.org/html/2509.19349v1) | Archive sampling, code mutations within editable boundaries, novelty assessment, execution feedback and scalar fitness. | We implement an external evaluator with behavioral fitness and retain detailed trace feedback. We are not proposing a new parent sampler or novelty algorithm. |
| [Digital Red Queen, section 3](https://arxiv.org/html/2601.03335v1) | New warriors optimize against the previous lineage; MAP-Elites preserves behavioral diversity under changing competitive pressure. | Historical cases may be useful reliability pressures, but the current prototype uses fixed requirements and does not implement coevolution or a moving oracle. |
| [Agentic Scientist](https://pub.sakana.ai/agentic-scientist/) | Coordinates coding agents around an evidence-grounded workflow; authors describe limitations in generated ideas and implementations. | Trace provenance and executable validation are relevant to the research workflow; fitting this theme does not by itself establish novelty. |
| [HarnessFix, III-C–D](https://arxiv.org/html/2606.06324v2) | Repair specifications bind concrete editable resources and required behavior; validation checks target improvement and regressions and preserves repair memory. | A trace-guided repair specification or regression gate alone is already established. AgentQA must demonstrate the added value of validated failure-family construction. |
| [Self-Harness, 3.2–3.4](https://arxiv.org/html/2606.09498v3) | Generates scoped mechanism-specific branches; promotion uses pass counts on evidence-visible and proposer-hidden tasks, rejecting split-wise degradation. | Separate evidence visible to a proposer from data used for acceptance. An independent final audit must remain outside both tuning and candidate selection. |
| [Failure-feedback study](https://arxiv.org/html/2610.14662v1) | Distinguishes directed repair, transfer and net held-out improvement; candidate quality and screening effects are separate. | Report all candidates and selectors on a common pool; source repair alone cannot justify a generalization claim. |
| [AgentAssay, 6.1](https://arxiv.org/html/2603.02601v1) | Agent metamorphic relations and cross-version violation-rate comparisons. | Do not claim first agent MT or first MR-based regression detection. Use a matched generic baseline to test the contribution. |

## Working contribution and current evidence

The proposed contribution remains failure-conditioned construction of valid metamorphic families and evidence that they improve repair selection. The initial model-generated repairs and a neutral unseeded policy use explicit provenance successfully. This narrows what can be inferred from the simple fixture; an authored narrow reminder control is not a substitute for diverse naturally failing agent modifications.

The unseeded probe returned four verified completions and three worker-timeout/infrastructure-inconclusive executions. Inspection of the immutable program and worker records does not substantiate a semantic freshness failure. Startup time must be measured separately from policy execution before interpreting those attempts.

The current ShinkaEvolve claim is a real pinned scheduler/evaluator integration with isolated pure policy execution. The whole evolutionary loop, multiple real repositories, and a final independent audit have not been reproduced.

## Remaining review

The Nature-paper main methods have now been checked through PMC. Supplementary analyses and broader original repository interfaces can be examined as needed for the final submission. Keep version-of-record versus preprint distinctions and concrete source links in the report. Any new novelty claim needs an updated search, especially around stateful agent testing and repair transfer.

## 70% checkpoint: closer state-awareness work

[SWE-Touch](https://arxiv.org/html/2608.02499v1), sections 3–5, constructs validated conflicting user edits near task-critical code and injects them during coding-agent execution. It measures how agents recover and re-verify. Thus our handoff/configuration-change workload is a diagnostic vehicle, not a new shared-workspace benchmark contribution. The remaining proposed distinction is **selection among repairs using mechanism-directed valid families**, with matched generic/source-only baselines; that claim still needs evidence.

[SyncMind / SyncBench](https://arxiv.org/html/2502.06994v2), sections 2–3, studies agent recovery from evolving repository states with executable verification. State awareness and recovery are established research topics. Our explicit execution-evidence contract and result-attribution case narrow the property being tested; they do not justify a first-in-field claim.

The [Agentic Scientist usage guide](https://github.com/SakanaAI/AI-Scientist-v3/blob/main/docs/usage.md) already describes source-evidence/snapshot consistency checks and clearing stale review aliases. Provenance checks alone are therefore not a novel architectural contribution. The newly reproduced Shinka scheduler API behavior is a concrete QA case at a pinned revision, not evidence that all Sakana systems lack provenance enforcement. No benchmark reproduction or complete native agent experiment was run for this reading update.
