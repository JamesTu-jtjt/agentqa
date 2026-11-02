"""Transactional cost reservation and immutable trial identities for resumable work."""

from decimal import Decimal
import json
from pathlib import Path
import sqlite3


class BudgetError(RuntimeError):
    pass


def micros(amount: str | Decimal) -> int:
    value = Decimal(amount)
    if not value.is_finite() or value < 0 or value * 1_000_000 != (value * 1_000_000).to_integral_value():
        raise ValueError("Use nonnegative USD amounts with at most six decimals")
    return int(value * 1_000_000)


class Ledger:
    def __init__(self, path: Path, *, cap_usd: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path, timeout=10, isolation_level=None)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("CREATE TABLE IF NOT EXISTS settings (id INTEGER PRIMARY KEY, cap INTEGER)")
        self.connection.execute("""CREATE TABLE IF NOT EXISTS trials (
            id TEXT PRIMARY KEY, status TEXT NOT NULL, reserved INTEGER NOT NULL,
            charged INTEGER, metadata TEXT NOT NULL, outcome TEXT)""")
        self.connection.execute("INSERT OR IGNORE INTO settings VALUES (1, ?)", (micros(cap_usd),))
        if self.connection.execute("SELECT cap FROM settings WHERE id=1").fetchone()[0] != micros(cap_usd):
            self.connection.close()
            raise BudgetError("Cannot silently change the recorded spending cap")

    def close(self):
        self.connection.close()

    def reserve(self, trial_id: str, upper_bound_usd: str, metadata: dict) -> None:
        if not trial_id:
            raise ValueError("Trial ID is required")
        amount = micros(upper_bound_usd)
        encoded = json.dumps(metadata, sort_keys=True, allow_nan=False)
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            if self.connection.execute("SELECT 1 FROM trials WHERE id=?", (trial_id,)).fetchone():
                raise BudgetError("Trial already exists; do not duplicate or silently retry it")
            cap = self.connection.execute("SELECT cap FROM settings WHERE id=1").fetchone()[0]
            committed = self.connection.execute(
                "SELECT COALESCE(SUM(COALESCE(charged, reserved)), 0) FROM trials").fetchone()[0]
            if committed + amount > cap:
                raise BudgetError("Insufficient unreserved budget")
            self.connection.execute("INSERT INTO trials VALUES (?, 'reserved', ?, NULL, ?, NULL)",
                                    (trial_id, amount, encoded))
            self.connection.execute("COMMIT")
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise

    def finish(self, trial_id: str, *, status: str, actual_usd: str | None, outcome: dict) -> None:
        if status not in {"completed", "task_failed", "infrastructure_failed", "usage_unknown"}:
            raise ValueError("Unsupported terminal status")
        if actual_usd is None and status != "usage_unknown":
            raise ValueError("Missing actual usage must remain explicitly unknown")
        encoded = json.dumps(outcome, sort_keys=True, allow_nan=False)
        actual = micros(actual_usd) if actual_usd is not None else None
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute("SELECT status, reserved FROM trials WHERE id=?", (trial_id,)).fetchone()
            if not row or row[0] != "reserved":
                raise BudgetError("Trial missing or already finalized")
            # Preserve even unexpectedly excessive provider charges; never hide overspend.
            charge = actual if actual is not None else row[1]
            self.connection.execute("UPDATE trials SET status=?, charged=?, outcome=? WHERE id=?",
                                    (status, charge, encoded, trial_id))
            self.connection.execute("COMMIT")
        except BaseException:
            self.connection.execute("ROLLBACK")
            raise

    def snapshot(self) -> dict:
        cap = self.connection.execute("SELECT cap FROM settings WHERE id=1").fetchone()[0]
        rows = self.connection.execute("SELECT id, status, reserved, charged, metadata, outcome FROM trials ORDER BY id").fetchall()
        committed = sum(row[3] if row[3] is not None else row[2] for row in rows)
        return {"cap_microusd": cap, "committed_microusd": committed,
                "remaining_microusd": max(0, cap - committed),
                "over_cap": committed > cap,
                "trials": [{"id": r[0], "status": r[1], "reserved_microusd": r[2],
                            "charged_microusd": r[3], "metadata": json.loads(r[4]),
                            "outcome": json.loads(r[5]) if r[5] else None} for r in rows]}
