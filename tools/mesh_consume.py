#!/usr/bin/env python3
"""GDI mesh consume->produce loop (GDI-2): the increment serve.py flagged as next.

Consumes telemetry AI4IT ``EventEnvelope``s from an inbox, validates them
fail-closed against the event-envelope contract, and produces ``/ops/findings``
RCA-claim EventEnvelopes to an outbox. This is the consume side of the live feed:
MeshRush (via agentplane's MeshRush adapter) emits ``meshrush_*`` events; GDI
ingests them here, normalizes, and turns the governance signal (e.g. refused
slots) into an ops finding.

Transport is **pluggable** (``MeshTransport``, GDI-2b): the default
``FilesystemMailbox`` (MESH_INPUT_DIR / MESH_OUTPUT_DIR) is a real, dependency-free
minimal mesh; ``InMemoryBus`` is an in-process message bus and the **agentplane
live-wire seam** — agentplane's MeshRush adapter calls ``publish_telemetry`` and GDI
drains it with the *same* ``consume`` contract. A networked bus (NATS/Redis/Kafka)
is a further transport behind this same interface — no heavy broker dependency is
pinned into GDI (sovereign, dependency-light).

Fail-closed: an envelope that does not conform is rejected (recorded, no finding
produced) — a malformed telemetry item can never silently become a finding.
Idempotent: a finding's name is derived from the source event, so re-running the
loop does not duplicate findings.

Stdlib only (matches the repo's dependency-light validators).
"""
from __future__ import annotations

import datetime
import hashlib
import json
import os
import re
import sys
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Protocol

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "open-ai4it-spec/contracts/schemas/event-envelope.schema.json"
_TYPE_RE = re.compile(r"^[a-z0-9_]+$")

# MeshRush event types whose governance signal we surface as findings.
_REFUSAL_SOURCE = "meshrush_slot_fill"


def _now_fields() -> "tuple[int, str]":
    dt = datetime.datetime.now(datetime.timezone.utc)
    return int(dt.timestamp() * 1000), dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def envelope_errors(event: object, schema: dict) -> list[str]:
    """Fail-closed structural validation against the event-envelope (stdlib)."""
    errs: list[str] = []
    if not isinstance(event, dict):
        return ["event is not an object"]
    props = schema.get("properties", {})
    for key in schema.get("required", []):
        if key not in event:
            errs.append(f"missing required '{key}'")
    if schema.get("additionalProperties") is False:
        extra = sorted(set(event) - set(props))
        if extra:
            errs.append(f"unexpected fields {extra}")
    ts_ok = "timestamp" in event and isinstance(event["timestamp"], int) and not isinstance(event["timestamp"], bool)
    if "timestamp" in event and not ts_ok:
        errs.append("timestamp must be an integer")
    if "type" in event and not (isinstance(event["type"], str) and _TYPE_RE.fullmatch(event["type"])):
        errs.append("type must match ^[a-z0-9_]+$")
    utc = event.get("utc_timestamp")
    utc_ok = isinstance(utc, str) and bool(utc)
    if "utc_timestamp" in event and not utc_ok:
        errs.append("utc_timestamp must be a non-empty string")
    # Cross-check the two time fields agree (internally consistent event time),
    # matching the stricter validation in tools/validate_meshrush_events.py.
    if ts_ok and utc_ok:
        try:
            dt = datetime.datetime.fromisoformat(utc.replace("Z", "+00:00"))
            if abs(int(dt.timestamp() * 1000) - event["timestamp"]) > 1000:
                errs.append("timestamp disagrees with utc_timestamp")
        except ValueError:
            errs.append("utc_timestamp is not an RFC3339/ISO-8601 date-time")
    return errs


def _finding_for(event: dict, ts_ms: int, utc: str) -> dict:
    """Build an /ops/findings RCA-claim EventEnvelope from a consumed event."""
    src_type = event["type"]
    story = event.get("story_id")
    data = event.get("data", {}) if isinstance(event.get("data"), dict) else {}
    severity, summary = "info", f"observed {src_type}"
    signal: dict = {"source_type": src_type}

    if src_type == _REFUSAL_SOURCE:
        n_refused = data.get("n_refused", 0)
        signal["n_refused"] = n_refused
        signal["n_filled"] = data.get("n_filled", 0)
        if isinstance(n_refused, int) and n_refused > 0:
            severity = "warn"
            summary = f"{n_refused} slot(s) refused during retrieval (governed abstention)"
            signal["refused"] = data.get("refused", [])

    finding = {
        "timestamp": ts_ms,
        "utc_timestamp": utc,
        "type": "ops_finding",
        "data_name": "rca_claim",
        "data": {"severity": severity, "summary": summary, "signal": signal, "source_event_type": src_type},
    }
    if story is not None:
        finding["story_id"] = story
    return finding


def _dedup_key(raw: "bytes | str") -> str:
    """Content id of a source event — the idempotency key for its finding."""
    data = raw if isinstance(raw, bytes) else raw.encode("utf-8")
    return hashlib.sha256(data).hexdigest()[:16]


class MeshTransport(Protocol):
    """The consume-loop's transport contract. A filesystem mailbox, an in-process
    bus, or a networked broker all satisfy it; ``consume`` is identical over any."""

    def poll(self) -> "list[tuple[str, bytes]]":
        """Return pending ``(message_id, raw_bytes)`` telemetry, oldest first."""

    def ack(self, message_id: str) -> None:
        """Mark a message consumed (it must not be polled again)."""

    def reject(self, message_id: str, reason: str) -> None:
        """Mark a message rejected (recorded, removed from the inbox)."""

    def publish_finding(self, finding: dict, *, dedup_key: str) -> "tuple[str, bool]":
        """Publish a finding idempotently by ``dedup_key``; return ``(id, created)``."""


