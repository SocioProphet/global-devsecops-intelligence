"""Teeth tests for the incident-similarity contract (AI4IT Pipeline 3).

These pin the scorer and its validator in both directions:
  * the committed validator passes on the golden fixtures;
  * the scorer is deterministic and its receipt verifies;
  * malformed inputs are refused;
  * a perturbed golden is detected as drift (the gate can fail).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_incident_similarity.py"
SCORER_PATH = (
    ROOT / "open-ai4it-spec" / "modules" / "story_services" / "incident_similarity" / "scorer.py"
)
EX = ROOT / "examples" / "incident-similarity"


def _load_scorer():
    spec = importlib.util.spec_from_file_location("isim_scorer_under_test", SCORER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def test_validator_passes_on_golden():
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr


def test_scorer_reproduces_golden_and_is_deterministic():
    scorer = _load_scorer()
    query = _json(EX / "query.example.json")
    corpus = _json(EX / "corpus.example.json")
    golden = _json(EX / "result.expected.json")

    first = scorer.score_incidents(query, corpus)
    second = scorer.score_incidents(query, corpus)
    assert _canonical(first) == _canonical(second), "scorer is not deterministic"
    assert _canonical(first) == _canonical(golden), "scorer drifted from the golden"


def test_receipt_hash_verifies_and_is_sha256():
    scorer = _load_scorer()
    golden = _json(EX / "result.expected.json")
    assert golden["receipt"]["algorithm"] == "sha256"
    assert golden["receipt"]["trace_hash"].startswith("sha256:")
    assert len(golden["receipt"]["trace_hash"].split(":", 1)[1]) == 64


def test_verdicts_are_reprojectable():
    scorer = _load_scorer()
    query = _json(EX / "query.example.json")
    golden = _json(EX / "result.expected.json")
    thresholds = scorer._resolve_thresholds(query.get("thresholds"))
    for match in golden["matches"]:
        assert match["verdict"] == scorer.project_verdict(match["score"], thresholds)


@pytest.mark.parametrize(
    "fixture,args",
    [
        ("query-empty-terms.json", "query"),
        ("corpus-missing-id.json", "corpus"),
    ],
)
def test_scorer_refuses_malformed_inputs(fixture, args):
    scorer = _load_scorer()
    query = _json(EX / "query.example.json")
    corpus = _json(EX / "corpus.example.json")
    bad = _json(EX / "invalid" / fixture)
    with pytest.raises(Exception):
        if args == "query":
            scorer.score_incidents(bad, corpus)
        else:
            scorer.score_incidents(query, bad)


def test_perturbed_golden_is_detected(tmp_path):
    """Copy the tree's golden, perturb a score, confirm the validator fails."""
    scorer = _load_scorer()
    query = _json(EX / "query.example.json")
    corpus = _json(EX / "corpus.example.json")
    recomputed = scorer.score_incidents(query, corpus)
    tampered = _json(EX / "invalid" / "result-tampered-score.json")
    assert _canonical(tampered) != _canonical(recomputed)
