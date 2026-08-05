#!/usr/bin/env python3
"""Validate the competitive-landscape source input against its schema and invariants."""
from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except Exception as exc:  # pragma: no cover
    raise SystemExit("pyyaml is required: `python -m pip install pyyaml`") from exc

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "source_inputs" / "competitive-intel" / "landscape.v0.yaml"
SCHEMA = ROOT / "schemas" / "competitive-landscape.schema.json"
SEVERITIES = {"critical", "high", "medium", "low"}
STAGES = {"experimental", "beta", "ga", "scaled"}

errors: list[str] = []
doc = yaml.safe_load(DATA.read_text())

if doc.get("apiVersion") != "gdsi.socioprophet.org/v0":
    errors.append("apiVersion must be gdsi.socioprophet.org/v0")
if doc.get("kind") != "CompetitiveLandscape":
    errors.append("kind must be CompetitiveLandscape")

competitors = (doc.get("spec") or {}).get("competitors") or []
if not competitors:
    errors.append("spec.competitors is empty")

seen: set = set()
for c in competitors:
    key = f"{c.get('vendor')}/{c.get('product')}"
    if key in seen:
        errors.append(f"duplicate competitor: {key}")
    seen.add(key)
    for field in ("vendor", "product", "cluster", "maturity", "beats_us_on"):
        if field not in c:
            errors.append(f"{key}: missing {field}")
    if (c.get("maturity") or {}).get("stage") not in STAGES:
        errors.append(f"{key}: maturity.stage not in {sorted(STAGES)}")
    if not c.get("beats_us_on"):
        errors.append(f"{key}: beats_us_on is empty (an entry with no gap should be dropped)")
    for g in c.get("beats_us_on", []):
        for field in ("capability", "severity", "evidence"):
            if field not in g:
                errors.append(f"{key}: gap missing {field}")
        if g.get("severity") not in SEVERITIES:
            errors.append(f"{key}: gap severity {g.get('severity')!r} not in {sorted(SEVERITIES)}")

# Optional strict schema validation when jsonschema is installed.
try:
    import jsonschema  # type: ignore
    try:
        jsonschema.validate(doc, json.loads(SCHEMA.read_text()))
    except jsonschema.ValidationError as exc:  # pragma: no cover
        errors.append(f"schema: {exc.message}")
except ImportError:
    pass

if errors:
    print("VALIDATION FAILED:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

gaps = sum(len(c.get("beats_us_on", [])) for c in competitors)
print(f"ok: competitive-landscape valid — {len(competitors)} competitors, {gaps} gap findings")
