from decimal import Decimal

import pytest

from agentqa.ledger import BudgetError, Ledger
from agentqa.selection import Outcome, select


def test_regression_gate_rejects_high_scoring_regression():
    candidates = ["parent", "good", "bad"]
    selection = [Outcome(c, "s", 0, c != "parent", False) for c in candidates]
    regression = [Outcome(c, "r", 0, c != "bad", c == "bad") for c in candidates]
    result = select("parent", selection, regression)
    assert result["selected"] == "good"
    assert result["excluded"] == ["bad"]


def test_cost_then_identifier_breaks_ties():
    candidates = ["parent", "a", "b"]
    selection = [Outcome(c, "s", 0, True, False, Decimal("2" if c == "parent" else "1")) for c in candidates]
    regression = [Outcome(c, "r", 0, True, False) for c in candidates]
    assert select("parent", selection, regression)["selected"] == "a"


def test_parent_retained_if_all_children_regress():
    selection = [Outcome("parent", "s", 0, False, False), Outcome("child", "s", 0, True, False)]
    regression = [Outcome("parent", "r", 0, True, False), Outcome("child", "r", 0, False, False)]
    assert select("parent", selection, regression)["selected"] == "parent"


def test_partial_or_duplicate_trials_rejected():
    selection = [Outcome("parent", "s", 0, True, False), Outcome("child", "s", 1, True, False)]
    regression = [Outcome(c, "r", 0, True, False) for c in ["parent", "child"]]
    with pytest.raises(ValueError):
        select("parent", selection, regression)
    with pytest.raises(ValueError):
        select("parent", selection[:1] * 2, regression[:1])


def test_reservations_are_shared_between_connections_and_survive_restart(tmp_path):
    path = tmp_path / "ledger.db"
    first = Ledger(path, cap_usd="1")
    second = Ledger(path, cap_usd="1")
    first.reserve("t1", "0.7", {"kind": "pilot"})
    with pytest.raises(BudgetError):
        second.reserve("t2", "0.4", {})
    first.finish("t1", status="completed", actual_usd="0.2", outcome={"verified": False})
    second.reserve("t2", "0.4", {})
    first.close()
    second.close()
    reopened = Ledger(path, cap_usd="1")
    assert reopened.snapshot()["committed_microusd"] == 600000
    with pytest.raises(BudgetError):
        reopened.reserve("t1", "0.1", {})
    reopened.close()


def test_unknown_usage_retains_reservation(tmp_path):
    ledger = Ledger(tmp_path / "ledger.db", cap_usd="1")
    ledger.reserve("lost", "1", {})
    ledger.finish("lost", status="usage_unknown", actual_usd=None, outcome={"reason": "transport lost"})
    assert ledger.snapshot()["remaining_microusd"] == 0
    with pytest.raises(BudgetError):
        ledger.reserve("retry", "0.01", {"retry_of": "lost"})
    ledger.close()


def test_overspend_is_recorded_and_prevents_more_calls(tmp_path):
    ledger = Ledger(tmp_path / "ledger.db", cap_usd="1")
    ledger.reserve("expensive", "0.9", {})
    ledger.finish("expensive", status="completed", actual_usd="1.1", outcome={})
    assert ledger.snapshot()["over_cap"]
    with pytest.raises(BudgetError):
        ledger.reserve("another", "0", {})
    ledger.close()


def test_cannot_change_cap_or_finish_twice(tmp_path):
    path = tmp_path / "ledger.db"
    ledger = Ledger(path, cap_usd="0")
    ledger.reserve("offline", "0", {})
    ledger.finish("offline", status="completed", actual_usd="0", outcome={})
    with pytest.raises(BudgetError):
        ledger.finish("offline", status="completed", actual_usd="0", outcome={})
    with pytest.raises(BudgetError):
        Ledger(path, cap_usd="100")
    ledger.close()
