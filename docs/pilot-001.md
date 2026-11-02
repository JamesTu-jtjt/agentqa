# Implementation checkpoint and first Codex pilot

Date: 2 November 2026. This is a development checkpoint, not the final research report.

## What actually ran

The development environment uses Python 3.13.5 and a pinned Python container image. The first demonstration executed five authored policies on seven family cases: 35 trials, each using actual visible-test and functional-check processes. Their event traces can be replayed without inference.

The authored reminder policy verifies after reading the explicit phrase that code was edited. It completes the source, renaming, noise, cache, and unchanged cases, but fails the compaction and handoff cases because the phrase is absent. A provenance-checking reference and an always-rerun reference complete all seven. A refusing reference completes none. These behaviors were deliberately specified as measurement controls.

James then authorized use of his signed-in Codex account with low usage. One `codex exec` call using `gpt-6.1-sol`, low reasoning, returned two small `choose_action` programs from the original source failure. No development-family cases or audit results were included in that generation prompt.

Both generated policies check whether current evidence has a passing status and matches the current fingerprint; one also requires an identified record. Generated Python ran in a container with no host mounts, external network, provider credentials, or evaluator state. The trusted host controller interpreted the returned action and executed the corresponding authored fixture operation. Candidate code did not execute inside the host recorder.

## Results

| Candidate | Source | Other development cases | Total verified |
| --- | ---: | ---: | ---: |
| Require passing evidence for the current footprint | 1/1 | 6/6 | 7/7 |
| Require an identified, current passing record | 1/1 | 6/6 | 7/7 |

There is one execution per candidate/case. No independent audit, repeated stochastic assessment, natural-failure search, or comparative selector experiment has run. The source failure and fixture edits are authored. The policy programs are actual model outputs.

**Interpretation:** The Codex account route and isolated policy execution work. This fixture presents the relevant fingerprints explicitly, and both repairs use them. It therefore offers no observed basis for selecting one repair over the other. The authored narrow-reminder case validates the apparatus but cannot establish that naturally generated repairs commonly overfit in this way.

The next scientific step is to assess naturally occurring failures and repair variability before finalizing the study. If robust policies consistently solve the chosen class, report that result or revise the research scope during development. Do not weaken validation or hide provenance merely to manufacture a selector advantage.

## Resource accounting

- Codex invocations: **1**, generation only; local evaluation makes no additional inference calls.
- Requested/used model: `gpt-6.1-sol`; saved ChatGPT authentication; CLI `0.160.0`.
- Reported input tokens: **9,064**; output tokens: **376**; reasoning output tokens: **112**, retained as a separate reported field rather than added again to output.
- Generation runtime: approximately **14.5 seconds**.
- Subscription dollar cost: **unavailable**. No separate API key was used; this is not evidence of zero subscription consumption.
- Small-run allowance: **three total persisted invocations**, serial, at most 120 seconds each. One is consumed; two remain. There is no automatic large study launch or automatic replenishment.

## Verification and reproducibility

The offline suite passed **61 tests**, with three opt-in Docker tests skipped. The Docker test file passed **7 tests** when enabled; four are also part of the offline suite. These should not be added as if they were all distinct tests.

The Docker checks verify no host-user directory or Docker socket, no inherited sentinel credential, a non-root UID, a read-only system filesystem, unavailable external networking, and bounded timeout/output behavior with container cleanup. They validate a specific execution configuration, not a general proof of container security.

Artifacts:

- [Generation prompt](../evidence/codex-pilot-001/prompt.txt), [response and usage](../evidence/codex-pilot-001/inference.json), and [trial summary](../evidence/codex-pilot-001/summary.json).
- [Candidate 0](../evidence/codex-pilot-001/candidate-00.json) and [candidate 1](../evidence/codex-pilot-001/candidate-01.json).
- [Authored-control summary](../evidence/offline-controls-001/summary.json), with trace paths and final hashes.
- [Authored-control figure](../report/figures/authored-control-outcomes.png) and [design diagram](../report/figures/experimental-design.png), also exported as SVG/PDF. `scripts/build_figures.py` verifies every underlying authored trace before plotting.

Live invocation identities and results persist in an ignored SQLite ledger; sanitized inference, candidate, and trace artifacts are included in the evidence directory. Do not delete the ledger to repeat a completed invocation.

Official interface references: [non-interactive Codex](https://developers.openai.com/codex/noninteractive), [configuration reference](https://developers.openai.com/codex/config-reference), and [GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol). The CLI was checked locally before invocation. No credentials were read into project artifacts.
