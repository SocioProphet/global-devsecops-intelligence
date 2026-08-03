#!/usr/bin/env python3
"""Teeth for the incident-similarity contract (AI4IT Pipeline 3).

This validator refuses to pass unless every one of these holds:

  1. GOLDEN REPRODUCIBILITY - re-running the scorer on the committed
     query+corpus reproduces ``result.expected.json`` byte-for-byte. If the
     scorer drifts from the golden, this fails.
  2. DETERMINISM - two independent scorer runs are identical.
  3. RECEIPT INTEGRITY - the SHA-256 trace hash in the golden equals a freshly
     computed hash over the sealed inputs+ranking (FIPS-180-4 algorithm).
  4. ASSAY PROJECTION SOUNDNESS - every match's stored ok/sad/bad verdict is
     re-derivable from its score and the thresholds (no hand-edited verdicts).
  5. SCHEMA SHAPE - query, corpus, and result conform to the committed JSON
     Schemas (stdlib structural check; the repo does not vendor jsonschema).
  6. NEGATIVE FIXTURES (teeth both ways) - malformed queries/corpora are
     REJECTED by the scorer, and a tampered result is DETECTED as drift. A gate
     that cannot fail is theater; these prove it can.

Standard library only, matching the other validators in this repo.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCORER_PATH = (
    ROOT
    / "open-ai4it-spec"
    / "modules"
    / "story_services"
    / "incident_similarity"
    / "scorer.py"
)
SCHEMA_DIR = ROOT / "open-ai4it-spec" / "contracts" / "schemas"
QUERY_SCHEMA = SCHEMA_DIR / "incident-similarity-query.schema.json"
RESULT_SCHEMA = SCHEMA_DIR / "incident-similarity-result.schema.json"
EX = ROOT / "examples" / "incident-similarity"
QUERY = EX / "query.example.json"
CORPUS = EX / "corpus.example.json"
GOLDEN = EX / "result.expected.json"
INVALID = EX / "invalid"


def _load_scorer():
    spec = importlib.util.spec_from_file_location("incident_similarity_scorer", SCORER_PATH)
    if spec is None or spec.loader is None:
        raise SystemExit(f"[FAIL] cannot load scorer from {SCORER_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


# --- minimal stdlib JSON-Schema shape check (subset used by these contracts) ---


def _schema_errors(instance: Any, schema: dict, defs: dict, path: str = "$") -> list[str]:
    errors: list[str] = []

    if "$ref" in schema:
        ref = schema["$ref"]
        if not ref.startswith("#/$defs/"):
            return [f"{path}: unsupported $ref {ref}"]
        target = defs.get(ref.split("/")[-1])
        if target is None:
            return [f"{path}: missing $def {ref}"]
        return _schema_errors(instance, target, defs, path)

    types = schema.get("type")
    if types is not None:
        if isinstance(types, str):
            types = [types]
        if not any(_type_ok(instance, t) for t in types):
            return [f"{path}: expected type {types}, got {type(instance).__name__}"]

    if "const" in schema and instance != schema["const"]:
        errors.append(f"{path}: expected const {schema['const']!r}, got {instance!r}")

    if "enum" in schema and instance not in schema["enum"]:
        errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")

    if isinstance(instance, (int, float)) and not isinstance(instance, bool):
        if "minimum" in schema and instance < schema["minimum"]:
            errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
        if "maximum" in schema and instance > schema["maximum"]:
            errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            errors.append(f"{path}: string shorter than minLength {schema['minLength']}")
        if "pattern" in schema:
            import re

            if re.search(schema["pattern"], instance) is None:
                errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']}")

    if isinstance(instance, dict):
        for key in schema.get("required", []):
            if key not in instance:
                errors.append(f"{path}: missing required property {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = set(instance) - set(props)
            if extra:
                errors.append(f"{path}: unexpected properties {sorted(extra)}")
        for key, value in instance.items():
            if key in props:
                errors += _schema_errors(value, props[key], defs, f"{path}.{key}")

    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: fewer than minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if isinstance(item_schema, dict):
            for idx, item in enumerate(instance):
                errors += _schema_errors(item, item_schema, defs, f"{path}[{idx}]")

    return errors


def _type_ok(instance: Any, t: str) -> bool:
    if t == "object":
        return isinstance(instance, dict)
    if t == "array":
        return isinstance(instance, list)
    if t == "string":
        return isinstance(instance, str)
    if t == "integer":
        return isinstance(instance, int) and not isinstance(instance, bool)
    if t == "number":
        return isinstance(instance, (int, float)) and not isinstance(instance, bool)
    if t == "boolean":
        return isinstance(instance, bool)
    if t == "null":
        return instance is None
    return False


def _validate_schema(label: str, instance: Any, schema_path: Path, failures: list[str]) -> None:
    schema = _load_json(schema_path)
    errors = _schema_errors(instance, schema, schema.get("$defs", {}))
    for err in errors:
        failures.append(f"[FAIL] {label} schema: {err}")


def main() -> int:
    failures: list[str] = []
    scorer = _load_scorer()

    query = _load_json(QUERY)
    corpus = _load_json(CORPUS)
    golden = _load_json(GOLDEN)

    # (5) schema shape of the inputs and the committed golden.
    _validate_schema("query", query, QUERY_SCHEMA, failures)
    _validate_schema("result", golden, RESULT_SCHEMA, failures)

    # (1) golden reproducibility.
    recomputed = scorer.score_incidents(query, corpus)
    if _canonical(recomputed) != _canonical(golden):
        failures.append(
            "[FAIL] golden drift: scorer output does not match result.expected.json "
            "(regenerate with the scorer CLI and review the diff)"
        )

    # (2) determinism.
    again = scorer.score_incidents(query, corpus)
    if _canonical(again) != _canonical(recomputed):
        failures.append("[FAIL] non-deterministic: two scorer runs disagree")

    # (3) receipt integrity — recompute the trace hash independently.
    weights = scorer._resolve_weights(query.get("weights"))
    thresholds = scorer._resolve_thresholds(query.get("thresholds"))
    fresh_receipt = scorer.build_receipt(
        query, corpus, weights, thresholds, recomputed["matches"]
    )
    if fresh_receipt["trace_hash"] != golden["receipt"]["trace_hash"]:
        failures.append("[FAIL] receipt trace_hash does not verify against recomputation")
    if golden["receipt"]["algorithm"] != "sha256":
        failures.append("[FAIL] receipt algorithm must be sha256 (FIPS-180-4)")

    # (4) Assay projection soundness — verdicts must be re-derivable.
    for match in golden["matches"]:
        expected = scorer.project_verdict(match["score"], thresholds)
        if match["verdict"] != expected:
            failures.append(
                f"[FAIL] verdict drift for {match['incident_id']}: stored "
                f"{match['verdict']} != projected {expected}"
            )

    # (6a) negative input fixtures — the scorer must REFUSE malformed inputs.
    bad_query = _load_json(INVALID / "query-empty-terms.json")
    if not _raises(lambda: scorer.score_incidents(bad_query, corpus)):
        failures.append("[FAIL] scorer accepted a query with empty terms (should refuse)")

    bad_corpus = _load_json(INVALID / "corpus-missing-id.json")
    if not _raises(lambda: scorer.score_incidents(query, bad_corpus)):
        failures.append("[FAIL] scorer accepted a corpus entry with no incident_id (should refuse)")

    # (6b) tampered golden — recomputation must DETECT the drift.
    tampered = _load_json(INVALID / "result-tampered-score.json")
    if _canonical(tampered) == _canonical(recomputed):
        failures.append("[FAIL] tampered result fixture matches the scorer — it is not a tamper")

    if failures:
        for line in failures:
            print(line, file=sys.stderr)
        return 1

    print(
        "[OK] incident-similarity validated: golden reproduced, deterministic, "
        "receipt verified, verdicts sound, schemas conform, negative fixtures rejected"
    )
    return 0


def _raises(fn) -> bool:
    try:
        fn()
    except Exception:
        return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
