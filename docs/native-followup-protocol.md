# N1: native initialization reachability and minimal defenses

2 November 2026. Declared before new native executions. This bounded follow-up uses **zero inference calls**; the original three-call allowance remains exhausted. It does not reopen C1 or manufacture generated repair diversity.

## Question and scope

Can retained evaluation output affect the actual initialization, database, archive or best-program state of the unchanged pinned Shinka runner? Which simple defense suffices for this bounded mechanism? The subject is ShinkaEvolve revision `8adc053a2ce4511ad2ac310e004c530a73fb974a`, not current upstream generally. Programs, evaluator failures and interruptions are authored. No natural incidence, model failure, repair-selector improvement or long-run scientific harm is inferred.

Use `ShinkaEvolveRunner.run()` with a supplied Python initial program, one total generation, one island, local scheduler, no models/embeddings/novelty/meta/prompt evolution/W&B, offline pricing and blocked Internet sockets. This executes native setup, evaluation, persistence, maintenance and termination; it is not a sampled evolution trajectory. Do not patch upstream source, persistence or selection. A transparent submit observer records actual process return codes. Defense arms interpose only at the scheduler's `run` boundary and return explicit unsuccessful results rather than raising into the runner's fallback.

## Fixed native reachability grid

Seven target publication modes: nonzero without output; zero without output; metrics only with zero exit; correctness only with zero exit; complete output followed by exit 7; complete positive output; complete negative output. The same authored target program is used for a mode across conditions. Complete targets return score .9; a positive primer returns score .1.

Three histories, seven targets each:

1. **Fresh:** no prior run or retained result files.
2. **Completed generation zero:** execute a complete one-generation run, then restart the same results directory with a changed initial program. Native code determines resume behavior; no database rows are edited or deleted.
3. **Interrupted initialization:** the primer evaluator publishes complete output and a marker, then blocks. The external controller terminates the entire worker process group before native initialization can insert its program. Preserve the empty initialized database and result files. Restart with the changed target program. Check the database has zero programs immediately after interruption; otherwise stop as an apparatus failure.

The interruption marker/block is an authored evaluator fixture, not a change to Shinka. The interruption is a fault injection. No evidence is claimed about the frequency of such interruptions or changed-seed retries.

## Fixed defense comparison

Use completed-generation-zero history for all seven targets and each of six policies: upstream; exit-only; schema-only; fresh-directory-only; fresh directory plus exit plus schema; attempt-bound receipts. Reuse the seven upstream/completed rows from the reachability grid; do not rerun them. Each remaining cell has its own successful native primer and native target run. Fresh directories are sibling attempt directories; prior artifacts remain preserved. Schema means the existing finite numeric score / boolean correctness / complete JSON contract, applied equally to schema-only and the combined defense. Bound receipts use the already implemented adapter, not a newly tuned candidate.

There are **56 distinct target cells**, 49 successful or interrupted primers, at most **105 evaluator subprocesses**, and no repeated stochastic samples. This is a deterministic mechanism/ablation study, not an independent repair audit. Do not present cells as independent source failures or compute confidence intervals.

## Endpoints and contract

The strict publication contract requires a successful zero-exit attempt and complete, schema-valid output from that attempt. Full publication followed by nonzero exit is invalid under this explicit contract; alternative contracts allowing committed output despite later failure are outside this study.

- Primary: current target program incorrectly stored with `correct=True` under an invalid attempt; whether that program enters the archive or becomes best.
- Positive control: complete positive target stored with correct=True and score .9.
- Negative control: complete negative target stored with correct=False and score .9, retaining useful negative evidence.
- Secondary: exact stored score/code, raw returned data, actual exit status, previous/current artifact hashes, database rows/archive/best IDs, observed model-proposal count, duration and process cleanup.

For invalid output, nonzero score retention can still be an attribution error even if the correct flag is false. Report it separately; do not collapse it into positive acceptance. A fresh directory may prevent old results while leaving independent process/schema checks necessary. Receipts may tie the simple combined defense; that would not establish an accuracy advantage for receipts.

## Integrity, resource and stopping controls

Freeze scenario definitions, adapters, analysis, tests and this protocol in a Git commit before execution. Record source hashes and a separate plan hash. Each cell has a unique durable reservation; refuse reruns or output-directory overwrite. Preserve all failures and classify incomplete infrastructure separately. A worker has 30 seconds, interruption setup 20 seconds; terminate its process group on timeout. A failed primer, missing marker, unexpected database state or attempted Internet connection stops the run and remains recorded. Repair apparatus only through an explicit amendment retaining the original attempt.

Verify every observed row from saved SQLite and execution files before analysis. Run unit boundary checks, existing regression tests and a clean installation/evidence replay. Plot native consequences and the full defense table. Update the report and its existing private Google Doc, preserving previous pilot evidence and owner-only permissions. No upstream message, issue, public release or external submission is authorized.
