"""Host-owned event chain and offline replay (integrity, not authentication)."""

from copy import deepcopy
import json
from pathlib import Path
import re

from .contracts import CONTRACT, SCHEMA, Verdict, canonical, digest


class TraceError(ValueError):
    pass


class Recorder:
    def __init__(self, trial_id: str, metadata: dict):
        self.trial_id = trial_id
        self._events: list[dict] = []
        self.append("start", {"schema": SCHEMA, "contract": CONTRACT, **metadata})

    @property
    def events(self) -> list[dict]:
        return deepcopy(self._events)

    def append(self, kind: str, payload: dict) -> dict:
        if self._events and self._events[-1]["kind"] == "complete":
            raise TraceError("Completed trial is immutable")
        body = {"trial_id": self.trial_id, "seq": len(self._events), "kind": kind,
                "payload": deepcopy(payload),
                "previous": self._events[-1]["hash"] if self._events else "0" * 64}
        event = {**body, "hash": digest(body)}
        self._events.append(event)
        return deepcopy(event)

    def save(self, path: Path) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Never overwrite an existing trial, including a failed attempt.
        with path.open("xb") as stream:
            for event in self._events:
                stream.write(canonical(event) + b"\n")
        return self._events[-1]["hash"]


def validate_trace(events: list[dict], expected_tip: str | None = None) -> None:
    if not events:
        raise TraceError("Empty trace")
    previous = "0" * 64
    trial = events[0].get("trial_id")
    if not isinstance(trial, str) or not trial:
        raise TraceError("Missing trial identity")
    for index, event in enumerate(events):
        if set(event) != {"trial_id", "seq", "kind", "payload", "previous", "hash"}:
            raise TraceError("Unexpected event fields")
        body = {key: value for key, value in event.items() if key != "hash"}
        if (type(event["seq"]) is not int or event["seq"] != index
                or event["trial_id"] != trial or event["previous"] != previous
                or digest(body) != event["hash"]):
            raise TraceError("Broken event chain")
        if event["kind"] not in {"start", "state", "observation", "test", "complete"}:
            raise TraceError("Unknown event type")
        if not isinstance(event["payload"], dict):
            raise TraceError("Invalid event payload")
        payload = event["payload"]
        fingerprints = ({"state": ["fingerprint"], "test": ["before", "after"],
                         "complete": ["fingerprint"]}).get(event["kind"], [])
        for field in fingerprints:
            if not isinstance(payload.get(field), str) or not re.fullmatch(r"[a-f0-9]{64}", payload[field]):
                raise TraceError("Missing or invalid footprint identity")
        if event["kind"] == "test":
            if payload.get("purpose") not in ("visible", "functional"):
                raise TraceError("Invalid verification purpose")
            if payload.get("status") not in {"passed", "failed", "timeout", "infrastructure_error", "modified_during_test"}:
                raise TraceError("Invalid process status")
            if payload.get("returncode") is not None and type(payload["returncode"]) is not int:
                raise TraceError("Invalid process return code")
            if payload["status"] == "passed" and payload.get("returncode") != 0:
                raise TraceError("Passing process lacks a zero exit status")
        if index > 0 and event["kind"] == "start":
            raise TraceError("Duplicate start")
        if index < len(events) - 1 and event["kind"] == "complete":
            raise TraceError("Events after completion")
        previous = event["hash"]
    header = events[0]
    if (header["kind"] != "start" or header["payload"].get("schema") != SCHEMA
            or header["payload"].get("contract") != CONTRACT):
        raise TraceError("Unsupported trace contract")
    if expected_tip is not None and previous != expected_tip:
        raise TraceError("Trace does not match frozen manifest")


def evaluate(events: list[dict], expected_tip: str | None = None) -> Verdict:
    validate_trace(events, expected_tip)
    if events[-1]["kind"] != "complete":
        return Verdict(False, False, False, False, "incomplete")
    completion = events[-1]["payload"]
    if type(completion.get("declared")) is not bool:
        raise TraceError("Malformed completion")
    current = completion.get("fingerprint")
    states = [event for event in events if event["kind"] == "state"]
    if not states or current != states[-1]["payload"].get("fingerprint"):
        raise TraceError("Completion lacks a matching state snapshot")
    records = {event["hash"]: event for event in events if event["kind"] == "test"}

    def passes(record: dict | None, purpose: str) -> bool:
        if record is None:
            return False
        data = record["payload"]
        return (data.get("purpose") == purpose and data.get("status") == "passed"
                and type(data.get("returncode")) is int and data["returncode"] == 0
                and data.get("before") == current and data.get("after") == current)

    fresh = any(passes(record, "visible") for record in records.values())
    functional = passes(records.get(completion.get("functional_record")), "functional")
    declared = completion["declared"]
    if not declared:
        reason = "not_completed"
    elif not functional:
        reason = "functional_failure"
    elif not fresh:
        reason = "missing_fresh_evidence"
    else:
        reason = "verified"
    return Verdict(declared, functional, fresh, declared and functional and fresh, reason)


def replay(path: Path, expected_tip: str | None = None) -> Verdict:
    try:
        events = [json.loads(line) for line in path.read_text().splitlines()]
        return evaluate(events, expected_tip)
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise TraceError(f"Malformed trace: {exc}") from exc
