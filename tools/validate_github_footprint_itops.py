#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised in real environment only
    raise SystemExit("ERROR: PyYAML is required for GitHub footprint ITOPS validation") from exc

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "github-footprint-itops-expansion.yaml"
SAMPLE = ROOT / "examples" / "github-footprint-itops-sample.yaml"
SMOKE = ROOT / "tests" / "github-footprint-itops-smoke.yaml"
MAPPING = ROOT / "mappings" / "ibm-itops-glo-to-ops-domain.md"
GLO_EXCERPT = ROOT / "third_party" / "ibm-itops" / "GLO_V1-profile-excerpt.ttl"

REQUIRED_SOURCE_PLANES = {"repository_spine", "semantic_scaffold", "website_surface_taxonomy"}
REQUIRED_LOCAL_CLASSES = {
    "RepositoryArtifact",
    "RuntimeSystem",
    "OperationalService",
    "WebsiteSurface",
    "DependencyEdge",
    "CanonicalSourceNamespace",
    "EvidenceArtifact",
    "WorkflowState",
    "ProviderConnectionState",
    "CapabilityType",
}
REQUIRED_SURFACES = {"organizations", "documentation", "ai", "developer", "cloud", "live", "digital_trust"}
REQUIRED_GLO_TERMS = {
    "Document",
    "WorkProduct",
    "Organization",
    "Company",
    "Project",
    "System",
    "TechnicalSystem",
    "Service",
    "Incident",
    "State",
    "provenance",
    "hasPart",
    "partOf",
}
REQUIRED_WORKFLOW_STATES = {"proposed", "approved", "executing", "reviewed", "reversed", "remediated"}
REQUIRED_PROVIDER_STATES = {"connected", "limited_capability", "failed_test", "revoked"}


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def load_yaml(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(path)
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def require_subset(name: str, required: set[str], observed: set[str]) -> None:
    missing = sorted(required - observed)
    if missing:
        raise ValueError(f"{name} missing required values: {missing}")


def validate_profile(profile_doc: dict[str, Any]) -> None:
    profile = profile_doc.get("profile", {})
    if profile.get("id") != "github-footprint-itops-expansion":
        raise ValueError("profile.id must be github-footprint-itops-expansion")
    if profile.get("status") != "draft":
        raise ValueError("profile.status must be draft")

    source_planes = profile_doc.get("source_planes", {})
    require_subset("source_planes", REQUIRED_SOURCE_PLANES, set(source_planes))
    if source_planes["repository_spine"].get("repo") != "SocioProphet/sociosphere":
        raise ValueError("repository_spine.repo must be SocioProphet/sociosphere")
    if source_planes["semantic_scaffold"].get("repo") != "SocioProphet/ontogenesis":
        raise ValueError("semantic_scaffold.repo must be SocioProphet/ontogenesis")
    if source_planes["website_surface_taxonomy"].get("site") != "socioprophet.com":
        raise ValueError("website_surface_taxonomy.site must be socioprophet.com")

    local_classes = profile_doc.get("local_classes", {})
    require_subset("local_classes", REQUIRED_LOCAL_CLASSES, set(local_classes))
    runtime_maps = set(local_classes["RuntimeSystem"].get("maps_to_glo", []))
    require_subset("RuntimeSystem.maps_to_glo", {"System", "TechnicalSystem"}, runtime_maps)
    service_maps = set(local_classes["OperationalService"].get("maps_to_glo", []))
    require_subset("OperationalService.maps_to_glo", {"Service"}, service_maps)

    vocab = profile_doc.get("controlled_vocabularies", {})
    require_subset("workflow_states", REQUIRED_WORKFLOW_STATES, set(vocab.get("workflow_states", [])))
    require_subset("provider_connection_states", REQUIRED_PROVIDER_STATES, set(vocab.get("provider_connection_states", [])))

    surfaces = profile_doc.get("surface_taxonomy", {})
    require_subset("surface_taxonomy", REQUIRED_SURFACES, set(surfaces))
    require_subset("surface_taxonomy.cloud.normalized_topics", {"operations", "deployment", "trust"}, set(surfaces["cloud"].get("normalized_topics", [])))
    require_subset("surface_taxonomy.organizations.normalized_topics", {"deployment", "governance", "trust", "capability"}, set(surfaces["organizations"].get("normalized_topics", [])))


def validate_sample(sample_doc: dict[str, Any]) -> None:
    sample = sample_doc.get("sample", {})
    if sample.get("id") != "github-footprint-itops-sample":
        raise ValueError("sample.id must be github-footprint-itops-sample")
    repos = {repo.get("id") for repo in sample_doc.get("repositories", [])}
    require_subset("sample.repositories", {"sociosphere", "ontogenesis", "global-devsecops-intelligence", "agentplane"}, repos)
    surfaces = {surface.get("id") for surface in sample_doc.get("surfaces", [])}
    require_subset("sample.surfaces", {"organizations", "documentation", "cloud", "live"}, surfaces)
    namespace_bindings = {binding.get("namespace"): binding.get("canonical_repo") for binding in sample_doc.get("namespace_bindings", [])}
    if namespace_bindings.get("data/ontogenesis") != "ontogenesis":
        raise ValueError("sample namespace data/ontogenesis must bind to ontogenesis")
    glo_bindings = sample_doc.get("ibm_glo_bindings", {})
    if set(glo_bindings.get("RuntimeSystem", [])) != {"System", "TechnicalSystem"}:
        raise ValueError("sample RuntimeSystem IBM GLO binding must be System + TechnicalSystem")


def validate_mapping_ledger(text: str) -> None:
    required_lines = [
        "| `Project` | rejected |",
        "| `System` | adopted |",
        "| `TechnicalSystem` | adopted |",
        "| `Service` | adopted |",
        "| `provenance` | adopted |",
    ]
    for line in required_lines:
        if line not in text:
            raise ValueError(f"mapping ledger missing required decision line containing: {line}")


def validate_glo_excerpt(text: str) -> None:
    for term in REQUIRED_GLO_TERMS:
        needle = f":{term}" if term[0].isupper() else f":{term}"
        if needle not in text:
            raise ValueError(f"GLO profile excerpt missing {needle}")


def validate_smoke(smoke_doc: dict[str, Any]) -> None:
    tests = smoke_doc.get("smoke_tests", [])
    queries = smoke_doc.get("queries", [])
    if len(tests) < 8:
        raise ValueError("smoke_tests must include at least 8 checks")
    if len(queries) < 4:
        raise ValueError("queries must include at least 4 query examples")


def main() -> int:
    try:
        validate_profile(load_yaml(PROFILE))
        validate_sample(load_yaml(SAMPLE))
        validate_smoke(load_yaml(SMOKE))
        validate_mapping_ledger(MAPPING.read_text(encoding="utf-8"))
        validate_glo_excerpt(GLO_EXCERPT.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        return fail(f"missing required file: {exc.args[0]}")
    except Exception as exc:  # noqa: BLE001 - CLI validator should surface direct error text
        return fail(str(exc))

    print("OK: validated GitHub footprint ITOPS profile, sample, mapping ledger, and IBM GLO excerpt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
