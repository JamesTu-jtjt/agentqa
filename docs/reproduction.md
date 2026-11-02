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

Validated with Python 3.13.5 on macOS ARM64. The installed core uses the standard library. The lock adds test/figure dependencies. The 80% clean check installs a noneditable wheel into a new isolated environment, runs all 124 offline tests (three opt-in Docker tests skip), verifies saved evidence, regenerates the publication figure/analysis, and rebuilds a byte-identical HTML replay. See `evidence/clean-reproduction-080.json` for the tested wheel and source-code hashes. Cross-platform byte-identical scientific figure export is not claimed.

## Recorded evidence and replay

`agentqa verify-evidence --root .` checks 143 coding traces, 28 publication receipts, the frozen three-candidate pilot pool, the six pinned-source diagnostic cases, and the twenty-case publication qualification. It checks existing records; it does not rerun the original model, task or native scheduler. Hashes detect drift against manifests, not malicious replacement of the entire evidence store.

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
