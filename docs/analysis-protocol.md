# Pre-audit analysis specification

Version 1, 2 November 2026. Implementation: `src/agentqa/analysis.py`; qualification: `tests/test_analysis.py`. Tests use explicitly synthetic data. **No independent audit has been opened, no final audit plan has been registered, and this document is not a completed main-study freeze.**

**Later C1 amendment:** The original statement above records this specification's pre-audit state. At 90%, the unchanged analysis implementation was frozen before, and applied to, a completed controlled template-transfer pilot. Its plan/results are in `evidence/controlled-transfer-012/`; `docs/controlled-audit-protocol.md` defines the narrower scope. This is one authored source pool with cached generated policies, not a final native-agent main-study freeze. No audit outcome was used to change the policies or the already recorded selector decisions.

## Main question and immutable inputs

The main question remains whether failure-mechanism-directed families select model-generated repairs that transfer better than source-only and generic selection, under matched budgets. The pilot has not produced a discriminating generated pool. The new upstream case supplies realistic execution evidence, but its repair is authored and cannot establish model-repair generalization.

A final `agentqa.audit-analysis-plan.v1` manifest must include frozen source pools, parent/candidate program hashes, optional fixed references, every audit slot's case/template membership and repeat index, and the selected candidate for all three methods. It must have status `selection_frozen`, and its full canonical hash must be retained externally before audit execution. References are evaluated but cannot be selected as if generated candidates. No candidate may be replaced after selection or audit.

The eventual audit runner must replay/validate its execution records before producing normalized outcomes. The analysis module checks plan/candidate identities, exact grid completeness, duplicates, boolean types and consistency of verified completion; it does not authenticate a bare outcome supplied by an untrusted source. Missing, unknown and unreconciled infrastructure outcomes stop the primary comparison. They do not silently become task failures or exclusions. An eventual retry policy must be frozen separately and preserve every original attempt.

## Estimands and grouping

For each candidate, average repeats within each semantic case, cases within each source pool, then give source pools equal weight. The paired unit is the **source pool**, not an action, test invocation, deterministic repeat or generated patch. Report the selected candidate's verified completion alongside declared completion, functional correctness, evidence freshness, explicit refusal and stale completion (`completed and not fresh`). Refusal does not earn verified completion. Functional errors and stale evidence remain distinct.

Compute mechanism-guided minus source-only and mechanism-guided minus generic verified-completion differences within each source pool, then average those paired differences. Show every pool and raw count. The best audit candidate is a labeled **post-hoc pool ceiling**, not a selector that could have used unseen audit information.

If fewer than five independent source pools are available, withhold bootstrap intervals and report descriptive paired counts/differences only. Otherwise use 10,000 bootstrap draws of paired source-pool differences, seed 17, percentile endpoints at 2.5% and 97.5%. This is a descriptive uncertainty calculation, not a significance or representativeness claim. A fixed finite operator suite and a small number of projects limit external validity even with more pools.

## Resource accounting

Unknown subscription costs remain unknown. Report known API-dollar subtotal, number of unknown-cost trials and whether cost accounting is complete. Do not silently coerce missing cost to zero. Shared generation costs must be a separate stage-level line item; the analysis's per-trial subtotal explicitly excludes generation. Record model invocations/tokens, local worker counts, timing and failed-attempt usage separately. No new inference is permitted by this analysis plan; the three-call pilot is exhausted.

## Upstream diagnostic track

The Shinka result-publication case uses a different outcome: **correct attribution of a result to its evaluation request**. It must not be relabeled as the main coding-agent verified-completion endpoint. Its six fault/reuse scenarios, four adapter checks and any authored ablations are diagnostic qualification, not an independent audit or an empirical selector-benefit experiment.

Mechanism-derived transformations include changing process exit status without publication; replacing only one result component; changing a request while retaining an earlier bundle; and comparing a reused directory with a fresh one. Applicability requires a real prior publication, a changed request, a well-defined publisher behavior, observable event/artifact provenance and both positive and negative reference cases. A generic path rename must preserve the evaluator mapping and behavior. Cases that hide all request identity from a purportedly capable checker cannot substantiate an information-preserving robustness claim.

## Gate before the main run

Still required: a qualified source failure relevant to the chosen model-agent workflow; source-conditioned model-generated candidate pools with useful behavioral variation; separate audit producers/templates rather than sibling variants split randomly; a final budget/scope decision; frozen analysis/code/dependency/contract/split hashes; and recorded matched selection decisions before audit outcomes are available. The same implementer may author the two splits, so only procedural separation, not human blinding, is claimed.

If additional inference remains unavailable, an honest controlled qualification report or an inconclusive pilot report is possible. That would be an explicit scope amendment, not a successful test of the original main hypothesis.
