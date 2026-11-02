"""Offline, read-only replay of native study artifacts and actual SQLite state."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

from .bundles import verify_bundle
from .contracts import digest
from .native_study import EVALUATOR, SCHEMA, cells, program, snapshot_database, analyze_rows


def isolated_database_snapshot(path):
    # SQLite's mode=ro can still update WAL shared-memory read marks. Copy the
    # durable database and WAL, never the volatile shared-memory lock/index file.
    with tempfile.TemporaryDirectory(prefix="agentqa-native-replay-") as temporary:
        destination = Path(temporary) / "programs.sqlite"
        shutil.copyfile(path, destination)
        wal = path.with_name(path.name + "-wal")
        if wal.exists():
            shutil.copyfile(wal, destination.with_name(destination.name + "-wal"))
        return snapshot_database(destination)


def verify_native_study(root: Path):
    root = root.resolve()
    envelope = json.loads((root / "plan.json").read_text())
    plan = {k: v for k, v in envelope.items() if k != "plan_hash"}
    if (digest(plan) != envelope["plan_hash"] or plan["schema"] != SCHEMA
            or plan["cells"] != [asdict(cell) for cell in cells()] or digest(EVALUATOR) != plan["evaluator_hash"]):
        raise ValueError("Native frozen plan mismatch")
    manifest = json.loads((root / "file-manifest.json").read_text())
    if manifest["plan_hash"] != envelope["plan_hash"] or digest(manifest["files"]) != manifest["files_hash"]:
        raise ValueError("Native file manifest mismatch")
    actual_names = {str(p.relative_to(root)) for p in root.rglob("*")
                    if p.is_file() and p.name != "file-manifest.json"}
    if set(manifest["files"]) != actual_names:
        raise ValueError("Native artifact inventory changed")
    volatile = []
    for name, expected in manifest["files"].items():
        path = root / name
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            raise ValueError("Unsafe native artifact path")
        if name.endswith("/programs.sqlite-shm"):
            volatile.append(name)
            continue
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError(f"Native artifact changed: {name}")
    for prefix, mapping in (("code_snapshot", plan["source_hashes"]), ("upstream-source", plan["upstream_hashes"])):
        for name, expected in mapping.items():
            if hashlib.sha256((root / prefix / name).read_bytes()).hexdigest() != expected:
                raise ValueError("Native source snapshot mismatch")
    rows = json.loads((root / "outcomes.json").read_text())
    indexed = {cell.name: cell for cell in cells()}
    evaluator_processes = 0
    interrupted = 0
    for row in rows:
        name = "--".join(row["cell"][key] for key in ("history", "policy", "mode"))
        cell = indexed[name]
        folder = root / "cells" / name
        if row != json.loads((folder / "result.json").read_text()):
            raise ValueError("Native row differs from preserved cell")
        reservation = json.loads((folder / "reservation.json").read_text())
        if reservation != {"cell": asdict(cell), "plan_hash": envelope["plan_hash"]}:
            raise ValueError("Native reservation mismatch")
        if (folder / "evaluate.py").read_text() != EVALUATOR:
            raise ValueError("Native evaluator changed")
        if (folder / "target-initial.py").read_text() != program(cell.mode):
            raise ValueError("Native target input changed")
        observed = isolated_database_snapshot(folder / "native/programs.sqlite")
        if observed != row["database"]:
            raise ValueError("Native SQLite state differs from row")
        if row["target_report"] != json.loads((folder / "target-worker.json").read_text()):
            raise ValueError("Native worker report changed")
        event, = row["target_report"]["events"]
        expected_exit = 7 if cell.mode in {"nonzero_empty", "full_then_nonzero"} else 0
        if not event["completed"] or event["returncode"] != expected_exit:
            raise ValueError("Native actual process status contradicts authored condition")
        if row["target_report"]["llm_models"] or row["target_report"]["recorded_api_cost"] != 0:
            raise ValueError("Unexpected model use")
        evaluator_processes += 1
        prior_ids = {p["id"] for p in (row["primer"] or {"database": {"programs": []}})["database"]["programs"]}
        new = [p for p in observed["programs"] if p["id"] not in prior_ids]
        if new != [row["current"]]:
            raise ValueError("Native target persistence differs from database")
        if cell.history != "fresh":
            evaluator_processes += 1
            if cell.history == "interrupted":
                interrupted += 1
                evidence = json.loads((folder / "primer-interruption.json").read_text())
                if evidence != row["primer"] or evidence["worker_returncode"] != -15 or evidence["database"]["programs"]:
                    raise ValueError("Native interruption preconditions not satisfied")
            elif row["primer"] != json.loads((folder / "primer-worker.json").read_text()):
                raise ValueError("Native primer changed")
        if cell.policy == "bound":
            bundle_manifest = row["target_report"]["adapters"][0]["manifest"]
            verdict = verify_bundle(folder / "defense-attempt", expected_request_hash=bundle_manifest["request_hash"],
                                    expected_receipt_hash=bundle_manifest["receipt_hash"]).to_dict()
            if verdict != bundle_manifest["verdict"]:
                raise ValueError("Native bound receipt differs from replay")
    analysis = analyze_rows(rows)
    if analysis != json.loads((root / "analysis.json").read_text()):
        raise ValueError("Native analysis mismatch")
    if evaluator_processes != plan["max_evaluator_processes"]:
        raise ValueError("Native process accounting mismatch")
    return {"schema": SCHEMA, "cells": len(rows), "evaluator_processes": evaluator_processes,
            "interrupted_primers": interrupted, "native_databases": len(rows), "bound_receipts": 7,
            "model_calls": 0, "plan_hash": envelope["plan_hash"], "files_hash": manifest["files_hash"],
            "volatile_sqlite_shared_memory_excluded": volatile,
            "replay_note": "Database and WAL hashes verified; SQLite read-mark files excluded. See native-replay-amendment-013.json.",
            "analysis": analysis}
