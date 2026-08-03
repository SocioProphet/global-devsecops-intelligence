import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mesh_consume import (  # noqa: E402
    InMemoryBus,
    consume,
    consume_once,
    envelope_errors,
)

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "open-ai4it-spec/contracts/schemas/event-envelope.schema.json").read_text())
CLOCK = lambda: (1785628800000, "2026-08-02T00:00:00.000Z")


def _write(d: Path, name: str, obj: dict) -> None:
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(json.dumps(obj), encoding="utf-8")


def _valid_slot_fill(n_refused=1):
    return {
        "timestamp": 1785628800000, "utc_timestamp": "2026-08-02T00:00:00.000Z",
        "type": "meshrush_slot_fill", "story_id": "s1",
        "data": {"n_filled": 1, "n_refused": n_refused, "fills": [], "refused": [{"slot": "pricing", "reason": "floor"}]},
    }


def test_consumes_valid_event_and_produces_finding(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "e1.json", _valid_slot_fill())
    stats = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    assert stats == {"consumed": 1, "produced": 1, "rejected": 0}
    findings = list(outbox.glob("finding-*.json"))
    assert len(findings) == 1
    finding = json.loads(findings[0].read_text())
    # The produced finding is itself a valid EventEnvelope.
    assert envelope_errors(finding, SCHEMA) == []
    # Refusals are surfaced as a warn-severity governance signal.
    assert finding["type"] == "ops_finding"
    assert finding["data"]["severity"] == "warn"
    assert "refused" in finding["data"]["summary"]
    assert finding["data"]["signal"]["n_refused"] == 1


def test_no_refusals_is_info_severity(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "e1.json", _valid_slot_fill(n_refused=0))
    consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    finding = json.loads(next(outbox.glob("finding-*.json")).read_text())
    assert finding["data"]["severity"] == "info"


def test_malformed_envelope_is_rejected_not_turned_into_finding(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "bad.json", {"type": "MeshRush", "data": {}})  # missing timestamp/utc; bad type
    stats = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    assert stats["rejected"] == 1 and stats["produced"] == 0
    assert list(outbox.glob("finding-*.json")) == []
    assert (outbox / "_rejected.log").exists()
    assert (outbox / "_rejected" / "bad.json").exists()  # drained out of the inbox


def test_timestamp_utc_mismatch_is_rejected(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    ev = _valid_slot_fill()
    ev["utc_timestamp"] = "2099-01-01T00:00:00.000Z"  # disagrees with timestamp
    _write(inbox, "skew.json", ev)
    stats = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    assert stats["rejected"] == 1 and stats["produced"] == 0


def test_inbox_is_drained_so_reruns_do_not_reconsume(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "e1.json", _valid_slot_fill())
    consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    stats2 = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)  # re-run: inbox drained
    assert stats2 == {"consumed": 0, "produced": 0, "rejected": 0}
    assert len(list(outbox.glob("finding-*.json"))) == 1
    assert (outbox / "_processed" / "e1.json").exists()


# --- GDI-2b: pluggable transport / in-process bus (agentplane live wire) --------

def test_inmemory_bus_valid_produces_finding_and_acks():
    bus = InMemoryBus()
    bus.publish_telemetry(json.dumps(_valid_slot_fill()))  # agentplane producer side
    stats = consume(bus, SCHEMA, clock=CLOCK)
    assert stats == {"consumed": 1, "produced": 1, "rejected": 0}
    findings = bus.findings()
    assert len(findings) == 1
    assert findings[0]["data"]["severity"] == "warn"
    assert envelope_errors(findings[0], SCHEMA) == []
    assert bus.poll() == []  # acked -> not re-polled


def test_inmemory_bus_malformed_is_rejected_not_a_finding():
    bus = InMemoryBus()
    bus.publish_telemetry(json.dumps({"type": "MeshRush", "data": {}}))  # missing/invalid fields
    stats = consume(bus, SCHEMA, clock=CLOCK)
    assert stats["rejected"] == 1 and stats["produced"] == 0
    assert bus.findings() == []
    assert len(bus.rejected()) == 1


def test_inmemory_bus_is_idempotent_across_identical_events():
    bus = InMemoryBus()
    payload = json.dumps(_valid_slot_fill())
    bus.publish_telemetry(payload)
    bus.publish_telemetry(payload)  # identical content -> same dedup key
    stats = consume(bus, SCHEMA, clock=CLOCK)
    assert stats["consumed"] == 2
    assert stats["produced"] == 1  # deduped: one finding only
    assert len(bus.findings()) == 1


def test_bus_and_mailbox_agree_over_the_same_contract(tmp_path):
    # the swap-the-transport promise: identical stats over either transport.
    ev = _valid_slot_fill()
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "e1.json", ev)
    fs_stats = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    bus = InMemoryBus()
    bus.publish_telemetry(json.dumps(ev))
    bus_stats = consume(bus, SCHEMA, clock=CLOCK)
    assert fs_stats == bus_stats == {"consumed": 1, "produced": 1, "rejected": 0}
