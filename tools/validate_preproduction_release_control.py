#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "devops" / "preproduction-release-doctrine.md"
MATRIX = ROOT / "docs" / "devops" / "preproduction-release-traceability-matrix.md"
ADR = ROOT / "docs" / "adr" / "0003-preproduction-release-doctrine-boundary.md"
PROFILE = ROOT / "profiles" / "preproduction-release-control-profile.v0.yaml"
SAMPLE = ROOT / "examples" / "preproduction-release-control-sample.yaml"
SMOKE = ROOT / "tests" / "preproduction-release-control-smoke.yaml"

REQUIRED_FILES = [DOC, MATRIX, ADR, PROFILE, SAMPLE, SMOKE]

CONTROL_IDS = [f"PRC-{idx:03d}" for idx in range(1, 12)]

REQUIRED_DOC_TOKENS = [
    "Preproduction Release Doctrine",
    "ChangeRecord",
    "DeploymentBOM",
    "EvidenceBundle",
    "BaselineManifest",
    "ReleaseException",
    "PromotionEvent",
    "RollbackEvent",
    "EmergencyReconciliation",
    "readiness from certification",
    "change.record.created",
    "evidence.bundle.attached",
    "deployment.signature.failed",
    "baseline.updated",
    "breakglass.reconciled",
]

REQUIRED_MATRIX_TOKENS = [
    "Preproduction Release Traceability Matrix",
    "Control objective",
    "Required evidence",
    "Enforcement primitive",
    "Graph query target",
    "ChangeRecord",
    "DeploymentBOM",
    "EvidenceBundle",
    "BaselineManifest",
]

REQUIRED_ADR_TOKENS = [
    "ADR 0003",
    "Preproduction Release Doctrine Boundary",
    "SHALL own the ops-domain projection",
    "SHALL NOT become the canonical implementation home",
    "Sociosphere owns repository inventory",
    "Readiness remains a signal",
]

REQUIRED_PROFILE_TOKENS = [
    "id: preproduction-release-control",
    "readiness_is_certification: false",
    "blocked",
    "partial",
    "ready_for_review",
    "ready_for_promotion",
    "emergency_reconcile",
    "complete",
    "raw_sensitive_payloads: reference_only",
    "evidence_requires_immutable_refs: true",
]

REQUIRED_SAMPLE_TOKENS = [
    "id: preproduction-release-control-sample",
    "kind: PreproductionReleaseControlSample",
    "CHG-SYNTH-0001",
    "evb-synthetic-0001",
    "base-synthetic-0001",
    "EXC-SYNTH-0001",
    "synthetic medium finding accepted for preproduction validation only",
]

REQUIRED_SMOKE_TOKENS = [
    "doctrine-primitives-present",
    "control-families-present",
    "boundary-present",
    "readiness-boundary-present",
    "emergency-reconciliation-present",
    "release-topics-present",
]


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require_tokens(label: str, text: str, tokens: list[str]) -> str | None:
    missing = [token for token in tokens if token not in text]
    if missing:
        return f"{label} missing tokens: {missing}"
    return None


def main() -> int:
    missing_files = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing_files:
        return fail(f"missing required files: {missing_files}")

    doc = read(DOC)
    matrix = read(MATRIX)
    adr = read(ADR)
    profile = read(PROFILE)
    sample = read(SAMPLE)
    smoke = read(SMOKE)

    checks = [
        ("doctrine", doc, REQUIRED_DOC_TOKENS),
        ("matrix", matrix, REQUIRED_MATRIX_TOKENS),
        ("adr", adr, REQUIRED_ADR_TOKENS),
        ("profile", profile, REQUIRED_PROFILE_TOKENS),
        ("sample", sample, REQUIRED_SAMPLE_TOKENS),
        ("smoke", smoke, REQUIRED_SMOKE_TOKENS),
    ]
    for label, text, tokens in checks:
        error = require_tokens(label, text, tokens)
        if error:
            return fail(error)

    for control_id in CONTROL_IDS:
        for label, text in [("doctrine", doc), ("matrix", matrix), ("profile", profile)]:
            if control_id not in text:
                return fail(f"{label} missing {control_id}")

    if "readiness_score_is_certification: false" not in profile:
        return fail("profile must reject readiness-score certification equivalence")
    if "emergency_flow_deletes_evidence_requirement: false" not in profile:
        return fail("profile must preserve evidence requirements for emergency flow")
    if "Raw sensitive payloads should stay in canonical stores" not in doc:
        return fail("doctrine must keep raw sensitive payloads out of ops-domain projections")

    print("OK: validated preproduction release control doctrine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
