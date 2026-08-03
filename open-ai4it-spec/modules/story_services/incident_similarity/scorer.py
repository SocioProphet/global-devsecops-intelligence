#!/usr/bin/env python3
"""Deterministic incident-similarity scorer (Pipeline 3 of the AI4IT reference).

This is the sovereign, dependency-free equivalent of a Watson-AIOps-style
"Similar Incidents Service": given the free-text search terms an SRE types and a
corpus of prior incidents, rank the corpus by similarity and attach, for every
match, an explainability breakdown, an epistemic verdict (the estate "Assay"
ok/sad/bad projection), and a provenance receipt (SHA-256 trace hash,
FIPS-180-4 algorithm — not a FIPS-140 module claim).

Design constraints (why this is buildable now, and reviewable):
  * Pure Python standard library. No ML, no network, no wall-clock. Every input
    that could vary with time (recency) is supplied explicitly as ``as_of_utc``,
    so the same inputs always produce byte-identical output. That determinism is
    what the validator's teeth depend on.
  * Estate primitives reused, not reinvented:
      - receipt spine   -> ``build_receipt`` seals inputs+outputs under sha256,
                           mirroring sourceos-spec ReasoningReceipt.traceHash.
      - the Assay        -> ``project_verdict`` renders (method, score) -> ok/sad/bad
                           at display time, re-projectable if thresholds change.
      - HellGraph topology-> consumed as a per-candidate ``topology_distance``
                           (hop count from the query focus service); the scorer
                           stays offline and testable while the field is fed by
                           the live service topology graph in production.

The public surface is :func:`score_incidents`; the schemas in
``open-ai4it-spec/contracts/schemas/incident-similarity-{query,result}.schema.json``
are the wire contract and ``tools/validate_incident_similarity.py`` enforces that
this code, the committed golden result, the receipt, and the verdicts all agree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from typing import Any

SCHEMA_VERSION = "0.1.0"
RECEIPT_VERSION = "0.1.0"

# Rounding precision applied to every emitted float. Fixing this makes the JSON
# output reproducible across platforms/interpreters (no last-bit float drift),
# which is a precondition for the golden-file teeth in the validator.
PRECISION = 6

DEFAULT_WEIGHTS: dict[str, float] = {
    "lexical": 0.5,
    "entity_overlap": 0.2,
    "topology": 0.2,
    "recency": 0.1,
}

DEFAULT_THRESHOLDS: dict[str, float] = {
    # Assay projection bands over the final [0,1] score.
    "ok": 0.5,
    "sad": 0.2,
    # Minimum score for a candidate to appear in the ranked matches at all.
    "min_score": 0.0,
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _round(value: float) -> float:
    return round(float(value), PRECISION)


def normalize_tokens(text: str) -> set[str]:
    """Lowercase, split on non-alphanumeric, drop empties -> deterministic set."""
    return set(_TOKEN_RE.findall(text.lower()))


def _incident_text_tokens(incident: dict[str, Any]) -> set[str]:
    parts: list[str] = []
    for key in ("title", "summary"):
        value = incident.get(key)
        if isinstance(value, str):
            parts.append(value)
    for key in ("tags", "entities"):
        value = incident.get(key)
        if isinstance(value, list):
            parts.extend(str(item) for item in value)
    return normalize_tokens(" ".join(parts))


def _entity_tokens(incident: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for item in incident.get("entities", []) or []:
        tokens |= normalize_tokens(str(item))
    return tokens


def _jaccard(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    intersection = left & right
    if not intersection:
        return 0.0
    return len(intersection) / len(left | right)


def _parse_utc(value: Any) -> float | None:
    """Parse an RFC3339/ISO-8601 UTC timestamp to epoch seconds, or None.

    Deliberately strict and offline: no timezone database, no wall clock. A
    trailing ``Z`` is accepted; anything unparseable yields None (the recency
    signal then contributes 0 rather than guessing).
    """
    if not isinstance(value, str) or not value:
        return None
    import datetime as _dt

    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = _dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=_dt.timezone.utc)
    return parsed.timestamp()


def _signal_lexical(query_tokens: set[str], incident: dict[str, Any]) -> float:
    return _jaccard(query_tokens, _incident_text_tokens(incident))


def _signal_entity(query_tokens: set[str], incident: dict[str, Any]) -> float:
    return _jaccard(query_tokens, _entity_tokens(incident))


def _signal_topology(incident: dict[str, Any]) -> float:
    distance = incident.get("topology_distance")
    if not isinstance(distance, (int, float)) or isinstance(distance, bool):
        return 0.0
    if distance < 0:
        return 0.0
    return 1.0 / (1.0 + float(distance))


def _signal_recency(incident: dict[str, Any], as_of_epoch: float | None) -> float:
    if as_of_epoch is None:
        return 0.0
    opened = _parse_utc(incident.get("opened_utc"))
    if opened is None:
        return 0.0
    age_days = (as_of_epoch - opened) / 86400.0
    if age_days < 0:
        age_days = 0.0
    return 1.0 / (1.0 + age_days)


def _resolve_weights(overrides: Any) -> dict[str, float]:
    weights = dict(DEFAULT_WEIGHTS)
    if isinstance(overrides, dict):
        for key, value in overrides.items():
            if key in weights and isinstance(value, (int, float)) and not isinstance(value, bool):
                weights[key] = float(value)
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weights must sum to a positive value")
    return weights


def _resolve_thresholds(overrides: Any) -> dict[str, float]:
    thresholds = dict(DEFAULT_THRESHOLDS)
    if isinstance(overrides, dict):
        for key, value in overrides.items():
            if key in thresholds and isinstance(value, (int, float)) and not isinstance(value, bool):
                thresholds[key] = float(value)
    if not (thresholds["sad"] <= thresholds["ok"]):
        raise ValueError("threshold 'sad' must be <= 'ok'")
    return thresholds


def project_verdict(score: float, thresholds: dict[str, float]) -> dict[str, str]:
    """The Assay projection: render (method, score) -> ok/sad/bad at read time.

    Method is always ``computed`` here: the score comes from deterministic
    lexical/graph arithmetic, never from a generative model. Bands are supplied
    (not hard-coded) so history is re-projectable when calibration improves.
    """
    if score >= thresholds["ok"]:
        state = "ok"
    elif score >= thresholds["sad"]:
        state = "sad"
    else:
        state = "bad"
    return {"state": state, "method": "computed"}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build_receipt(
    query: dict[str, Any],
    corpus: list[dict[str, Any]],
    weights: dict[str, float],
    thresholds: dict[str, float],
    matches: list[dict[str, Any]],
) -> dict[str, Any]:
    """Seal the computation under a SHA-256 (FIPS-180-4 algorithm) trace hash.

    The hash covers the normalized query terms, the sorted corpus ids, the
    resolved weights/thresholds, and the ranked (id, score) result. Any tamper
    with inputs or the emitted ranking changes the hash — the validator recomputes
    it and fails on drift. This is the provenance receipt spine, offline and
    self-verifying (no signer, no external authority required).
    """
    sealed = {
        "query_terms": sorted(_normalized_terms(query)),
        "corpus_ids": sorted(str(item.get("incident_id", "")) for item in corpus),
        "weights": {k: _round(v) for k, v in sorted(weights.items())},
        "thresholds": {k: _round(v) for k, v in sorted(thresholds.items())},
        "ranking": [[m["incident_id"], m["score"]] for m in matches],
    }
    digest = hashlib.sha256(_canonical(sealed).encode("utf-8")).hexdigest()
    return {
        "receipt_version": RECEIPT_VERSION,
        "algorithm": "sha256",
        "trace_hash": f"sha256:{digest}",
        "query_id": query.get("query_id"),
        "candidate_count": len(corpus),
        "match_count": len(matches),
    }


def _normalized_terms(query: dict[str, Any]) -> set[str]:
    terms = query.get("terms")
    if not isinstance(terms, list):
        raise ValueError("query.terms must be a list of strings")
    tokens: set[str] = set()
    for term in terms:
        tokens |= normalize_tokens(str(term))
    return tokens


def score_incidents(query: dict[str, Any], corpus: list[dict[str, Any]]) -> dict[str, Any]:
    """Rank ``corpus`` against ``query`` and return the result contract object."""
    if not isinstance(query, dict):
        raise ValueError("query must be an object")
    if not isinstance(corpus, list):
        raise ValueError("corpus must be a list")
    query_id = query.get("query_id")
    if not isinstance(query_id, str) or not query_id:
        raise ValueError("query.query_id is required and must be a non-empty string")

    query_tokens = _normalized_terms(query)
    if not query_tokens:
        raise ValueError("query.terms yielded no usable tokens")

    weights = _resolve_weights(query.get("weights"))
    thresholds = _resolve_thresholds(query.get("thresholds"))
    weight_total = sum(weights.values())
    as_of_epoch = _parse_utc(query.get("as_of_utc"))
    top_k = query.get("top_k")

    scored: list[dict[str, Any]] = []
    for incident in corpus:
        if not isinstance(incident, dict):
            raise ValueError("each corpus entry must be an object")
        incident_id = incident.get("incident_id")
        if not isinstance(incident_id, str) or not incident_id:
            raise ValueError("each corpus entry requires a non-empty incident_id")

        signals = {
            "lexical": _signal_lexical(query_tokens, incident),
            "entity_overlap": _signal_entity(query_tokens, incident),
            "topology": _signal_topology(incident),
            "recency": _signal_recency(incident, as_of_epoch),
        }
        contributions = {
            name: _round(weights[name] * value / weight_total) for name, value in signals.items()
        }
        score = _round(sum(contributions.values()))
        matched_terms = sorted(query_tokens & _incident_text_tokens(incident))

        scored.append(
            {
                "incident_id": incident_id,
                "score": score,
                "signals": {name: _round(value) for name, value in signals.items()},
                "explainability": {
                    "matched_terms": matched_terms,
                    "weighted_contributions": contributions,
                },
                "verdict": project_verdict(score, thresholds),
            }
        )

    # Deterministic ordering: score descending, then incident_id ascending.
    scored.sort(key=lambda m: (-m["score"], m["incident_id"]))

    min_score = thresholds["min_score"]
    matches = [m for m in scored if m["score"] >= min_score]
    if isinstance(top_k, int) and not isinstance(top_k, bool) and top_k >= 0:
        matches = matches[:top_k]
    for rank, match in enumerate(matches):
        match["rank"] = rank

    receipt = build_receipt(query, corpus, weights, thresholds, matches)

    return {
        "schema_version": SCHEMA_VERSION,
        "query_id": query_id,
        "as_of_utc": query.get("as_of_utc"),
        "weights": {k: _round(v) for k, v in weights.items()},
        "thresholds": {k: _round(v) for k, v in thresholds.items()},
        "matches": matches,
        "receipt": receipt,
    }


def _load_json(path: str) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="path to a query JSON document")
    parser.add_argument("--corpus", required=True, help="path to a corpus JSON array")
    parser.add_argument("--out", help="write result JSON here (default: stdout)")
    args = parser.parse_args(argv)

    result = score_incidents(_load_json(args.query), _load_json(args.corpus))
    text = json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            handle.write(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
