"""Clean offline export/wheel validation; never calls models or candidates.

Requires the core development wheelhouse to have been downloaded beforehand.
The Google Doc is verified separately through the authenticated connector;
offline reproduction checks its versioned source and native-readback record.
"""

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

from agentqa.distribution import verify_archive


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--wheel", type=Path, required=True)
    parser.add_argument("--wheelhouse", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    archive, wheel, wheelhouse, output = (p.resolve() for p in (args.archive, args.wheel, args.wheelhouse, args.output))
    archive_check = verify_archive(archive)
    output.mkdir(parents=True, exist_ok=False)
    source = output / "source"
    source.mkdir()
    with zipfile.ZipFile(archive) as bundle:
        bundle.extractall(source)
    subprocess.run([sys.executable, "-m", "venv", str(output / "env")], check=True)
    python = output / "env/bin/python"
    env = dict(os.environ)
    for variable in ("PYTHONPATH", "OPENAI_API_KEY", "CODEX_API_KEY", "AGENTQA_DOCKER_TESTS"):
        env.pop(variable, None)
    env.update(PYTHONNOUSERSITE="1", MPLCONFIGDIR=str(output / "mpl"), XDG_CACHE_HOME=str(output / "cache"))
    steps = []

    def run(name, command):
        with (output / f"{name}.log").open("wb") as stream:
            result = subprocess.run([str(part) for part in command], cwd=source, env=env,
                                    stdout=stream, stderr=subprocess.STDOUT)
        steps.append({"step": name, "returncode": result.returncode})
        print(name, result.returncode, flush=True)
        if result.returncode:
            raise RuntimeError(f"{name} failed; retained log: {output / (name + '.log')}")

    run("dependencies", [python, "-m", "pip", "--disable-pip-version-check", "install", "--no-index",
                         "--find-links", wheelhouse, "-r", source / "requirements-dev.lock"])
    run("wheel_install", [python, "-m", "pip", "--disable-pip-version-check", "install", "--no-index", "--no-deps", wheel])
    run("installed_location", [python, "-I", "-c", "import agentqa; print(agentqa.__file__)"])
    if str(output / "env") not in (output / "installed_location.log").read_text():
        raise ValueError("Package did not import from the isolated wheel environment")
    run("tests", [python, "-I", "-m", "pytest", "tests"])
    run("evidence", [output / "env/bin/agentqa", "verify-evidence", "--root", source])
    evidence = json.loads((output / "evidence.log").read_text())
    audit = source / "evidence/controlled-transfer-012"
    frozen = json.loads((audit / "plan.json").read_text())["plan_hash"]
    run("audit_replay", [python, "-I", source / "scripts/run_controlled_audit.py", "verify", "--root", source,
                         "--output", audit, "--expected-hash", frozen])
    run("audit_analysis", [python, "-I", source / "scripts/analyze_controlled_audit.py", "--root", source,
                           "--audit", audit, "--expected-hash", frozen, "--output", output / "figure"])
    for name in ("trials.csv", "results.md"):
        if (output / "figure" / name).read_bytes() != (source / "report/figures/controlled-transfer-012" / name).read_bytes():
            raise ValueError("Regenerated audit CSV/table differs")
    run("html_replay", [python, "-I", source / "scripts/build_replay.py", "--output", output / "replay/index.html"])
    if (output / "replay/index.html").read_bytes() != (source / "report/demo-native/index.html").read_bytes():
        raise ValueError("Final replay did not regenerate identically")
    result = {"schema": "agentqa.final-reproduction.v1", "archive_sha256": archive_check["sha256"],
              "wheel_sha256": sha(wheel), "steps": steps, "isolated_noneditable_wheel": True,
              "tests": (output / "tests.log").read_text().strip().splitlines()[-1],
              "evidence": evidence, "audit_table_csv_match": True, "html_byte_identical": True,
              "report_sha256": sha(source / "report/final-report.md"),
              "final_pdf": False, "new_model_or_candidate_executions": 0,
              "core_file_hashes": {p.name: sha(p) for p in sorted((source / "src/agentqa").glob("*.py"))},
              "scope": "C1 pilot plus N1 native initialization and N2 isolated helper boundary; generated-repair main study unperformed"}
    (output / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"result": str(output / "result.json"), "saved_evidence_verified": True,
                      "html_matches": True, "new_inference_calls": 0}))


if __name__ == "__main__":
    main()
