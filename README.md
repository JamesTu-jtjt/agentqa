# AgentQA: Beyond the Repaired Example

Metamorphic validation of self-improving coding agents. This is Task 2 of the Sakana AI exercise and an independent Git repository, physically located beside `Neuroevolution/` inside the shared workspace.

**Question:** Can valid test families built around a known failure mechanism select agent repairs that transfer better than source-only retesting or generic variations?

**Initial failure class:** Stale verification evidence—an agent treats old passing tests as verification of a changed repository state.

## Project documents

- [Research proposal](proposal.md): hypothesis, novelty boundary, comparisons, and submission deliverables.
- [Timeline](docs/timeline.md): eight working days of planned work, dependencies, milestone checks, and contingency choices.
- [Implementation TODOs](docs/todos.md): ordered work items, acceptance criteria, and completion evidence.
- [Implementation and experiment runbook](docs/execution.md): component boundaries, experiment controls, accounting, and handoff procedure.
- [Decisions and current status](docs/status.md): assumptions, pending inputs, completed work, and the next action.
- [Agent instructions](AGENTS.md): implementation conventions for Codex.

## Current state

The executable development core is implemented: trusted test records, content fingerprints, an independent completion oracle, seven family cases, authored controls, offline replay, selection rules, cost reservations, and an isolated Docker worker. Codex is the implementation owner; James owns research direction and resource choices.

Implementation started on 2 November 2026. The real pinned ShinkaEvolve scheduler/evaluator bridge, immutable registry, and resumable matched-suite runner are implemented. A 60-trial development comparison selected the same repair under all three methods; there is no demonstrated selection advantage. An independent audit and confirmed naturally occurring semantic failures remain outstanding.

**Progress: approximately 80%, stopped at the requested checkpoint.** The bounded coding workflow, grounded Shinka source case and publication adapter are implemented. Twenty broader authored publication cases matched their contracts; all ten renamed-layout pairs preserved their verdicts, including valid negative results. The suite passes 124 offline tests. A clean noneditable wheel install replays 143 coding traces and 28 publication receipts and regenerates the recorded demo. These remain development evidence; native model-agent source failures and selector advantage are not established.

All three allowed Codex calls are consumed; no new calls were made for the 70% or 80% work. Subscription dollar cost is unavailable. The main selector comparison remains unproven. See the [80% checkpoint](docs/checkpoint-080.md), [source diagnosis](docs/upstream-source-diagnosis.md), [working report](report/working-report.md) and [reproduction guide](docs/reproduction.md). Generated-pool diversity, final main-study freeze, independent audit and submission remain unfinished.

