#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "github-footprint-itops-expansion.yaml"
SAMPLE = ROOT / "examples" / "github-footprint-itops-sample.yaml"
SMOKE = ROOT / "tests" / "github-footprint-itops-smoke.yaml"
MAPPING = ROOT / "mappings" / "ibm-itops-glo-to-ops-domain.md"
GLO_EXCERPT = ROOT / "third_party" / "ibm-itops" / "GLO_V1-profile-excerpt.ttl"

REQUIRED_FILES = [PROFILE, SAMPLE, SMOKE, MAPPING, GLO_EXCERPT]
REQUIRED_PROFILE_TOKENS = [
    "id: github-footprint-itops-expansion",
    "status: draft",
    "repository_spine:",
    "repo: SocioProphet/sociosphere",
    "semantic_scaffold:",
    "repo: SocioProphet/ontogenesis",
    "website_surface_taxonomy:",
    "site: socioprophet.com",
    "RepositoryArtifact:",
    "RuntimeSystem:",
    "maps_to_glo: [System, TechnicalSystem]",
    "OperationalService:",
    "maps_to_glo: [Service]",
    "WebsiteSurface:",
    "DependencyEdge:",
    "CanonicalSourceNamespace:",
    "EvidenceArtifact:",
    "WorkflowState:",
    "ProviderConnectionState:",
    "CapabilityType:",
    "organizations:",
    "cloud:",
    "live:",
    "digital_trust:",
    "proposed",
    "approved",
    "executing",
    "reviewed",
    "reversed",
    "remediated",
    "connected",
    "limited_capability",
    "failed_test",
    "revoked",
]
REQUIRED_SAMPLE_TOKENS = [
    "id: github-footprint-itops-sample",
    "id: sociosphere",
    "id: ontogenesis",
    "id: global-devsecops-intelligence",
    "id: agentplane",
    "namespace: data/ontogenesis",
    "canonical_repo: ontogenesis",
    "RepositoryArtifact: [Document, WorkProduct]",
    "RuntimeSystem: [System, TechnicalSystem]",
    "OperationalService: [Service]",
    "WorkflowState: [State]",
    "EvidenceArtifact: [Document, WorkProduct, provenance]",
]
REQUIRED_SMOKE_TOKENS = [
    "source-planes-present",
    "repository-spine-points-to-sociosphere",
    "ontogenesis-scaffold-present",
    "website-surface-taxonomy-present",
    "ibm-project-not-canonical-cloud-project",
    "ibm-service-and-system-adopted",
    "Which repository is canonical source for data/ontogenesis?",
    "Which public surfaces normalize to operations and deployment topics?",
]
REQUIRED_MAPPING_TOKENS = [
    "| `Project` | rejected |",
    "| `System` | adopted |",
    "| `TechnicalSystem` | adopted |",
    "| `Service` | adopted |",
    "| `provenance` | adopted |",
]
REQUIRED_GLO_TOKENS = [
    ":Document",
    ":WorkProduct",
    ":Organization",
    ":Company",
    ":Project",
    ":System",
    ":TechnicalSystem",
    ":Service",
    ":Incident",
    ":State",
    ":provenance",
    ":hasPart",
    ":partOf",
]


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def require_tokens(label: str, text: str, tokens: list[str]) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise ValueError(f"{label} missing required tokens: {missing}")


def main() -> int:
    try:
        for path in REQUIRED_FILES:
            if not path.exists():
                raise FileNotFoundError(path)

        require_tokens("profile", PROFILE.read_text(encoding="utf-8"), REQUIRED_PROFILE_TOKENS)
        require_tokens("sample", SAMPLE.read_text(encoding="utf-8"), REQUIRED_SAMPLE_TOKENS)
        require_tokens("smoke", SMOKE.read_text(encoding="utf-8"), REQUIRED_SMOKE_TOKENS)
        require_tokens("mapping ledger", MAPPING.read_text(encoding="utf-8"), REQUIRED_MAPPING_TOKENS)
        require_tokens("GLO profile excerpt", GLO_EXCERPT.read_text(encoding="utf-8"), REQUIRED_GLO_TOKENS)
    except FileNotFoundError as exc:
        return fail(f"missing required file: {exc.args[0]}")
    except Exception as exc:  # noqa: BLE001 - CLI validator should surface direct error text
        return fail(str(exc))

    print("OK: validated GitHub footprint ITOPS profile, sample, smoke checks, mapping ledger, and IBM GLO excerpt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
