# Candidate, suite, and split specification

Development specification, 2 November 2026. Final audit registration remains pending.

Later amendment C1 adds a separate frozen runner and a completed controlled template-transfer pilot; see `controlled-audit-protocol.md` and `checkpoint-090.md`. The existing development runner still rejects audit phases. The original broader native-agent main-study registration remains pending.

## Candidates and generation attempts

`CandidateRegistry` stores immutable program text/hash, a candidate ID, parent ID, source hash, origin, and provenance. Origin distinguishes authored controls, model-generated repairs, and unseeded model policies. A parent must already exist before a child is added. Program size is bounded; candidate code is never imported by the registry.

Generation attempts are separate records, with pending/completed/invalid/failed/timeout status. A pending attempt can be finalized only once. Failed attempts are retained and included in the pool freeze. A pool cannot freeze while an applicable generation attempt is pending. Duplicate candidate/attempt/pool identities cannot silently replace earlier records.

A pool manifest includes the parent, candidate texts and hashes, relevant attempt records, and a canonical content hash. A source-conditioned pool includes one source identity and its ancestry. Database triggers prevent accidental update/deletion of frozen candidate/pool records. These controls detect accidental mutation; an attacker with complete database/file access is outside the threat model.

The first pool imports the existing pilot retrospectively, with that fact explicit in provenance: one authored always-complete parent and two repairs from generation call `generation-001`. Its manifest freezes **before** the new matched comparison. This is not a prospective registration of the earlier pilot.

## Matched development suites

Every candidate receives the same slots for each selector:

| Selector | Six selection slots |
| --- | --- |
| Source-only | Identity six times. |
| Generic | Identity, renaming, noise, repeated twice. |
| Failure-family | Identity, renaming, noise, compaction, handoff, cache. |

The two common regression cases are unchanged-footprint controls with the original and renamed layouts. No task is selected using only a favorable subset of candidate outcomes. All candidates include the same parent option and the same eligibility/tie rule.

Repeated identical pure-policy inputs are budget controls, not independent scenario discoveries or estimates of model sampling variance. Candidate generation incurs subscription usage once; evaluation of the resulting pure policies incurs no inference calls. API-dollar tie costs for these local trials are zero incremental API usage, while shared generation subscription dollar cost is unavailable. Tool counts/runtime are reported separately.

The comparison plan records candidate IDs/pool hash, source-code hash, full slot definitions, retry policy, and a canonical hash. It is frozen to disk before execution. A resumed run refuses changed code/pools/slots. Each logical trial has a unique identity and an external trace. Completed trials are replay-validated and reused; an interrupted trial without a completed result requires reconciliation rather than silent resampling. Infrastructure failures stop selector computation instead of counting as semantic agent failures.

## Independent audit requirements

The current runner explicitly rejects an audit phase. Its development results cannot be relabeled as held-out transfer.

Before an audit runner is enabled, the final manifest must identify separately authored repository/template families, immutable case definitions/hashes, membership, and model/editor access policy. Sibling variants of a single template may not be split randomly into development and audit. Semantic-template overlap must be reviewed in addition to checking IDs/hashes.

Record selected candidate IDs before opening audit outcomes. Neither candidate generation nor transformation tuning may use those outcomes. A single implementer authors both sides, so the study has procedural separation and no claim of human blinding. Contaminated cases become development data; a replacement audit or an exploratory label is required.

## Current scope

The implemented ShinkaEvolve bridge supports pure `choose_action` policy programs at an external evaluation boundary. It does not yet support arbitrary editable multi-module coding harnesses or run the complete ShinkaEvolve evolution loop. The real upstream scheduler has been exercised with an existing candidate and the isolated evaluator; that is the integration claim supported by evidence.
