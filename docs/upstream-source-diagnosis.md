# Grounded source case: result attribution after a failed rerun

**Later follow-up:** This original API diagnostic is preserved. N1 now reproduces native initialization/restart/interruption archive and best-state consequences; N2 tests the standard helper and a credited prior repair. See `native-followup-results.md`. Public PR #150 already discussed related resume/crash-consistency issues, so the bug class is not claimed as new. Statements below about unreproduced native reachability describe the earlier diagnostic stage.

2 November 2026. [Predeclared six-case probe](upstream-discovery-protocol.md), [actual results](../evidence/upstream-source-006/summary.json), [unchanged source and license](../evidence/upstream-source-006/upstream-source/).

## Finding and scope

At ShinkaEvolve revision `8adc053a2ce4511ad2ac310e004c530a73fb974a`, the public local scheduler API can return a successful result from a previous request when a changed evaluation reuses its output directory and fails before publishing a complete new result. This is existing upstream behavior under authored process-failure/reuse conditions. No defect was inserted into the upstream implementation. It is **not** an observed model reasoning failure, an estimate of real-world prevalence, or evidence that a published Sakana result is incorrect. We have not established whether it is fixed after this pin or previously reported.

Three local facts explain the result:

1. [`submit`](https://github.com/SakanaAI/ShinkaEvolve/blob/8adc053a2ce4511ad2ac310e004c530a73fb974a/shinka/launch/local.py) creates an existing output directory and replaces log files, but leaves prior result JSON in place.
2. `monitor` observes process completion/return code and then calls `load_results` irrespective of the exit status.
3. [`load_results`](https://github.com/SakanaAI/ShinkaEvolve/blob/8adc053a2ce4511ad2ac310e004c530a73fb974a/shinka/utils/general.py) loads metrics and correctness files independently without request or attempt identity.

The checked-out upstream tree was clean before execution. Source copies and hashes are preserved with the probe. Apache-2.0 attribution is in `third_party/NOTICE.md` and the copied license. Nothing was published or sent upstream.

## Measured outcomes

| Authored process condition | Exit | Expected attribution | Scheduler result |
| --- | ---: | --- | --- |
| Changed request, reused directory, no publication | 7 | Reject old bundle | **Old success**, score 1 |
| Same failure mode, fresh directory | 7 | Reject | Rejected |
| Changed request, reused directory, no publication | 0 | Reject old bundle | **Old success**, score 1 |
| Changed request, reused directory, metrics only | 0 | Reject mixed bundle | **New score .25 + old success flag** |
| Changed request, reused directory, both files | 0 | Accept | New success, score .25 |
| Changed request, fresh directory, both files | 0 | Accept | New success, score .25 |

There are three false attributions in six deliberately chosen diagnostic cases. This fraction is a test qualification result, not a population failure rate. Original successful executions really wrote the prior files; no fabricated success string or timestamp was used. Prior/current program hashes differ in reused cases. In the two no-publication cases, both old JSON hashes remain unchanged. In the partial-publication case, only the metrics hash changes. All logs and original priming outputs remain on disk.

The fresh-directory failure is a counterfactual supporting dependence on retained result files. The zero-exit case falsifies an exit-status-only repair. The partial-publication case shows that separately valid JSON files need not belong to the same attempt. These observations support the attribution mechanism directly; no model explanation or statistical causal estimate is needed.

## Reachability boundary

The normal asynchronous proposal path creates generation directories exclusively (`async_runner.py`, `_generate_proposal_async`) and refuses an existing directory. This reduces exposure in that path. Initial-program setup instead creates generation-zero/results directories with `exist_ok=True` and rewrites the initial program. Code inspection shows a potential rerun boundary, but we have **not** reproduced a complete native evolution restart or database promotion. The supported execution claim is the public scheduler API, through both actual submission and actual result collection.

Do not generalize this result to a complete AI Scientist run, a persistent archive corruption rate, a security vulnerability, or a naturally occurring stale-evidence mistake by GPT-6.1 Sol. The earlier generated agents still have no confirmed semantic failure.

## Repair and contract

`agentqa.bundles.run_bound_job` places each attempt in a new directory; refuses overwrite; binds a host-owned receipt to full declared input hashes, runtime identity, exact launch-command hash and random attempt ID; requires a zero-exit execution and complete finite/schema-valid result JSON; checks input stability; hashes the complete result bundle; and returns validity separately from reported correctness. A legitimate negative result can be valid evidence.

The adapter invokes only fixed, authored local evaluators. Generated task/controller code remains in Docker through the existing interfaces. It is not a sandbox, a proof of functional correctness, or protection against an adversary controlling the host/receipt store. The caller must declare all relevant inputs/runtime and keep the trusted scheduler/evaluator stable. Before/after hashes do not prove that an input never changed and reverted during execution; this limitation is explicit. The adapter does not claim descendant-process containment for arbitrary external programs. An eventual untrusted evaluator needs a dedicated sandbox backend.

Saved request/receipt hashes must come from a frozen external manifest. Replaying an old bundle with its old request verifies that historical request; it does not authorize attributing that result to a new request. Exact same-request caching would need explicit provenance and is not prohibited by the general idea. This per-request result-publication contract is separate from the coding workflow's content-restoration rule.

## Review record

One Codex diagnosis pass checked three pinned source modules, six process outcomes, exit statuses and prior/current artifact hashes. No independent human review occurred; human review effort is zero. Reading/review wall time was not instrumented, so no precise elapsed review figure is claimed. The actual probe's process timings are in each result row. Automated qualification validates these facts independently of candidate descriptions. Both supporting and limiting code paths are recorded above.

The local repair is tested independently against nonzero exit, missing and partial publication, legitimate negative results, result tampering, cross-request substitution, input changes, symlinks, ambiguous/nonfinite JSON, timeout preservation, overwrite refusal and scheduler/evaluator mismatch. This qualifies a concrete QA mechanism. It does not yet establish the proposed metamorphic selector's advantage.
