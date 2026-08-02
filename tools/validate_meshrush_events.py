#!/usr/bin/env python3
"""Validate MeshRush-emitted AI4IT events against GDI's event-envelope + topic registry.

MeshRush is a signal source for GDI (ops-intelligence normalizer/query plane): it
emits cairnpath walks and slot-fill results (with epistemic level + refusals) as
AI4IT events. This validator makes GDI's ingest contract for those events explicit
and enforced — it runs in ``make validate``, which CI runs, every image build runs,
and ``serve.py`` runs continuously, so the MeshRush event class is auto-checked on
every build and rollout.

Dependency-light on purpose (matches the other GDI validators): stdlib only, no
jsonschema/pyyaml. It (1) enforces the event-envelope's required fields, snake_case
``type`` pattern, and additionalProperties:false against each fixture; (2) checks
each event ``type`` is a registered MeshRush topic in topics.yaml (token presence);
and (3) recomputes the slot-fill counts so a mislabeled example cannot pass.
"""
from __future__ import annotations

import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "open-ai4it-spec/contracts/schemas/event-envelope.schema.json"
TOPICS = ROOT / "open-ai4it-spec/contracts/topics/topics.yaml"
EVENTS = [
    ROOT / "examples/meshrush-slot-fill.event.json",
    ROOT / "examples/meshrush-cairnpath-walk.event.json",
]
# MeshRush event type -> its registered topic string (must appear in topics.yaml).
MESHRUSH_TOPICS = {
    "meshrush_slot_fill": "derived-meshrush-slot-fill",
    "meshrush_cairnpath_walk": "raw-meshrush-cairnpath-walk",
}
_TYPE_RE = re.compile(r"^[a-z0-9_]+$")


def _fail(msg: str) -> None:
    raise ValueError(msg)


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _validate_envelope(event: dict, schema: dict, label: str) -> None:
    props = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in event:
            _fail(f"{label}: missing required '{key}'")
    if schema.get("additionalProperties") is False:
        extra = sorted(set(event) - set(props))
        if extra:
            _fail(f"{label}: unexpected fields {extra} (additionalProperties:false)")
    if not isinstance(event["timestamp"], int) or isinstance(event["timestamp"], bool):
        _fail(f"{label}: timestamp must be an integer (POSIX ms)")
    if not isinstance(event["utc_timestamp"], str) or not event["utc_timestamp"]:
        _fail(f"{label}: utc_timestamp must be a non-empty string")
    if not _TYPE_RE.fullmatch(event["type"]):
        _fail(f"{label}: type {event['type']!r} must match ^[a-z0-9_]+$")
    # Cross-check the two time fields agree (internally consistent event time).
    try:
        dt = datetime.datetime.fromisoformat(event["utc_timestamp"].replace("Z", "+00:00"))
    except ValueError:
        _fail(f"{label}: utc_timestamp is not an RFC3339/ISO-8601 date-time")
    expected_ms = int(dt.timestamp() * 1000)
    if abs(expected_ms - event["timestamp"]) > 1000:
        _fail(f"{label}: timestamp {event['timestamp']} disagrees with utc_timestamp ({expected_ms})")


def main() -> int:
    try:
        schema = _load(SCHEMA)
        topics_text = TOPICS.read_text(encoding="utf-8")
        for path in EVENTS:
            event = _load(path)
            label = path.name
            _validate_envelope(event, schema, label)

            etype = event["type"]
            if etype not in MESHRUSH_TOPICS:
                _fail(f"{label}: unknown MeshRush event type {etype!r}")
            topic = MESHRUSH_TOPICS[etype]
            # Match a real YAML list entry, not any substring (avoid comment false-positives).
            if not re.search(rf"^\s*-\s*{re.escape(topic)}\s*$", topics_text, re.MULTILINE):
                _fail(f"{label}: topic {topic!r} for type {etype!r} not registered as a topics.yaml list entry")

            # Semantic check: a slot-fill's stated counts must match its arrays
            # (a mislabeled example must not pass — the estate's declared-not-checked rule).
            if etype == "meshrush_slot_fill":
                d = event.get("data", {})
                fills, refused = d.get("fills"), d.get("refused")
                if not isinstance(fills, list) or not isinstance(refused, list):
                    _fail(f"{label}: data.fills and data.refused must be lists")
                if d.get("n_filled") != len(fills):
                    _fail(f"{label}: n_filled != len(fills)")
                if d.get("n_refused") != len(refused):
                    _fail(f"{label}: n_refused != len(refused)")
    except (ValueError, OSError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: MeshRush event ingest validated ({len(EVENTS)} events, {len(MESHRUSH_TOPICS)} topics)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