Private GitHub repository: [JamesTu-jtjt/agentqa](https://github.com/JamesTu-jtjt/agentqa), explicitly authorized by the user and separate from Neuroevolution.

## Run the development core

Validated on Python 3.13.5. Core execution uses only the standard library; the lock file includes tests and figure dependencies.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps -e .
.venv/bin/python -m pytest
.venv/bin/agentqa verify-evidence --root .
.venv/bin/agentqa demo --output runs/my-offline-demo
.venv/bin/python scripts/build_figures.py runs/my-offline-demo/summary.json --output runs/my-figures
```

Demo output directories must not already exist. Replay a recorded trial without a model call:

```sh
.venv/bin/agentqa replay evidence/offline-controls-001/traces/compaction--narrow_reminder.jsonl
```

Docker integration checks are opt-in and require a running daemon and the pinned image. They exercise the container worker, not an entire evolutionary run:

```sh
docker pull python@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419
AGENTQA_DOCKER_TESTS=1 .venv/bin/python -m pytest tests/test_sandbox.py
```

The Codex pilot uses saved account authentication; it does not read or copy credentials. `scripts/codex_pilot.py` requires a new output directory and preserves a fixed invocation ID in `runs/codex-pilot.sqlite3`, preventing an accidental second generation when rerun. Inspect the existing result rather than deleting the ledger to repeat it.

## Development evidence and figures

- [Authored controls](evidence/offline-controls-001/summary.json): 35 executed control trials, zero model calls; replayable traces included.
- [Codex pilot](evidence/codex-pilot-001/summary.json): two model-generated policy repairs evaluated on the development family.
- [Pilot interpretation](docs/pilot-001.md): actual findings, usage, and limits.
- [Control outcome figure](report/figures/authored-control-outcomes.png) and [experimental design](report/figures/experimental-design.png); SVG/PDF copies and generation manifest accompany them.
- [Matched comparison](evidence/development-comparison-001/summary.json), [outcome figure](report/figures/comparison-001/development-comparison.png), and [worker timing](report/figures/comparison-001/worker-timing.png).
- [Candidate/split specification](docs/candidate-split-spec.md), [discovery protocol](docs/discovery-protocol.md), and [methods reading](docs/reading-notes.md).
- [Stateful workflow protocol](docs/workflow-protocol.md), [generated-controller results](evidence/stateful-controller-005/summary.json), [workflow outcomes](report/figures/workflow-003/workflow-outcomes.png) and [recorded actions](report/figures/workflow-003/workflow-actions.png).
- [Grounded upstream results](evidence/upstream-source-006/summary.json), [current adapter checks](evidence/bound-shinka-008/summary.json), [qualification figure](report/figures/upstream-004/publication-qualification.png), [analysis specification](docs/analysis-protocol.md) and [third-party attribution](third_party/NOTICE.md).
- [Broader twenty-case qualification](evidence/publication-qualification-011/summary.json), [recorded HTML replay](report/demo/index.html), [clean reproduction](evidence/clean-reproduction-080.json) and [packaging instructions](docs/reproduction.md). Download/open the HTML locally; GitHub's source viewer does not execute it.

Check and plot saved upstream/publication evidence without model calls or new evaluations:

```sh
MPLCONFIGDIR=/tmp/agentqa-mpl XDG_CACHE_HOME=/tmp/agentqa-cache .venv/bin/python scripts/analyze_upstream.py --source evidence/upstream-source-006 --bound evidence/bound-shinka-008 --output runs/my-publication-analysis
```

Run the pre-audit analysis's **synthetic demonstration** (not a real audit):

```sh
.venv/bin/python scripts/analyze_audit.py --plan evidence/preaudit-analysis-010/synthetic-plan.json --outcomes evidence/preaudit-analysis-010/synthetic-outcomes.json --output runs/my-synthetic-analysis.json
```

Reanalyze existing workflow evidence without model calls or Docker execution:

```sh
MPLCONFIGDIR=/tmp/agentqa-mpl XDG_CACHE_HOME=/tmp/agentqa-cache .venv/bin/python scripts/analyze_workflow.py evidence/workflow-controls-004 evidence/stateful-controller-005 --output runs/my-workflow-analysis
```

Run the authored stateful controls in fresh isolated workers (no inference):

```sh
.venv/bin/python scripts/workflow_pilot.py --mode controls --output runs/my-workflow-controls
```

The generation mode is not a routine reproduction step: the lifetime three-call pilot allowance is exhausted. Preserve the existing generated controller and accounting ledger.

Build a deterministic, scanned source/evidence archive without model calls:

```sh
.venv/bin/python scripts/build_repro_bundle.py --output dist/agentqa-reproduction.zip
```

## ShinkaEvolve integration and comparison

ShinkaEvolve is an optional integration dependency, isolated from the core environment. Install the official checkout at the recorded revision, then use `requirements-shinka.lock` in a separate environment. If the checkout is absent:

```sh
git clone https://github.com/SakanaAI/ShinkaEvolve.git vendor/ShinkaEvolve
git -C vendor/ShinkaEvolve checkout 8adc053a2ce4511ad2ac310e004c530a73fb974a
```

```sh
python3 -m venv scratch/shinka-venv
scratch/shinka-venv/bin/python -m pip install -r requirements-shinka.lock
scratch/shinka-venv/bin/python -m pip install --no-build-isolation --no-deps -e . -e vendor/ShinkaEvolve
scratch/shinka-venv/bin/python scripts/check_shinka_bridge.py --program evidence/frozen-pool-001/repair-00.py --output runs/my-shinka-check
.venv/bin/python scripts/run_comparison.py --pool evidence/frozen-pool-001/pool.json --output runs/my-comparison
```

Both commands execute cached policy programs in Docker and make no inference calls. New outputs require new directories. The comparison can resume its own unchanged plan and code; it refuses silent input changes or resampling of interrupted trials. Existing saved evidence can be replayed; use its included code snapshot when reproducing the exact frozen code hash after later development changes.

The diagnostic source/adapter checks also use the optional Shinka environment. They execute fixed authored evaluators, not generated code, and require fresh output directories:

```sh
scratch/shinka-venv/bin/python scripts/probe_shinka_results.py --output runs/my-upstream-probe
scratch/shinka-venv/bin/python scripts/check_bound_shinka.py --output runs/my-bound-check
```

```sh
.venv/bin/python scripts/build_comparison_figures.py evidence/development-comparison-001/summary.json --output runs/my-comparison-figures
```

## Repository boundary

Run all project and Git commands from this directory. The surrounding workspace ignores this repository, and Task 2 must not be added to the Neuroevolution history or registered as its submodule. The working branch is `james-tu/agentqa`; use `james-tu/` for subsequent branches. The authorized remote is the private `JamesTu-jtjt/agentqa` repository.

The proposal is preserved at its original path. The local subprocess fixture runner is for trusted authored code only; generated policy functions execute through the container worker.
