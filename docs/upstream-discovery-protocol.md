# Upstream source qualification, before execution

2 November 2026, declared before `scripts/probe_shinka_results.py` runs. One bounded six-case test of the already pinned, unchanged ShinkaEvolve scheduler (`8adc053a2ce4511ad2ac310e004c530a73fb974a`). No model calls, no private traces, no production job or remote write. All evaluator/program fixtures are authored. The local public scheduler API is the experimental subject; it is not a recorded LLM mistake.

## Hypothesis and limits

Code inspection of `shinka/launch/local.py:monitor` shows that it reads the process return code but loads result JSON regardless of the value. `load_results` reads existing `metrics.json` and `correct.json`, with no request/source identity. Submission creates its output directory with `exist_ok=True` and replaces logs but does not clear old result JSON. Hypothesis: reusing a result directory after changing an evaluation input can attribute an old or mixed result to a new failed evaluation.

This is an API-level reliability hypothesis under explicit result-directory reuse. We do not yet know whether Shinka's normal high-level evolution runner reaches it, whether fresh generation directories prevent it, or whether any published result is affected. Do not describe the result as a security exploit, reward hacking, an observed model failure, or evidence against a Sakana paper.

## Fixed six-case search

The authored evaluator reads a JSON request from `program_path`. In successful mode it publishes a score and correctness result. Other modes terminate before publication, exit zero without publication, or publish only metrics. Reused cases first execute a successful original request, then change the request. Every original result/log is copied before reuse; failures are preserved. There is no injected change to upstream code.

| Case | Output directory | Changed request behavior | Expected correctness attribution |
| --- | --- | --- | --- |
| nonzero-reused | Primed with real success | Exit 7, publish nothing | Reject old result for the new request. |
| nonzero-fresh | Fresh | Exit 7, publish nothing | Reject; counterfactual for prior-result dependence. |
| zero-no-publication | Primed | Exit 0, publish nothing | Reject; zero exit alone is insufficient. |
| partial-publication | Primed | Publish new metrics only | Reject mixed-attempt bundle. |
| normal-publication | Primed | Publish both files | Accept new result. |
| normal-fresh | Fresh | Publish both files | Accept; fresh-directory control. |

The per-request publication requirement operationalizes the claim returned by this scheduler call. It is a different interface contract from the existing deterministic content-restoration contract: an explicit cache hit bound to the exact same full request could be valid, but this test changes the request and the upstream files contain no such binding.

Record actual subprocess exit status, prior/current program hashes, both JSON artifact hashes, returned result, fixed revision, upstream source hashes, evaluator code, timing, and all logs. Stop after six cases, regardless of outcome. A failure to prime is an apparatus error and stops the probe; it is not a semantic counterexample.

## Decision after the search

If the hypothesis is confirmed, qualify it as an existing harness defect exposed by deterministic process-failure/reuse conditions. Derive test families and counterfactuals from the verified mechanism. Keep an authored repair-pool qualification study separate from claims about model-generated repairs. Before opening any new audit, freeze its cases, contract, candidate origins, selection rules and analysis. If the hypothesis is not confirmed, preserve that result; do not expand the source search indefinitely.