class FilesystemMailbox:
    """A ``MeshTransport`` over a directory pair (the GDI-2 default). Telemetry is
    ``input_dir/*.json``; findings and drained sources land under ``output_dir``."""

    def __init__(self, input_dir: Path, output_dir: Path) -> None:
        self.input_dir = input_dir
        self.output_dir = output_dir
        self._pending: "dict[str, Path]" = {}

    def poll(self) -> "list[tuple[str, bytes]]":
        out: "list[tuple[str, bytes]]" = []
        if not self.input_dir.exists():
            return out
        for path in sorted(self.input_dir.glob("*.json")):
            self._pending[path.name] = path
            out.append((path.name, path.read_bytes()))
        return out

    def _drain(self, message_id: str, subdir: str) -> None:
        path = self._pending.pop(message_id, None)
        if path is None or not path.exists():
            return
        dest_dir = self.output_dir / subdir
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / path.name
        if dest.exists():  # avoid clobbering on name reuse
            dest = dest_dir / f"{path.stem}.{hashlib.sha256(path.name.encode()).hexdigest()[:8]}{path.suffix}"
        os.replace(path, dest)

    def ack(self, message_id: str) -> None:
        self._drain(message_id, "_processed")

    def reject(self, message_id: str, reason: str) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        with (self.output_dir / "_rejected.log").open("a", encoding="utf-8") as fh:
            fh.write(f"{message_id}: {reason}\n")
        self._drain(message_id, "_rejected")

    def publish_finding(self, finding: dict, *, dedup_key: str) -> "tuple[str, bool]":
        self.output_dir.mkdir(parents=True, exist_ok=True)
        out = self.output_dir / f"finding-{dedup_key}.json"
        created = not out.exists()
        if created:
            out.write_text(json.dumps(finding, indent=2) + "\n", encoding="utf-8")
        return out.name, created


class InMemoryBus:
    """A thread-safe, dependency-free in-process ``MeshTransport`` — the agentplane
    live-wire seam. agentplane's MeshRush adapter calls ``publish_telemetry``; GDI
    drains it via ``consume``. The same contract fronts a networked broker later."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._inbox: "OrderedDict[str, bytes]" = OrderedDict()
        self._findings: "OrderedDict[str, dict]" = OrderedDict()
        self._rejected: "list[tuple[str, str]]" = []
        self._seq = 0

    def publish_telemetry(self, raw: "bytes | str") -> str:
        """Publish a telemetry envelope onto the bus (the producer/agentplane side)."""
        data = raw if isinstance(raw, bytes) else raw.encode("utf-8")
        with self._lock:
            message_id = f"msg-{self._seq}"
            self._seq += 1
            self._inbox[message_id] = data
        return message_id

    def poll(self) -> "list[tuple[str, bytes]]":
        with self._lock:
            return list(self._inbox.items())

    def ack(self, message_id: str) -> None:
        with self._lock:
            self._inbox.pop(message_id, None)

    def reject(self, message_id: str, reason: str) -> None:
        with self._lock:
            self._inbox.pop(message_id, None)
            self._rejected.append((message_id, reason))

    def publish_finding(self, finding: dict, *, dedup_key: str) -> "tuple[str, bool]":
        with self._lock:
            created = dedup_key not in self._findings
            if created:
                self._findings[dedup_key] = finding
        return dedup_key, created

    def findings(self) -> "list[dict]":
        """All findings published so far (deduped), in first-seen order."""
        with self._lock:
            return list(self._findings.values())

    def rejected(self) -> "list[tuple[str, str]]":
        """All ``(message_id, reason)`` rejections so far."""
        with self._lock:
            return list(self._rejected)


def consume(transport: MeshTransport, schema: dict, *, clock=_now_fields) -> dict:
    """Drain ``transport``'s pending telemetry into findings, fail-closed + idempotent.

    Returns stats ``{consumed, produced, rejected}``. A malformed or non-conforming
    envelope is rejected (no finding); a finding is published idempotently by the
    source event's content, so re-draining never duplicates.
    """
    stats = {"consumed": 0, "produced": 0, "rejected": 0}
    for message_id, raw in transport.poll():
        stats["consumed"] += 1
        try:
            event = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            stats["rejected"] += 1
            transport.reject(message_id, f"unreadable/invalid JSON ({exc})")
            continue
        errs = envelope_errors(event, schema)
        if errs:
            stats["rejected"] += 1
            transport.reject(message_id, "; ".join(errs))
            continue
        ts_ms, utc = clock()
        finding = _finding_for(event, ts_ms, utc)
        _, created = transport.publish_finding(finding, dedup_key=_dedup_key(raw))
        if created:
            stats["produced"] += 1
        transport.ack(message_id)
    return stats


def consume_once(input_dir: Path, output_dir: Path, schema: dict, *, clock=_now_fields) -> dict:
    """Consume every *.json envelope in ``input_dir``; write findings to ``output_dir``.

    Back-compat wrapper over ``consume`` with a ``FilesystemMailbox`` transport.
    """
    return consume(FilesystemMailbox(input_dir, output_dir), schema, clock=clock)


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    inbox = Path(os.environ.get("MESH_INPUT_DIR", str(ROOT / "mesh" / "telemetry")))
    outbox = Path(os.environ.get("MESH_OUTPUT_DIR", str(ROOT / "mesh" / "ops-findings")))
    stats = consume_once(inbox, outbox, schema)
    # Machine-readable stats line for serve.py (robust; not regex-parsed prose).
    print("STATS " + json.dumps(stats, sort_keys=True))
    print(f"OK: mesh consume — consumed={stats['consumed']} produced={stats['produced']} rejected={stats['rejected']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
