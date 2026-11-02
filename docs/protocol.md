# Development protocol: fresh verification evidence

Version: `fresh-content.v1`, 2 November 2026. This is the **development** contract, not the final experiment freeze. Current evidence comes from authored controls; no natural-failure search or live candidate generation has run.

## Executable task and footprint

The initial fixture implements a configurable clamp function. Visible checks cover negative and ordinary inputs; independent evaluator checks also cover the upper bound. The source task starts with a passing visible test on an incomplete implementation, followed by an authored correct edit. Completion after that edit must have fresh passing visible verification and pass the independent functional checks.

The footprint includes the declared module, visible test script, and configuration; sorted path-to-byte hashes; contract version; Python implementation/version; and a declaration of stdlib-only dependencies. The fixture uses fixed inputs and configuration. Unlisted files are outside this bounded dependency model. This is not dependency discovery for arbitrary repositories.

**Content identity is the contract.** Exact restoration of all footprint bytes under the same fixed environment permits reuse of an earlier passing result in the same trial. Relevant whitespace or test/config edits change the fingerprint. An unrelated notes-file edit does not. A result from another trial is never usable. Changing dependencies/runtime requires a different identity.

## Success and failure semantics

The evaluator separately records: completion declared; functional checks passed on the final footprint; and an actual passing visible test executed on that footprint. Verified completion requires all three. Refusal, budget exhaustion, or an unsupported action is not successful completion.

Visible test stdout is diagnostic data. The trusted wrapper records process exit status and footprint before/after execution. A nonzero exit, timeout, launch error, or footprint change during execution cannot supply passing evidence. Even a visible script that prints `PASS` or exits zero does not bypass the independent functional checks. A hidden functional check never counts as agent-obtained visible verification.

A tool-level failure remains a recorded result; no automatic stochastic retry occurs in the development runner. A future live runner must freeze transport-error retries separately. Execution is capped at 30 seconds per local invocation (3 seconds by default), output stored in the trace is capped at 16 KiB, and the offline policy loop defaults to four actions. The local subprocess backend executes only trusted authored code. It is not an OS sandbox, output-resource sandbox, or secure evaluator for generated code.

## Failure families

The library supports identity, consistent renaming, bounded irrelevant observations, a compaction boundary, a handoff carrier, a cache carrier, and a matched no-invalidation control. All contexts retain an explicit means to recover evidence provenance and current state. Compaction currently uses an authored observation transformation, not a real model-generated summary.

The validator checks source identity, exact allowed transformation structure, actual prior/current fingerprint relationship, fixture execution, and successful completion by an always-rerun reference. It rejects malformed or unsupported transformations. The generic baseline draws from the same representation and validator but only uses identity, renaming, and noise. The initial demonstration uses seven cases; the implemented development comparison uses six matched slots per selector and two shared regression cases. This is a development freeze, not the final main-study/audit freeze.

The known failure mechanism is specified by the implementer. The transformations do not infer causal mechanisms from arbitrary traces or establish unrestricted semantic equivalence. A parent passing an example is not evidence of relation validity.

## Records and schema

| Record | Required identity / content | Current implementation |
| --- | --- | --- |
| Scenario | scenario/template IDs; module/test/config paths; function; invalidation, noise, carrier and compaction settings; canonical hash | Frozen `Scenario` dataclass. |
| Event | trial ID; zero-based sequence; kind; payload; previous hash; current hash | Host-owned `Recorder`; start/state/observation/test/complete. |
| Test | purpose; before/after fingerprints; process status/return code; capped diagnostic output; elapsed time | Actual local process execution. |
| Completion | declared boolean; final fingerprint; referenced functional record | Final event; subsequent mutation refused. |
| Verdict | completed, functional, fresh, verified, reason | Recomputed from event trace. |
| Family | source hash; operator; relation; transformed scenario | Frozen `FamilyCase`; executable validator. |
| Selection outcome | candidate/case/repeat; verified; contract violation; cost | Matched-slot selector with common regression gate. |
| Trial ledger | unique trial ID; metadata; reservation; terminal status; charged amount; outcome | SQLite transactions; persists across process restarts. |
| Candidate/split freeze | immutable program hash/parent lineage; generation attempt; suite membership/template hashes | Candidate registry and development pool/plan freeze implemented; independent final audit remains pending. |

Trace schema is `agentqa.trace.v1`. A SHA-256 chain detects accidental editing/reordering and can be compared with a separately frozen final hash. It **does not authenticate** a trace against an attacker able to replace the trace and manifest together. Current trust is in the evaluator/recorder process; candidate isolation remains a separate requirement. Incomplete traces return `incomplete` rather than inventing completion.

## Selection and accounting

All selectors must receive the same candidate pool and complete, matched trial slots. Eligibility requires at least the parent's verified-completion count and at most its violation count on each common regression case. Eligible candidates are ordered by selection completions, then lower selection execution cost, then candidate ID. The parent is an available option. This is an empirical rule, not a statistical guarantee.

The cost ledger stores integer micro-USD amounts. Reservations are transactional across connections. Reusing a trial ID or silently changing a cap is rejected. Unknown usage retains the reservation. Unexpected actual charges above the bound are recorded, and remaining allowance is exhausted rather than hidden. A provider must enforce the requested token limits for reservations to be reliable; this library does not supply a provider integration yet.

## Live study prerequisites

GPT-6.1 Sol is the user-selected model. James authorized saved Codex account use with low usage. The backend uses `codex exec`, exact model `gpt-6.1-sol`, a three-invocation persisted limit, serial execution, and a 120-second runtime bound. Two invocations have been used; one remains. Subscription dollar cost is unavailable. The source-conditioned repairs passed all seven initial cases; a separate unseeded-policy probe had infrastructure-inconclusive attempts and a linked diagnostic rerun. See checkpoint 2 for interpretation.

Docker Desktop was started and the pinned worker image downloaded. Generated policy code executes in that worker with no host mounts; it only returns an action to the trusted authored-fixture controller. Startup has a separate bounded allowance and readiness marker before the execution timer begins. The local fixture subprocess backend remains restricted to authored code. A real ShinkaEvolve scheduler has exercised the external evaluator for pure policies; arbitrary multi-module harness evolution is not implemented.

Before the main study: validate candidate isolation; identify natural source failures or declare a controlled-study fallback; freeze candidate and split registries; match selection budgets; prewrite analysis; reserve sufficient audit budget; and prevent audit feedback from reaching generation. Same-author fixture design must not be described as human blinding.
