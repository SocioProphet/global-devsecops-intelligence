#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "agent-service-desk-metrics.example.json"
REQUIRED_FIELDS = {
    "workstream", "repo", "issueRef", "prRef", "agentKind", "evidenceRefs",
    "timeToFirstActionMs", "timeToFirstPRMs", "timeToMergeMs", "timeToCloseMs",
    "turnsToCompletion", "agentWallClockMs", "ciWallClockMs", "validationWallClockMs",
    "retryCount", "reworkCount", "failureCount", "blockedDurationMs", "handoffCount",
    "evidenceCompletenessScore", "scopeComplianceStatus", "mergeGateStatus",
}
ALLOWED_AGENTS = {"codex", "copilot", "human", "local-cli", "system"}
ALLOWED_STATUS = {"pass", "warn", "fail", "not-evaluated"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if not EXAMPLE.exists():
        return fail(f"missing {EXAMPLE}")
    data = json.loads(EXAMPLE.read_text())
    if data.get("apiVersion") != "devsecops.socioprophet.dev/v1":
        return fail("apiVersion must be devsecops.socioprophet.dev/v1")
    if data.get("kind") != "AgentServiceDeskMetrics":
        return fail("kind must be AgentServiceDeskMetrics")
    records = data.get("spec", {}).get("records", [])
    if not records:
        return fail("spec.records must not be empty")
    for idx, record in enumerate(records):
        prefix = f"records[{idx}]"
        missing = sorted(REQUIRED_FIELDS - set(record))
        if missing:
            return fail(f"{prefix} missing fields: {missing}")
        if record["agentKind"] not in ALLOWED_AGENTS:
            return fail(f"{prefix}.agentKind is invalid")
        if record["scopeComplianceStatus"] not in ALLOWED_STATUS:
            return fail(f"{prefix}.scopeComplianceStatus is invalid")
        if record["mergeGateStatus"] not in ALLOWED_STATUS:
            return fail(f"{prefix}.mergeGateStatus is invalid")
        if not isinstance(record["evidenceRefs"], list) or not record["evidenceRefs"]:
            return fail(f"{prefix}.evidenceRefs must be a non-empty list")
        numeric_fields = [
            "timeToFirstActionMs", "timeToFirstPRMs", "timeToMergeMs", "timeToCloseMs",
            "turnsToCompletion", "agentWallClockMs", "ciWallClockMs", "validationWallClockMs",
            "retryCount", "reworkCount", "failureCount", "blockedDurationMs", "handoffCount",
        ]
        for field in numeric_fields:
            if int(record[field]) < 0:
                return fail(f"{prefix}.{field} must be non-negative")
        score = float(record["evidenceCompletenessScore"])
        if not 0.0 <= score <= 1.0:
            return fail(f"{prefix}.evidenceCompletenessScore must be between 0 and 1")
    print(f"OK: validated {len(records)} service desk metric records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
