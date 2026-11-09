# Research scope

AgentQA contains three completed, bounded studies: native initialization/restart and defense experiments (N1), a standard-helper repair-boundary comparison (N2), and a controlled repair-transfer pilot (C1).

The main finding is that evaluation-attempt identity, process status, and output completeness jointly determine whether evaluation evidence is valid for a changed program. Fresh attempt directories plus exit and schema checks prevented every tested invalid acceptance while preserving both valid controls.

The original repair-selection hypothesis remains unresolved. Both generated repairs passed all nine C1 cases, and all selectors chose the same repair. The pool therefore does not distinguish selector effectiveness. Future work requires behaviorally diverse repairs and a new held-out evaluation set.

The protocols and frozen snapshots describe historical experiments. Their plans, failed attempts, model usage, outcomes, and source hashes remain part of the research record. A successful replay validates consistency with that record; it does not establish natural failure incidence or long-run search improvements.

See [results](native-followup-results.md), [reproduction](reproduction.md), and the [report](../report/final-report.md).
