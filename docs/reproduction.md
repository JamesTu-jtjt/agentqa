# Reproducing the current prototype

This is a development proof of concept and inconclusive repair-selection pilot. The independent main-study audit has not run. Verification and replay below make **no model calls**. The recorded three-call Codex allowance is exhausted; a new clone does not reset it.

## Source and installation

The user authorized a private GitHub repository at `JamesTu-jtjt/agentqa`. Access requires that account's authorization. The working branch is `james-tu/agentqa`.

```sh
git clone https://github.com/JamesTu-jtjt/agentqa.git
cd agentqa
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/python -m pytest
.venv/bin/agentqa verify-evidence --root .
```

Validated with Python 3.13.5 on macOS ARM64. The installed core uses the standard library. The lock adds test/figure dependencies. The historical 80% clean check installed a noneditable wheel, passed 124 offline tests and rebuilt a byte-identical development replay; its package identities remain in `evidence/clean-reproduction-080.json`. The 90% clean check covers the changed package and completed C1 controlled audit: 131 offline tests (three opt-in Docker tests skip), 179 coding traces, 28 publication receipts and matching regenerated audit CSV/table. See `evidence/clean-reproduction-090.json` for the new wheel/source identities. No new model or candidate execution is required. Cross-platform byte-identical scientific figure export is not claimed.

## Recorded evidence and replay

`agentqa verify-evidence --root .` checks 179 coding traces, 28 publication receipts, the frozen three-candidate pilot pool, the six pinned-source diagnostic cases, and the twenty-case publication qualification. The 36 C1 traces are included in 179, not added again. It replays the original matched selector decisions, validates the C1 snapshot and complete outcome grid, and reproduces descriptive analysis. It checks existing records; it does not rerun the original model, task or native scheduler. Hashes detect drift against manifests, not malicious replacement of the entire evidence store.

## Controlled pilot C1

The committed freeze precedes all audit outcomes (`7ae8dd0`). The original native-agent main study remains unperformed; C1 is a separately labeled controlled template-transfer pilot using cached policies. Verify it without Docker or inference:

```sh
.venv/bin/python scripts/run_controlled_audit.py verify --output evidence/controlled-transfer-012 --expected-hash fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3
MPLCONFIGDIR=/tmp/agentqa-mpl XDG_CACHE_HOME=/tmp/agentqa-cache .venv/bin/python scripts/analyze_controlled_audit.py --audit evidence/controlled-transfer-012 --expected-hash fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3 --output runs/my-controlled-analysis
```

The analysis requires the entire original development comparison, its traces, frozen pool and C1 snapshots, all included in the bundle. The CSV and Markdown table regenerate exactly. Figure formats PNG/SVG/PDF and an input/output/script hash manifest accompany the recorded results. `verify` never creates missing final outputs or executes candidates. Exact historical execution requires the preserved source/runtime snapshot and existing Docker isolation; `run` refuses changed code/runtime or an interrupted reservation without a result. Do not erase the original trial directory to resample an unfavorable or interrupted outcome.

Both generated policies passed 9/9, parent 3/9 and nonselectable authored reference 9/9. All three previously selected IDs are identical; selector differences are zero. One source pool warrants descriptive results only, not a confidence interval or equivalence claim. The 80% HTML replay is preserved as a historical development artifact; the final delivery checkpoint will integrate C1 into a new replay.

Open `report/demo/index.html` in a browser. It is a self-contained page with no external assets, network requests, task execution or model calls. Tabs replay the actual failed/no-publication/partial/complete publisher cases; a separate timeline shows recorded controller actions around a configuration handoff. Limits and authored-versus-generated origins are visible in the page.

To rebuild the page from checked evidence, choose a new path:

```sh
.venv/bin/python scripts/build_replay.py --output runs/replay/index.html
```

Saved historical request identities include original absolute paths. Offline verification treats those as recorded identifiers and uses the included local copies; it does not require the original developer's home directory. New evaluations create new request paths and identities. Replaying a bundle for its historical request does not authorize attributing it to a changed request.

## Regenerate analysis and figures

```sh
MPLCONFIGDIR=/tmp/agentqa-mpl XDG_CACHE_HOME=/tmp/agentqa-cache .venv/bin/python scripts/analyze_upstream.py --source evidence/upstream-source-006 --bound evidence/bound-shinka-008 --output runs/publication-figures
.venv/bin/python scripts/analyze_audit.py --plan evidence/preaudit-analysis-010/synthetic-plan.json --outcomes evidence/preaudit-analysis-010/synthetic-outcomes.json --output runs/synthetic-analysis.json
```

The second command is explicitly **synthetic**, not an empirical audit or selector result. Existing figures also include development controls, the inconclusive selector comparison and stateful workflow outcomes. No re-analysis may relabel them as held-out transfer.

## Optional local execution

The original authored demo requires no model or Docker:

```sh
.venv/bin/agentqa demo --output runs/offline-demo
```

Generated controller/task code requires the pinned Docker worker. The optional real Shinka scheduler checks require the separate environment and official pinned checkout described in the README. To rerun the broader authored publication qualification in a new directory:

```sh
scratch/shinka-venv/bin/python scripts/qualify_publication.py --output runs/publication-qualification
```

Those are twenty fixed authored process checks, not independent agent-repair audit samples. Never execute generated task/controller code through the trusted local evaluator adapter. No credential or model access is needed for this command.

## Reproduction archive and publication boundary

```sh
.venv/bin/python scripts/build_repro_bundle.py --output dist/agentqa-reproduction.zip
```

The archive includes Git-visible project source, documents, selected experimental records, candidate programs, source snapshots, dependencies and attribution, plus an internal hash/size manifest. Its ordering and timestamps are fixed. It excludes Git metadata, environments, provider credentials, local runtime directories, optional vendor checkout and Neuroevolution. Symlinks, credential filenames and selected secret patterns block packaging. The scan is a useful boundary check, not a proof that arbitrary secrets are impossible.

`dist/`, `scratch/` and `runs/` are ignored; generated archives and downloaded dependency wheels are local outputs, not automatically uploaded. The source repository contains the recipe and selected evidence needed to rebuild them. Upstream source copies retain their Apache-2.0 license and attribution.

The current prototype is packaged and checked. Final reproduction must be repeated after any future main study or report changes. Native model-agent failure discovery, useful generated repair diversity, final selection/audit freeze and the main hypothesis remain unresolved.
