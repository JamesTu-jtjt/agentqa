# Closest-work and integration checkpoint

Reviewed during implementation kickoff, 2 November 2026. This is a bounded methods/interface review, not an exhaustive novelty certification.

| Source | Checked detail | Consequence for this project |
| --- | --- | --- |
| [Failure-feedback study](https://arxiv.org/html/2610.14662v1) | Separates target repair, related transfer, and held-out change; discusses selection versus candidate quality and limitations of causal attribution. | Report all candidates as well as selected ones. Do not claim that measuring transfer is itself new. |
| [AgentAssay](https://arxiv.org/html/2603.02601v1), section 6.1 | Defines agent metamorphic relations and explicitly uses changes in relation-violation rates across versions as regression evidence. | The contribution must be validated, mechanism-directed family construction and its selection value against a matched generic baseline. |
| [ShinkaEvolve](https://github.com/SakanaAI/ShinkaEvolve) | Inspected the official circle-packing evaluator, `shinka/core/wrap_eval.py`, dependency declarations, and Apache-2.0 license. | Integrate at the external evaluation boundary; do not run arbitrary candidate imports inside our trusted recorder. |

Official ShinkaEvolve revision: `8adc053a2ce4511ad2ac310e004c530a73fb974a`. The source is in ignored `vendor/ShinkaEvolve/`, installed in the isolated `scratch/shinka-venv/` integration environment. Its actual `JobScheduler` has exercised AgentQA's external evaluator. No full evolutionary generation loop has run.

At that revision, `run_shinka_eval` takes a program path, results directory, experiment function name, number of runs, and optional validation/aggregation functions. It writes `metrics.json` and `correct.json`; metrics conventionally contain `combined_score`, and the correctness payload contains `correct` and `error`. Its usual execution path loads a candidate program. We must integrate an isolated evaluator before using it with generated harness code; matching output JSON alone is not a completed ShinkaEvolve integration.

That isolated evaluator boundary is now implemented in `agentqa.shinka_bridge` and validated by the actual scheduler, with evidence in `evidence/shinka-bridge-001/`. The bridge reads candidates as data and delegates execution to the Docker worker, preserving host recorder/oracle ownership. Interface correctness and task fitness are distinct, so a valid policy with poor behavior receives low fitness rather than being discarded as a broken interface.

The project currently contains no copied ShinkaEvolve implementation. Preserve upstream license/notices for any future vendoring. The standalone dependency-free measurement core does not need the framework's model SDKs or full scientific stack.

The proposal already identifies [HarnessFix](https://arxiv.org/abs/2606.06324) and [Self-Harness](https://arxiv.org/abs/2606.09498) as direct overlap. A fuller method comparison and the required AI Scientist/Digital Red Queen reading remain part of S10 before the final research write-up. No "first" claim is justified by this checkpoint.
