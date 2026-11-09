# Reproducing AgentQA

Saved-record verification makes no model calls and requires neither Docker nor ShinkaEvolve. Optional experiment reruns use separate environments and new output directories.

## Install and verify

```sh
git clone https://github.com/JamesTu-jtjt/agentqa.git
cd agentqa
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.lock
.venv/bin/python -m pip install --no-build-isolation --no-deps .
.venv/bin/python -m pytest
.venv/bin/agentqa verify-evidence --root .
```

Validated with Python 3.13.5 on macOS ARM64. The core uses the standard library; the development lock adds testing and plotting dependencies. The historical clean-install result was 145 passing tests and three optional Docker skips; see `evidence/native-followup-validation.json`. Validation records describe their recorded revision, rather than guaranteeing later changes.

Verification covers 179 coding traces, 28 original publication receipts, the C1 frozen pool and outcomes, 56 native databases/WALs, seven additional bound receipts, and 24 standard-helper cases. It checks integrity and reproduces descriptive analysis using saved records. Historical paths are identifiers; replay uses included local artifacts and temporary SQLite copies. Volatile shared-memory coordination bytes are excluded under the [replay amendment](native-replay-amendment.md).

## View and regenerate the demonstration

Open `report/demo-native/index.html` locally in a browser. It contains recorded outcomes, has no external assets, and executes no models or candidates. Earlier `demo/` and `demo-final/` directories retain historical versions.

```sh
.venv/bin/python scripts/build_replay.py --output runs/my-replay/index.html
MPLCONFIGDIR=/tmp/agentqa-mpl XDG_CACHE_HOME=/tmp/agentqa-cache .venv/bin/python scripts/analyze_native_study.py --output runs/my-native-analysis
```

Choose new output paths. The native plot summarizes deliberately introduced faults; its counts do not estimate natural failure rates.

## Replay the controlled transfer pilot

```sh
.venv/bin/python scripts/run_controlled_audit.py verify --output evidence/controlled-transfer-012 --expected-hash fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3
MPLCONFIGDIR=/tmp/agentqa-mpl XDG_CACHE_HOME=/tmp/agentqa-cache .venv/bin/python scripts/analyze_controlled_audit.py --audit evidence/controlled-transfer-012 --expected-hash fddddb72f75b21e6b98f89506ea7634c2ec348f76ee4e5e4a2ccd2d5c035ebb3 --output runs/my-controlled-analysis
```

Both generated repairs passed 9/9 cases; all selectors chose the same repair. These results support a bounded controlled-policy transfer finding, without establishing a selector benefit. Verification uses the original snapshots and records; it does not rerun model generation. The historical three-call inference allowance is exhausted.

## Optional execution

Run trusted authored controls without Docker:

```sh
.venv/bin/agentqa demo --output runs/my-authored-demo
```

Generated programs must run in the isolated container worker. Docker tests are opt-in:

```sh
docker pull python@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419
AGENTQA_DOCKER_TESTS=1 .venv/bin/python -m pytest tests/test_sandbox.py
```

Native Shinka checks require the pinned upstream source in a separate environment:

```sh
git clone https://github.com/SakanaAI/ShinkaEvolve.git vendor/ShinkaEvolve
git -C vendor/ShinkaEvolve checkout 8adc053a2ce4511ad2ac310e004c530a73fb974a
python3 -m venv scratch/shinka-venv
scratch/shinka-venv/bin/python -m pip install -r requirements-shinka.lock
scratch/shinka-venv/bin/python -m pip install --no-build-isolation --no-deps -e . -e vendor/ShinkaEvolve
```

N1's execution recipe is `scripts/run_native_study.py`: freeze a new plan with `--freeze --output runs/my-native-study`, review and commit it, then run the same command without `--freeze`. It uses 105 authored evaluator processes, including seven deliberate interruptions, and no inference. N2 uses `scripts/check_standard_wrapper.py`; copy `evidence/standard-wrapper-014/pr150_helper.py` to ignored `scratch/pr150-wrap_eval.py` for its freeze and use `PYTHONDONTWRITEBYTECODE=1` as in the recorded run. N2 uses 48 authored evaluator processes and tests isolated helpers, rather than the complete upstream PR.

Frozen evidence directories refuse overwriting or resampling. Exact historical execution may require the included code/runtime snapshot; later source changes can cause frozen execution checks to refuse. Preserve all attempts and distinguish reruns from the original study.

## Build and check a portable archive

```sh
.venv/bin/python scripts/build_repro_bundle.py --output dist/agentqa-reproduction.zip
```

The deterministic archive contains Git-visible source, documentation, selected evidence, dependencies, and attribution. It excludes Git metadata, local environments, runtime directories, and the optional vendor checkout. Packaging rejects credential filenames, symlinks, and selected secret patterns. Pattern checks cannot rule out every possible secret.

For an offline clean installation, first cache public dependency wheels and build the project wheel:

```sh
.venv/bin/python -m pip download -r requirements-dev.lock --dest scratch/wheelhouse
.venv/bin/python -m pip wheel --no-build-isolation --no-deps . --wheel-dir scratch/wheels
.venv/bin/python scripts/reproduce_offline.py --archive dist/agentqa-reproduction.zip --wheel scratch/wheels/agentqa-0.1.0-py3-none-any.whl --wheelhouse scratch/wheelhouse --output /tmp/agentqa-clean-example
```

The output directory must be new. This check installs the wheel into a fresh environment, runs tests and saved-evidence verification, regenerates the C1 CSV/table and recorded HTML, and records the report hash. Private Google Docs preparation artifacts are excluded from the public package; this check makes no Google Drive requests.

Frozen records intentionally retain their historical identities. Current presentation changes do not revise experimental outcomes, original freeze commits, or third-party attribution. See the [public disclosure audit](public-disclosure-audit.md).
