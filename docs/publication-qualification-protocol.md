# Broader publication qualification, declared before execution

2 November 2026. Twenty authored development cases, fixed before `scripts/qualify_publication.py` executes. This does not open or substitute for the proposed independent agent-repair audit. No new model call, generated candidate, native evolution run or remote action is implied.

Ten modes each run in two layouts: ordinary relative names and nested paths containing spaces with renamed request/config/evaluator files. Both use the same pinned, unchanged Shinka local scheduler and the existing host-bound adapter. Renaming should preserve the verdict, including valid negative results. Both layouts are development counterparts; they are not statistically independent source pools.

| Mode | Required outcome |
| --- | --- |
| Complete positive publication | Valid, reported correctness true, score 2.5. |
| Complete negative publication | Valid, reported correctness false, score -.5. |
| Nonzero exit after complete publication | Invalid execution evidence. |
| Metrics only | Invalid incomplete bundle. |
| Correctness only | Invalid incomplete bundle. |
| Boolean score | Invalid score schema. |
| Duplicate JSON score key | Invalid ambiguous JSON. |
| Program input changed during execution | Invalid input identity. |
| Separately declared configuration changed during execution | Invalid input identity. |
| Zero exit without publication | Invalid incomplete bundle. |

Every case starts in a new directory with fresh input/config files. The evaluator is fixed authored code; generated code remains confined to Docker elsewhere. Each case gets one actual scheduler process and a ten-second bound. There are exactly twenty allowed processes, no retry and no replacement. All outcomes, including unexpected outcomes, are retained. The plan hashes cases, publisher, code snapshot and upstream revision before execution.

After the run, recheck every request/receipt against saved hashes and validate all ten renaming pairs. A failed invariant is reported, not repaired by removing a case. The outcome is API/publication qualification, not a natural-failure rate or evidence that a repair selector improves model agents.
