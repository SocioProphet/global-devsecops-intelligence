#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "devops" / "client-runtime-dump-exposure.md"
PROFILE = ROOT / "profiles" / "client-runtime-dump-exposure-profile.v0.yaml"
SAMPLE = ROOT / "examples" / "client-runtime-dump-exposure-sample.yaml"
SMOKE = ROOT / "tests" / "client-runtime-dump-exposure-smoke.yaml"

REQUIRED_FILES = [DOC, PROFILE, SAMPLE, SMOKE]

REQUIRED_DOC_TOKENS = [
    "ClientRuntimeDumpExposure",
    "Finding family",
    "Sensitive field classes",
    "Severity guidance",
    "Recommended controls",
    "cookie:",
    "client-auth-info",
    "__reactContainer",
    "ownerDocument",
    "containerInfo",
    "EvidenceArtifact",
    "SecurityControl",
    "ProvenanceRecord",
]

REQUIRED_PROFILE_TOKENS = [
    "id: client-runtime-dump-exposure-profile",
    "finding_family: ClientRuntimeDumpExposure",
    "cookies_or_auth_material_present",
    "identity_or_private_route_or_telemetry_present",
    "redacted_structural_runtime_graph_only",
    "synthetic_fixture_or_documentation_only",
    "sensitive_field_classes:",
    "cookies:",
    "auth_session:",
    "identity:",
    "private_routes:",
    "telemetry:",
    "runtime_graph:",
    "quarantine_raw_dump",
    "redact_before_indexing",
    "reject_public_cookie_material",
    "reject_public_client_auth_info",
    "EvidenceArtifact",
    "WorkflowState",
    "OperationalService",
    "SecurityControl",
    "ProvenanceRecord",
]

REQUIRED_SAMPLE_TOKENS = [
    "id: client-runtime-dump-exposure-sample",
    "unsafe_synthetic:",
    "SYNTHETIC_COOKIE_MATERIAL",
    "SYNTHETIC_CLIENT_AUTH_INFO",
    "expected_severity: high",
    "safe_redacted:",
    "REDACTED_COOKIE_BLOB",
    "REDACTED_PRIVATE_ROUTE",
    "expected_severity: low",
    "bounded_record:",
    "ClientRuntimeDiagnosticRecord",
    "native_object_logged: false",
    "removed_classes:",
]

REQUIRED_SMOKE_TOKENS = [
    "finding-family-present",
    "severity-model-present",
    "sensitive-fields-present",
    "unsafe-synthetic-sample-present",
    "safe-redacted-sample-present",
    "bounded-record-present",
    "ClientRuntimeDumpExposure",
    "cookies_or_auth_material_present",
    "identity_or_private_route_or_telemetry_present",
    "redacted_structural_runtime_graph_only",
    "ClientRuntimeDiagnosticRecord",
]

# Keep the fixture synthetic. Do not allow obvious real account/contact values or
# private app-route copies in the committed example pack.
FORBIDDEN_REGEXES = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}"),
    re.compile(r"https://[^\\s]+/(?:private|conversation|tenant|workspace|account)/[^\\s\\]\)]+"),
]


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def require_tokens(label: str, text: str, tokens: list[str]) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError(f"{label} missing required tokens: {missing}")


def reject_forbidden(label: str, text: str) -> None:
    hits = []
    for regex in FORBIDDEN_REGEXES:
        hits.extend(match.group(0) for match in regex.finditer(text))
    if hits:
        raise ValueError(f"{label} contains forbidden non-synthetic diagnostic tokens: {hits[:3]}")


def main() -> int:
    try:
        for path in REQUIRED_FILES:
            if not path.exists():
                raise FileNotFoundError(path)

        doc_text = DOC.read_text(encoding="utf-8")
        profile_text = PROFILE.read_text(encoding="utf-8")
        sample_text = SAMPLE.read_text(encoding="utf-8")
        smoke_text = SMOKE.read_text(encoding="utf-8")
        combined = "\n".join([doc_text, profile_text, sample_text, smoke_text])

        require_tokens("doc", doc_text, REQUIRED_DOC_TOKENS)
        require_tokens("profile", profile_text, REQUIRED_PROFILE_TOKENS)
        require_tokens("sample", sample_text, REQUIRED_SAMPLE_TOKENS)
        require_tokens("smoke", smoke_text, REQUIRED_SMOKE_TOKENS)
        reject_forbidden("client runtime dump exposure artifacts", combined)
    except FileNotFoundError as exc:
        return fail(f"missing required file: {exc.args[0]}")
    except Exception as exc:  # noqa: BLE001 - CLI validator should surface direct error text
        return fail(str(exc))

    print("OK: validated ClientRuntimeDumpExposure profile, sample, smoke checks, and synthetic-only guard")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
