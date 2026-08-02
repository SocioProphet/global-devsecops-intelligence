#!/usr/bin/env python3
"""GDI mesh consume->produce loop (GDI-2): the increment serve.py flagged as next.

Consumes telemetry AI4IT ``EventEnvelope``s from an inbox, validates them
fail-closed against the event-envelope contract, and produces ``/ops/findings``
RCA-claim EventEnvelopes to an outbox. This is the consume side of the live feed:
MeshRush (via agentplane's MeshRush adapter) emits ``meshrush_*`` events; GDI
ingests them here, normalizes, and turns the governance signal (e.g. refused
slots) into an ops finding.

Transport is a filesystem mailbox (MESH_INPUT_DIR / MESH_OUTPUT_DIR) — a real,
dependency-free minimal mesh; swap for a bus later without changing this contract.

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
from pathlib import Path

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


def consume_once(input_dir: Path, output_dir: Path, schema: dict, *, clock=_now_fields) -> dict:
    """Consume every *.json envelope in ``input_dir``; write findings to ``output_dir``.

    Returns stats ``{consumed, produced, rejected}``. Rejected envelopes are recorded
    in ``output_dir/_rejected.log`` with their errors; no finding is produced for them.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    processed_dir = output_dir / "_processed"
    rejected_dir = output_dir / "_rejected"
    stats = {"consumed": 0, "produced": 0, "rejected": 0}
    rejected_log: list[str] = []

    def _drain(path: Path, dest_dir: Path) -> None:
        # Move the source out of the inbox so a long-running loop consumes it once.
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / path.name
        if dest.exists():  # avoid clobbering on name reuse
            dest = dest_dir / f"{path.stem}.{hashlib.sha256(path.name.encode()).hexdigest()[:8]}{path.suffix}"
        os.replace(path, dest)

    for path in sorted(input_dir.glob("*.json")) if input_dir.exists() else []:
        stats["consumed"] += 1
        raw = path.read_bytes()
        try:
            event = json.loads(raw)
        except (json.JSONDecodeError, OSError) as exc:
            stats["rejected"] += 1
            rejected_log.append(f"{path.name}: unreadable/invalid JSON ({exc})")
            _drain(path, rejected_dir)
            continue
        errs = envelope_errors(event, schema)
        if errs:
            stats["rejected"] += 1
            rejected_log.append(f"{path.name}: {'; '.join(errs)}")
            _drain(path, rejected_dir)
            continue
        ts_ms, utc = clock()
        finding = _finding_for(event, ts_ms, utc)
        # Idempotent: derive the finding filename from the source event content.
        out = output_dir / f"finding-{hashlib.sha256(raw).hexdigest()[:16]}.json"
        if not out.exists():
            out.write_text(json.dumps(finding, indent=2) + "\n", encoding="utf-8")
            stats["produced"] += 1
        _drain(path, processed_dir)

    if rejected_log:
        with (output_dir / "_rejected.log").open("a", encoding="utf-8") as fh:
            fh.write("\n".join(rejected_log) + "\n")
    return stats


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
