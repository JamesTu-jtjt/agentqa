"""Attempt-bound result publication for trusted external evaluator processes.

This adapter does not sandbox an evaluator. Its caller must use a fixed authored
evaluator; any generated task/controller code must remain in Docker. Files and
receipts are host-owned. Hashes establish integrity against frozen manifests,
not authenticity against an attacker who can replace the entire artifact set.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import uuid

from .contracts import digest, safe_path

BUNDLE_SCHEMA = "agentqa.evaluation-bundle.v1"


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot_inputs(inputs):
    if not inputs or len(inputs) > 12 or any(not isinstance(name, str) for name in inputs):
        raise ValueError("Declare 1–12 named evaluator inputs")
    result = {}
    for name, raw in sorted(inputs.items()):
        path = Path(raw).absolute()
        if (path.is_symlink() or not path.is_file() or path.stat().st_nlink != 1
                or path.stat().st_size > 1048576):
            raise ValueError("Inputs must be regular unlinked files of at most 1 MiB")
        result[name] = {"path": str(path), "sha256": file_sha(path), "bytes": path.stat().st_size}
    return result


def read_json(path):
    if path.stat().st_size > 16384:
        raise ValueError("Result JSON exceeds 16 KiB")
    def reject_constant(value):
        raise ValueError(f"Nonfinite JSON constant: {value}")
    def unique_object(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("Duplicate JSON key")
            value[key] = item
        return value
    return json.loads(path.read_text(), parse_constant=reject_constant, object_pairs_hook=unique_object)


def parse_result(root):
    metrics = read_json(safe_path(root, "metrics.json"))
    correct = read_json(safe_path(root, "correct.json"))
    if not isinstance(metrics, dict) or not isinstance(correct, dict) or type(correct.get("correct")) is not bool:
        raise ValueError("Malformed metrics/correctness object")
    score = metrics.get("combined_score")
    if type(score) not in (int, float) or not math.isfinite(score):
        raise ValueError("Score must be a finite number")
    return {"metrics": metrics, "correct": correct}


@dataclass(frozen=True)
class BundleVerdict:
    valid: bool
    correct: bool
    score: float | int | None
    reason: str

    def to_dict(self):
        return asdict(self)


def verify_bundle(root: Path, *, expected_request_hash: str, expected_receipt_hash: str):
    """Replay publication evidence using external frozen identities."""
    try:
        request = read_json(safe_path(root, "request.json"))
        receipt = read_json(safe_path(root, "receipt.json"))
        if digest(request) != expected_request_hash or digest(receipt) != expected_receipt_hash:
            return BundleVerdict(False, False, None, "manifest_mismatch")
        if (request.get("schema") != BUNDLE_SCHEMA or receipt.get("schema") != BUNDLE_SCHEMA
                or receipt.get("request_hash") != expected_request_hash
                or receipt.get("attempt_id") != request.get("attempt_id")):
            return BundleVerdict(False, False, None, "request_mismatch")
        if receipt.get("status") != "completed" or type(receipt.get("returncode")) is not int or receipt["returncode"] != 0:
            return BundleVerdict(False, False, None, "execution_not_successful")
        if receipt.get("inputs_after") != request.get("inputs"):
            return BundleVerdict(False, False, None, "inputs_changed")
        if receipt.get("publication_error"):
            return BundleVerdict(False, False, None, "incomplete_or_invalid_publication")
        hashes = {name: file_sha(safe_path(root / "results", name)) for name in ("metrics.json", "correct.json")}
        if hashes != receipt.get("artifact_hashes"):
            return BundleVerdict(False, False, None, "artifact_mismatch")
        result = parse_result(root / "results")
        if digest(result) != receipt.get("result_hash"):
            return BundleVerdict(False, False, None, "result_mismatch")
        return BundleVerdict(True, result["correct"]["correct"], result["metrics"]["combined_score"], "bound_result")
    except (OSError, ValueError, TypeError, KeyError) as exc:
        return BundleVerdict(False, False, None, f"invalid_bundle:{type(exc).__name__}")


def run_bound_job(scheduler, program: Path, evaluator: Path, output: Path, *,
                  trusted_evaluator=False, extra_inputs=None, runtime_identity: dict | None = None,
                  timeout=10):
    """Preserve one fresh attempt. Never reuse or delete previous result files."""
    if not trusted_evaluator:
        raise ValueError("Only fixed authored evaluators may use the local scheduler adapter")
    if not 0 < timeout <= 60:
        raise ValueError("Evaluator timeout must be 0–60 seconds")
    inputs = {"program": program, "evaluator": evaluator}
    if extra_inputs:
        if set(extra_inputs) & set(inputs):
            raise ValueError("Extra input names collide with required inputs")
        inputs.update(extra_inputs)
    before = snapshot_inputs(inputs)
    output.mkdir(parents=True, exist_ok=False)
    results_dir = output / "results"
    results_dir.mkdir()
    request = {"schema": BUNDLE_SCHEMA, "attempt_id": uuid.uuid4().hex, "inputs": before,
               "runtime": runtime_identity or {}, "timeout_seconds": timeout,
               "publication": ["metrics.json", "correct.json"]}
    (output / "request.json").write_text(json.dumps(request, indent=2))
    started = time.monotonic()
    process, observed = None, None
    status, error = "infrastructure_error", None
    try:
        process = scheduler.submit_async(str(program.absolute()), str(results_dir.absolute()))
        try:
            process.wait(timeout=timeout)
            status = "completed" if process.returncode == 0 else "failed"
        except subprocess.TimeoutExpired:
            status = "timeout"
            process.kill()
            process.wait(timeout=5)
        observed = scheduler.get_job_results(process, str(results_dir.absolute()))
    except (OSError, ValueError, RuntimeError) as exc:
        error = str(exc)
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
    try:
        after = snapshot_inputs(inputs)
    except (OSError, ValueError):
        after = None
    artifacts, result, publication_error = {}, None, None
    try:
        result = parse_result(results_dir)
        artifacts = {name: file_sha(safe_path(results_dir, name)) for name in ("metrics.json", "correct.json")}
    except (OSError, ValueError, TypeError, KeyError) as exc:
        publication_error = type(exc).__name__
    receipt = {"schema": BUNDLE_SCHEMA, "attempt_id": request["attempt_id"],
               "request_hash": digest(request), "status": status,
               "returncode": process.returncode if process else None, "inputs_after": after,
               "artifact_hashes": artifacts, "result_hash": digest(result) if result is not None else None,
               "publication_error": publication_error, "execution_error": error,
               "duration_seconds": time.monotonic() - started}
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2))
    if observed is not None:
        (output / "scheduler-result.json").write_text(json.dumps(observed, indent=2))
    verdict = verify_bundle(output, expected_request_hash=digest(request), expected_receipt_hash=digest(receipt))
    manifest = {"schema": BUNDLE_SCHEMA, "request_hash": digest(request), "receipt_hash": digest(receipt),
                "verdict": verdict.to_dict()}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
