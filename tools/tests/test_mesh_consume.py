import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mesh_consume import consume_once, envelope_errors  # noqa: E402

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


def test_malformed_envelope_is_rejected_not_findinged(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "bad.json", {"type": "MeshRush", "data": {}})  # missing timestamp/utc; bad type
    stats = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    assert stats["rejected"] == 1 and stats["produced"] == 0
    assert list(outbox.glob("finding-*.json")) == []
    assert (outbox / "_rejected.log").exists()


def test_idempotent_no_duplicate_findings(tmp_path):
    inbox, outbox = tmp_path / "in", tmp_path / "out"
    _write(inbox, "e1.json", _valid_slot_fill())
    consume_once(inbox, outbox, SCHEMA, clock=CLOCK)
    stats2 = consume_once(inbox, outbox, SCHEMA, clock=CLOCK)  # re-run
    assert stats2["produced"] == 0  # already produced
    assert len(list(outbox.glob("finding-*.json"))) == 1
