#!/usr/bin/env python3
"""Validate operational-exhaust fusion mapping artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit("pyyaml is required: install with `python -m pip install pyyaml`") from exc

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "mappings" / "operational-exhaust-to-ops-domain.v0.yaml"
PROFILE = ROOT / "profiles" / "operational-exhaust-fusion-profile.v0.yaml"
EXAMPLE = ROOT / "examples" / "operational-exhaust" / "ops-domain-projection.example.json"

REQUIRED_TOP = {"apiVersion", "kind", "metadata", "spec"}
REQUIRED_SPEC = {
    "source_contracts",
    "target_projection",
    "entity_mappings",
    "trader_agent_mappings",
    "grouping_keys",
    "projection_rules",
}
REQUIRED_ENTITY_KEYS = {
    "event_id",
    "observed_at",
    "source_repo",
    "source_surface",
    "source_runtime",
    "environment_ref",
    "trace_ref",
    "projection_family",
}
REQUIRED_TRADER_KEYS = {
    "strategy_run_ref",
    "model_ref",
    "feature_snapshot_ref",
    "market_window_ref",
    "risk_policy_ref",
    "order_intent_ref",
    "execution_ref",
    "venue_ref",
}
REQUIRED_EXAMPLE_KEYS = {
    "projection_id",
    "source_contracts",
    "projection_family",
    "trace_ref",
    "entities",
    "edges",
    "projection_rules",
}


def load_yaml(path: Path) -> dict:
    try:
        value = yaml.safe_load(path.read_text())
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"failed to parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path} did not parse as a mapping")
    return value


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text())
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"failed to parse {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"{path} did not parse as a mapping")
    return value


def require_keys(value: dict, required: set[str]) -> list[str]:
    return sorted(required - set(value.keys()))


def main() -> int:
    failed = False
    mapping = load_yaml(MAPPING)
    missing = require_keys(mapping, REQUIRED_TOP)
    if missing:
        print(f"[FAIL] mapping top-level missing: {', '.join(missing)}", file=sys.stderr)
        failed = True
    spec = mapping.get("spec", {})
    if not isinstance(spec, dict):
        print("[FAIL] mapping spec is not a mapping", file=sys.stderr)
        return 1
    missing = require_keys(spec, REQUIRED_SPEC)
    if missing:
        print(f"[FAIL] mapping spec missing: {', '.join(missing)}", file=sys.stderr)
        failed = True
    entity_mappings = spec.get("entity_mappings", {})
    trader_mappings = spec.get("trader_agent_mappings", {})
    missing = require_keys(entity_mappings, REQUIRED_ENTITY_KEYS)
    if missing:
        print(f"[FAIL] entity_mappings missing: {', '.join(missing)}", file=sys.stderr)
        failed = True
    missing = require_keys(trader_mappings, REQUIRED_TRADER_KEYS)
    if missing:
        print(f"[FAIL] trader_agent_mappings missing: {', '.join(missing)}", file=sys.stderr)
        failed = True
    if not PROFILE.exists():
        print(f"[FAIL] referenced fusion profile missing: {PROFILE}", file=sys.stderr)
        failed = True
    source_contracts = spec.get("source_contracts", [])
    if len(source_contracts) < 2:
        print("[FAIL] expected at least two source contracts", file=sys.stderr)
        failed = True
    example = load_json(EXAMPLE)
    missing = require_keys(example, REQUIRED_EXAMPLE_KEYS)
    if missing:
        print(f"[FAIL] projection example missing: {', '.join(missing)}", file=sys.stderr)
        failed = True
    if example.get("projection_family") != "trader_agent_execution":
        print("[FAIL] projection example must use trader_agent_execution family", file=sys.stderr)
        failed = True
    if not example.get("entities"):
        print("[FAIL] projection example must include entities", file=sys.stderr)
        failed = True
    if failed:
        return 1
    print("[OK] operational exhaust fusion mapping validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
