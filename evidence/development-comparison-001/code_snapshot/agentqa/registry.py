"""Append-only candidate/attempt records and content-addressed frozen pools."""

import json
from pathlib import Path
import sqlite3

from .contracts import canonical, digest


class RegistryError(ValueError):
    pass


class CandidateRegistry:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, isolation_level=None, timeout=10)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("""CREATE TABLE IF NOT EXISTS candidates (
            id TEXT PRIMARY KEY, parent TEXT REFERENCES candidates(id),
            source_hash TEXT NOT NULL, origin TEXT NOT NULL, program TEXT NOT NULL,
            program_hash TEXT NOT NULL, provenance TEXT NOT NULL)""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS attempts (
            id TEXT PRIMARY KEY, parent TEXT NOT NULL REFERENCES candidates(id),
            source_hash TEXT NOT NULL, status TEXT NOT NULL, details TEXT NOT NULL)""")
        self.db.execute("CREATE TABLE IF NOT EXISTS pools (id TEXT PRIMARY KEY, manifest TEXT NOT NULL)")
        # These are application guardrails against accidental mutation, not an attacker-proof database.
        for table in ("candidates", "pools"):
            for operation in ("UPDATE", "DELETE"):
                self.db.execute(f"""CREATE TRIGGER IF NOT EXISTS immutable_{table}_{operation}
                    BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable record'); END""")
        self.db.execute("""CREATE TRIGGER IF NOT EXISTS immutable_attempt_delete
            BEFORE DELETE ON attempts BEGIN SELECT RAISE(ABORT, 'immutable attempt'); END""")
        self.db.execute("""CREATE TRIGGER IF NOT EXISTS immutable_finished_attempt
            BEFORE UPDATE ON attempts WHEN OLD.status != 'pending'
            BEGIN SELECT RAISE(ABORT, 'finished attempt'); END""")

    def close(self):
        self.db.close()

    def add(self, candidate_id: str, program: str, *, parent: str | None,
            source_hash: str, origin: str, provenance: dict) -> dict:
        if (not candidate_id or not isinstance(program, str) or not program.strip()
                or len(program.encode()) > 16000 or len(source_hash) != 64
                or origin not in {"authored-control", "model-generated", "unseeded-model-generated"}):
            raise RegistryError("Invalid candidate identity, source, origin, or program")
        try:
            self.db.execute("INSERT INTO candidates VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (candidate_id, parent, source_hash, origin, program,
                             digest(program), canonical(provenance).decode()))
        except sqlite3.IntegrityError as exc:
            raise RegistryError(f"Candidate exists or parent is missing: {candidate_id}") from exc
        return self.get(candidate_id)

    def get(self, candidate_id: str) -> dict:
        row = self.db.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone()
        if row is None:
            raise RegistryError("Unknown candidate")
        result = dict(zip(("id", "parent", "source_hash", "origin", "program", "program_hash", "provenance"), row))
        result["provenance"] = json.loads(result["provenance"])
        if digest(result["program"]) != result["program_hash"]:
            raise RegistryError("Candidate program differs from frozen hash")
        return result

    def begin_attempt(self, attempt_id: str, *, parent: str, source_hash: str, details: dict):
        try:
            self.db.execute("INSERT INTO attempts VALUES (?, ?, ?, 'pending', ?)",
                            (attempt_id, parent, source_hash, canonical(details).decode()))
        except sqlite3.IntegrityError as exc:
            raise RegistryError("Attempt already exists or parent is missing") from exc

    def finish_attempt(self, attempt_id: str, status: str, details: dict):
        if status not in {"completed", "invalid", "failed", "timeout"}:
            raise RegistryError("Invalid attempt status")
        row = self.db.execute("SELECT status, details FROM attempts WHERE id=?", (attempt_id,)).fetchone()
        if row is None or row[0] != "pending":
            raise RegistryError("Attempt missing or already finalized")
        record = {"request": json.loads(row[1]), "result": details}
        self.db.execute("UPDATE attempts SET status=?, details=? WHERE id=?",
                        (status, canonical(record).decode(), attempt_id))

    def freeze(self, pool_id: str, candidate_ids: list[str], *, parent: str) -> dict:
        if parent not in candidate_ids or len(set(candidate_ids)) != len(candidate_ids):
            raise RegistryError("Pool requires parent and unique candidate identities")
        candidates = [self.get(name) for name in sorted(candidate_ids)]
        source = {candidate["source_hash"] for candidate in candidates}
        if len(source) != 1:
            raise RegistryError("A source-conditioned pool cannot mix source identities")
        if any(candidate["id"] != parent and candidate["parent"] not in candidate_ids for candidate in candidates):
            raise RegistryError("Pool is missing candidate ancestry")
        attempts = [dict(zip(("id", "parent", "source_hash", "status", "details"), row))
                    for row in self.db.execute("SELECT * FROM attempts ORDER BY id")
                    if row[1] in candidate_ids and row[2] in source]
        for attempt in attempts:
            attempt["details"] = json.loads(attempt["details"])
        if any(attempt["status"] == "pending" for attempt in attempts):
            raise RegistryError("Cannot freeze a pool while generation attempts remain pending")
        body = {"schema": "agentqa.pool.v1", "id": pool_id, "parent": parent,
                "candidates": candidates, "attempts": attempts}
        manifest = {**body, "hash": digest(body)}
        try:
            self.db.execute("INSERT INTO pools VALUES (?, ?)", (pool_id, canonical(manifest).decode()))
        except sqlite3.IntegrityError as exc:
            raise RegistryError("Pool identity already frozen") from exc
        return manifest


def validate_pool(manifest: dict) -> None:
    body = {key: value for key, value in manifest.items() if key != "hash"}
    if manifest.get("schema") != "agentqa.pool.v1" or digest(body) != manifest.get("hash"):
        raise RegistryError("Pool manifest integrity failure")
    candidates = manifest.get("candidates", [])
    names = [candidate["id"] for candidate in candidates]
    if len(names) != len(set(names)) or manifest.get("parent") not in names:
        raise RegistryError("Invalid frozen pool membership")
    for candidate in candidates:
        if digest(candidate["program"]) != candidate["program_hash"]:
            raise RegistryError("Frozen program integrity failure")
