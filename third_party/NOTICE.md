# Third-party source attribution

The unmodified diagnostic source copies under `evidence/upstream-source-006/upstream-source/shinka/` originate from [SakanaAI/ShinkaEvolve](https://github.com/SakanaAI/ShinkaEvolve), revision `8adc053a2ce4511ad2ac310e004c530a73fb974a`, retrieved for the local implementation on 2 November 2026. Files: `shinka/launch/local.py`, `shinka/launch/scheduler.py`, and `shinka/utils/general.py`.

They are provided under the upstream Apache License, Version 2.0. The complete license is preserved at `evidence/upstream-source-006/upstream-source/LICENSE`. No source file was modified. The repository contains no separate upstream NOTICE file at this revision. Keep this attribution, the original source and license together when packaging these diagnostic artifacts.

The ignored `vendor/ShinkaEvolve/` checkout is an optional dependency; it is not included in the project package or copied wholesale into the reproduction evidence. AgentQA's new adapter and tests are separate project code.

N1 also preserves unchanged native runner/configuration/database/scheduler/loader files and LICENSE at the same pin under `evidence/native-initialization-013/upstream-source/`. N2 preserves the exact main-pin `shinka/core/wrap_eval.py` and the exact helper from public PR #150 head `7f6b67e20cd44821dd9d7df0d15d5905cefe43d8`, plus LICENSE, under `evidence/standard-wrapper-014/`. The latter helper and its correctness-marker invalidation are prior upstream work, not AgentQA's invention. Only the isolated helper is evaluated; the complete PR is not tested. Copies retain upstream Apache-2.0 terms; no vendored source tree was modified.
