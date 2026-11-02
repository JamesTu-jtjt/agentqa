# Pilot budget and study boundary

Updated 2 November 2026. James requested GPT-6.1 Sol through his Codex account with low usage. The route uses saved ChatGPT authentication through Codex CLI, exact model `gpt-6.1-sol`, serial execution, and at most 120 seconds per invocation. The lifetime pilot allowance is **three invocations; all three are consumed**. Subscription dollar cost is unavailable, not zero. No separately billed API calls were made.

## Actual allowance and usage

| Work | Inference allowance | Actual use / retained evidence |
| --- | ---: | --- |
| Source-conditioned candidate generation | 1 invocation | `generation-001`; 9,064 input / 376 output tokens; two policy repairs retained. |
| Unseeded verification-policy discovery | 1 invocation | `unseeded-policy-002`; 8,914 input / 420 output tokens; seven original trials and a separately labeled seven-trial infrastructure diagnostic retained. |
| Unseeded stateful-controller discovery | 1 invocation | `stateful-controller-003`; 9,254 input / 1,662 output tokens; six cases, one unchanged generated controller. |
| Cached selection / regression | 0 additional invocations | 60 development trials; all selectors evaluated the same pool. |
| Authored references / controls | 0 invocations | 35 original controls plus 12 stateful trials; no generated failures implied. |
| Upstream integration reference | 0 invocations | Two cached-policy trials through the actual pinned Shinka scheduler. |
| Generation retries / new contingency calls | 0 invocations | No inference retries. The worker diagnostic reused a cached program; original failures remain. |
| Independent audit | 0 pilot invocations / not started | Deferred to a separately frozen, feasible main study; no audit outcomes used. |
| **Total / remaining** | **3 / 0** | **27,232 input / 2,458 output tokens** reported across three completed calls. |

Reasoning-output fields sum to 1,227 tokens and are separately recorded; do not add them to the output-token field as though they were disjoint. The durable ledger is `runs/codex-pilot.sqlite3`; a sanitized accounting export accompanies the 50% checkpoint. Failed or timed-out invocations would consume the same allowance. Removing the ledger or cloning the repository does not reset the authorized lifetime cap.

The stateful workflow used 152 local container invocations across 18 trials, totaling 109.13 seconds of measured worker wall time. Its sole generation took 55.21 seconds. Worker sums exclude orchestration, analysis and plotting; these small deterministic tasks do not estimate the cost of realistic model-driven episodes.

The 50%→70% stage used **zero additional inference calls**. The grounded source/adapter track ran 18 local authored evaluator processes: four priming runs, six changed-request probe runs, and eight adapter checks across the preserved initial/current versions. These process jobs are separate from coding-agent episodes and unit-test subprocesses. Total source-track wall time was not fully instrumented (priming runtimes were not retained), so no complete timing/cost estimate is invented. All prior usage and failed outcomes remain preserved.

The 70%→80% stage also used **zero additional inference calls**. Twenty further fixed authored scheduler processes qualified the publication adapter; all twenty contracts and ten renamed pairs matched. Clean reproduction, replay, packaging and private GitHub publication do not consume model calls. They do not establish a completed main study.

## Main study: deferred scope, not spending authorization

The proposal's 1,572-episode example is not authorized by the pilot. The earlier 12-discovery/3-generation/8-validation sketch is superseded by the three-call allocation above. Repeated deterministic policy slots do not provide independent stochastic replications.

Before additional model-driven work, define a realistic episode containing the actual model/tool loop, identify a reproducible semantic source failure, and measure its complete resource profile. Then choose common candidate pools and matched selector budgets, explicitly reserving parent/reference runs, regression checks, independent audit, failed generations, permitted infrastructure retries, and contingency. Preserve all three selectors and audit separation even if candidate breadth must shrink.

Continued subscription inference needs a revised explicit invocation allowance. A separately billed API route would need a monetary cap and verified pricing. No API-key fallback is allowed. A negative feasibility result is not permission to expand the search indefinitely.

`CodexBackend` enforces durable invocation counts, duplicate-ID refusal, exact model, saved-account route and runtime bounds. `Ledger` separately tests monetary reservations for a possible API route. Neither makes unknown subscription cost measurable.
