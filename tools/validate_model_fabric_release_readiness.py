#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "model-fabric-release-readiness.example.json"
REQUIRED_TOOLS = {
    "model-router",
    "guardrail-fabric",
    "model-governance-ledger",
    "agent-registry",
    "prophet-cli",
    "homebrew-prophet",
}
REQUIRED_BOOL_FIELDS = {
    "releaseDryRunPresent",
    "releaseDryRunWorkflowPresent",
    "homebrewDevFormulaPresent",
    "stableReleaseArtifactPresent",
    "sha256Present",
    "sbomPresent",
    "provenancePresent",
    "formulaTestPresent",
}
ALLOWED_STATUSES = {"blocked", "partial", "ready", "complete"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def expected_score(record: dict) -> float:
    return sum(0.125 for field in REQUIRED_BOOL_FIELDS if record[field])


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    data = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    if data.get("apiVersion") != "devsecops.socioprophet.dev/v1":
        return fail("apiVersion must be devsecops.socioprophet.dev/v1")
    if data.get("kind") != "ModelFabricReleaseReadinessScorecard":
        return fail("kind must be ModelFabricReleaseReadinessScorecard")

    metadata = data.get("metadata", {})
    if metadata.get("readinessIsCertification") is not False:
        return fail("metadata.readinessIsCertification must be false")
    if metadata.get("certificationStatus") != "not-certified":
        return fail("metadata.certificationStatus must be not-certified")

    spec = data.get("spec", {})
    tools = spec.get("tools", [])
    if not tools:
        return fail("spec.tools must not be empty")
    seen = {tool.get("toolId") for tool in tools}
    missing_tools = sorted(REQUIRED_TOOLS - seen)
    if missing_tools:
        return fail(f"missing tool scorecards: {missing_tools}")

    semantics = spec.get("scoreSemantics", {})
    for field in REQUIRED_BOOL_FIELDS:
        if semantics.get(field) != 0.125:
            return fail(f"scoreSemantics.{field} must be 0.125")

    for idx, record in enumerate(tools):
        prefix = f"tools[{idx}]"
        for field in ["toolId", "repo", "openIssueRefs", "openPRRefs", "readinessScore", "readinessStatus", "notes"]:
            if field not in record:
                return fail(f"{prefix} missing field {field}")
        for field in REQUIRED_BOOL_FIELDS:
            if not isinstance(record.get(field), bool):
                return fail(f"{prefix}.{field} must be boolean")
        if not str(record["repo"]).startswith("SocioProphet/"):
            return fail(f"{prefix}.repo must use a SocioProphet repo ref")
        if not isinstance(record["openIssueRefs"], list) or not isinstance(record["openPRRefs"], list):
            return fail(f"{prefix}.openIssueRefs and openPRRefs must be lists")
        if record["readinessStatus"] not in ALLOWED_STATUSES:
            return fail(f"{prefix}.readinessStatus is invalid")
        score = float(record["readinessScore"])
        if not 0.0 <= score <= 1.0:
            return fail(f"{prefix}.readinessScore must be between 0 and 1")
        expected = expected_score(record)
        if abs(score - expected) > 0.0001:
            return fail(f"{prefix}.readinessScore expected {expected}, got {score}")
        if record["stableReleaseArtifactPresent"] is False and record["readinessStatus"] == "complete":
            return fail(f"{prefix}.readinessStatus cannot be complete without stable release artifact evidence")

    known_gaps = spec.get("knownGaps", [])
    if "readiness score is not production certification" not in known_gaps:
        return fail("knownGaps must include readiness-score boundary")

    print(f"OK: validated {len(tools)} model-fabric release readiness scorecards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
