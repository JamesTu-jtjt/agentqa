"""Portable, standard-library verification of saved development evidence."""

import hashlib
import json
from pathlib import Path

from .bundles import verify_bundle
from .contracts import digest, safe_path
from .controlled_audit import finish_audit
from .publication_qualification import validate_qualification
from .recorder import replay
from .registry import validate_pool


def _plan(folder):
    envelope = json.loads((folder / "plan.json").read_text())
    body = {key: value for key, value in envelope.items() if key != "plan_hash"}
    if digest(body) != envelope["plan_hash"]:
        raise ValueError("Changed plan")
    return envelope


def verify_evidence(root: Path):
    root = root.resolve()
    traces, bundles, coordinates = 0, 0, set()
    for folder in sorted((root / "evidence").iterdir()):
        if not folder.is_dir():
            continue
        for name in ("summary.json", "evaluation.json"):
            file = folder / name
            if not file.is_file():
                continue
            data = json.loads(file.read_text())
            for row in data.get("results", []):
                if "trace" in row:
                    path = safe_path(folder, row["trace"])
                    if path in coordinates:
                        raise ValueError("Trace counted twice")
                    coordinates.add(path)
                    verdict = replay(path, row.get("trace_tip", row.get("tip"))).to_dict()
                    if any(row[key] != value for key, value in verdict.items()):
                        raise ValueError("Trace/summary verdict mismatch")
                    traces += 1
                if "bundle" in row and "receipt_hash" in row:
                    # Validate the relative directory before reading its files.
                    safe_path(folder, row["bundle"] + "/manifest.json")
                    verdict = verify_bundle(folder / row["bundle"], expected_request_hash=row["request_hash"],
                                            expected_receipt_hash=row["receipt_hash"]).to_dict()
                    if verdict != row["verdict"]:
                        raise ValueError("Bundle/summary verdict mismatch")
                    bundles += 1
    pool = json.loads((root / "evidence/frozen-pool-001/pool.json").read_text())
    validate_pool(pool)
    source = root / "evidence/upstream-source-006"
    plan = _plan(source)
    source_summary = json.loads((source / "summary.json").read_text())
    if source_summary["plan_hash"] != plan["plan_hash"]:
        raise ValueError("Source summary/plan mismatch")
    for name, expected in plan["source_hashes"].items():
        if hashlib.sha256(safe_path(source / "upstream-source", name).read_bytes()).hexdigest() != expected:
            raise ValueError("Changed pinned source copy")
    if hashlib.sha256((source / "authored_evaluator.py").read_bytes()).hexdigest() != plan["evaluator_sha256"]:
        raise ValueError("Changed authored evaluator")
    seen = set()
    declared = {name: (mode, prime) for name, mode, prime in plan["cases"]}
    for row in source_summary["results"]:
        if row["case"] in seen or declared[row["case"]] != (row["mode"], row["primed"]):
            raise ValueError("Unexpected source case")
        seen.add(row["case"])
        folder = source / row["case"]
        if hashlib.sha256((folder / "program.json").read_bytes()).hexdigest() != row["current_program_sha256"]:
            raise ValueError("Changed source request")
        for subfolder, key in (("results", "current_artifacts"), ("prior-results", "prior_artifacts")):
            actual = {file.name: hashlib.sha256(file.read_bytes()).hexdigest() for file in (folder / subfolder).glob("*.json")}
            if actual != row[key]:
                raise ValueError("Changed source result files")
        if row["returncode"] != (7 if row["mode"] == "fail" else 0):
            raise ValueError("Source execution status mismatch")
    if seen != set(declared):
        raise ValueError("Incomplete source cases")
    qualification = validate_qualification(root / "evidence/publication-qualification-011")
    controlled = root / "evidence/controlled-transfer-012"
    controlled_result = None
    if (controlled / "summary.json").is_file():
        frozen = _plan(controlled)
        summary, analysis = finish_audit(root, controlled, frozen["plan_hash"])
        controlled_result = {"trials": summary["trial_count"], "source_pools": analysis["source_pool_count"],
                             "plan_hash": frozen["plan_hash"], "native_agent_main_study": False}
    native_result = None
    if (root / "evidence/native-initialization-013/file-manifest.json").is_file():
        from .native_replay import verify_native_study
        native_result = verify_native_study(root / "evidence/native-initialization-013")
    standard_result = None
    if (root / "evidence/standard-wrapper-014/file-manifest.json").is_file():
        from .standard_replay import verify_standard_wrapper
        standard_result = verify_standard_wrapper(root / "evidence/standard-wrapper-014")
    return {"schema": "agentqa.evidence-verification.v1", "coding_traces": traces,
            "publication_bundles": bundles, "upstream_source_cases": len(seen),
            "frozen_candidates": len(pool["candidates"]), "broader_qualification": qualification,
            "controlled_transfer_audit": controlled_result,
            "native_initialization_study": native_result, "standard_helper_boundary": standard_result,
            "new_execution_or_model_calls": 0, "independent_audit": False,
            "scope": "Integrity/replay checks of retained evidence; controlled transfer is distinct from a native-agent main audit; no authenticity against full-store replacement"}
