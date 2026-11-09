# Recorded experimental resources

The pilot used three sequential GPT-6.1 Sol calls with a 120-second bound per call. All outputs and failed worker attempts were retained. Subscription dollar cost is unavailable; no separately billed API calls were made. N1 and N2 used no additional inference.

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
| Original native-agent main audit | 0 pilot invocations / not started | Deferred; the separately labeled C1 controlled pilot uses cached programs and does not complete this main study. |
| **Total / remaining** | **3 / 0** | **27,232 input / 2,458 output tokens** reported across three completed calls. |

Reasoning tokens are recorded separately and must not be added to output tokens as though disjoint. The frozen ledgers and inference records preserve per-call accounting. Reproduction uses cached policies and saved evidence without further model calls.
