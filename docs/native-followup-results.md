# Native follow-up results: N1 and N2

2 November 2026. Both prospectively frozen, deterministic studies completed. No additional experimental model calls were used; the lifetime allowance remains 3/3 consumed. No cell was retried or excluded.

## Native consequences

N1 freeze commit `1c6a88d`, plan `fc55f4e1c1ada0c79ce61bc7ebc33ff03f2b170bd3592d7804c68e486d7ce139`. All 56 target cells and 49 primers were executed: 105 evaluator processes, including seven deliberate interrupted primers. Actual `ShinkaEvolveRunner.run()` used supplied authored seeds, one generation and one island; no model proposals, embeddings or external service calls. Upstream source remained unchanged at `8adc053a2ce4511ad2ac310e004c530a73fb974a`, also verified as public main at the time of the check.

Both completed-generation-zero restart and interruption-before-first-insert retry admitted all five authored invalid target attempts as correct, to the actual archive and best tracking. A fresh run admitted two independent schema/status conditions. These are fixed fault-injection cases, not prevalence estimates or a sampled evolutionary trajectory.

| Defense on completed-generation-zero restarts | Invalid targets stored correct / 5 | Positive preserved | Negative score preserved |
| --- | ---: | ---: | ---: |
| Upstream | 5/5 | 1/1 | 1/1 |
| Exit only | 3/5 | 1/1 | 1/1 |
| Schema only | 5/5 | 1/1 | 1/1 |
| Fresh directory only | 2/5 | 1/1 | 1/1 |
| Fresh + exit + schema | 0/5 | 1/1 | 1/1 |
| Bound receipts | 0/5 | 1/1 | 1/1 |

All five original invalid restart targets were archived and tracked as best. Fresh-only archived two invalid targets, one tracked as best. The combined guard and receipts archived none. The combined guard matches receipts on this endpoint; no accuracy gain for receipts is established. The strict contract requires zero exit even if a result was written before a later crash; different durable-commit contracts could make different choices on that one condition.

Evidence: `evidence/native-initialization-013/{plan,outcomes,analysis,file-manifest}.json`, actual databases and WALs under `cells/`, native figure/table under `report/figures/native-initialization-013/`. Replay excludes volatile SQLite shared-memory coordination files and reads temporary database/WAL copies; the original manifest and explicit amendment remain in `docs/native-replay-amendment.md` and `evidence/native-replay-amendment-013.json`. Durable hashes/outcomes were unchanged, and no experiment was rerun to repair verification.

## Standard helper and prior repair

Public [Shinka PR #150](https://github.com/SakanaAI/ShinkaEvolve/pull/150) already discusses related resume detection and crash consistency. It is closed and unmerged. We credit the exact helper from head `7f6b67e20cd44821dd9d7df0d15d5905cefe43d8`; this is not our invention. N2 freeze commit `9799639`, plan `dac6db34c9369be3610d48fe4f26e54d7276a4ac626dc2e5694405cf1f5735c0`.

N2 completed 24 target cells and 24 successful primers through the actual standard helpers and local scheduler. The main helper with a raw consumer accepted four invalid attempts. The proposed helper accepted zero of two inside-helper failures, but two of two failures before helper entry. Both helpers with the simple combined consumer guard accepted zero invalid attempts and retained both valid controls. The proposed helper still returns old metrics with correctness false after its internal abrupt-exit cases; rejection is not proof of fresh metrics. The complete PR and its native resume/shutdown changes were not evaluated.

Evidence: `evidence/standard-wrapper-014/`, exact helper sources/license, actual process records/result files, public prior-art metadata `evidence/shinka-pr150-prior-art.json`, and `report/figures/standard-wrapper-014/verification.json`.

## Scientific interpretation

This follow-up adds actual initialization/database consequences, credible simple baselines and a real prior repair's applicability boundary. It strengthens a bounded QA case study at a self-improvement feedback boundary. It does not establish a new cache-invalidation principle, first harness-testing method, natural failure rate, complete-PR defect, autonomous scientific harm or improved selection among model-generated repairs. The original selector result remains zero observed difference with one easy source pool. More generated pools still require a separately revised inference allowance and a new sealed audit.
