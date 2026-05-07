#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOCIOSPHERE = ROOT / "source_inputs" / "sociosphere" / "repository-map.v0.json"
ONTOGENESIS = ROOT / "source_inputs" / "ontogenesis" / "module-map.v0.json"
INTEGRATION_PLANES = ROOT / "source_inputs" / "integration-planes" / "ops-integration-map.v0.json"
ACCOUNT_HIERARCHY = ROOT / "source_inputs" / "institutional-account" / "account-hierarchy.v0.json"
OUTPUT = ROOT / "examples" / "github-footprint-itops-generated.yaml"
SCHEMA_REF = "schemas/github-footprint-itops-generated.schema.json"

SURFACES = [
    ("organizations", "deployment", ["deployment", "institutions", "governance", "trust", "capability"]),
    ("documentation", "docs", ["architecture", "reference", "trust", "platform", "governance"]),
    ("ai", "technical", ["intelligence", "platform", "automation", "builders", "trust"]),
    ("developer", "technical", ["platform", "builders", "integration", "capability", "apis"]),
    ("cloud", "technical", ["platform", "operations", "deployment", "trust", "hosting"]),
    ("live", "technical", ["platform", "operations", "deployment", "signal", "demonstration"]),
    ("digital_trust", "trust", ["trust", "governance", "identity", "platform", "public_positioning"]),
]

REPO_BINDINGS = {
    "sociosphere": ["RepositoryArtifact", "DependencyEdge", "CanonicalSourceNamespace"],
    "ontogenesis": ["EvidenceArtifact"],
    "global-devsecops-intelligence": ["WebsiteSurface", "WorkflowState", "CapabilityType", "ProviderConnectionState", "EvidenceArtifact"],
    "prophet-platform": ["RuntimeSystem", "OperationalService"],
    "agentplane": ["WorkflowState", "EvidenceArtifact", "CapabilityType"],
    "regis-entity-graph": ["CanonicalSourceNamespace", "EvidenceArtifact"],
    "policy-fabric": ["EvidenceArtifact"],
}

IBM_GLO_BINDINGS = {
    "RepositoryArtifact": ["Document", "WorkProduct"],
    "RuntimeSystem": ["System", "TechnicalSystem"],
    "OperationalService": ["Service"],
    "WebsiteSurface": ["Service", "Document"],
    "WorkflowState": ["State"],
    "EvidenceArtifact": ["Document", "WorkProduct", "provenance"],
    "InstitutionalOrganization": ["Organization", "Company"],
    "CloudProject": ["System", "Service"],
    "CloudFolder": ["Organization"],
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text(encoding="utf-8"))


def yaml_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, str):
        if not value:
            return '""'
        if any(ch in value for ch in [":", "#", "[", "]", "{", "}", ","]):
            return json.dumps(value)
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def yaml_list(values: list[str]) -> str:
    return "[" + ", ".join(json.dumps(value) for value in values) + "]"


def render_account_hierarchy(lines: list[str], account_hierarchy: dict[str, Any]) -> None:
    org = account_hierarchy["organization"]
    lines.extend([
        "",
        "institutional_account_hierarchy:",
        "  organization:",
        f"    id: {yaml_scalar(org['id'])}",
        f"    kind: {yaml_scalar(org['kind'])}",
        f"    provider: {yaml_scalar(org['provider'])}",
        f"    display_name: {yaml_scalar(org['display_name'])}",
        f"    canonical_twin_id: {yaml_scalar(org['canonical_twin_id'])}",
        "  folders:",
    ])
    for folder in account_hierarchy["folders"]:
        lines.extend([
            f"    - id: {yaml_scalar(folder['id'])}",
            f"      kind: {yaml_scalar(folder['kind'])}",
            f"      provider: {yaml_scalar(folder['provider'])}",
            f"      display_name: {yaml_scalar(folder['display_name'])}",
            f"      parent: {yaml_scalar(folder['parent'])}",
            f"      canonical_twin_id: {yaml_scalar(folder['canonical_twin_id'])}",
        ])
    lines.append("  projects:")
    for project in account_hierarchy["projects"]:
        lines.extend([
            f"    - id: {yaml_scalar(project['id'])}",
            f"      kind: {yaml_scalar(project['kind'])}",
            f"      provider: {yaml_scalar(project['provider'])}",
            f"      display_name: {yaml_scalar(project['display_name'])}",
            f"      parent: {yaml_scalar(project['parent'])}",
            f"      declared_environment: {yaml_scalar(project['declared_environment'])}",
            f"      structural_environment: {yaml_scalar(project['structural_environment'])}",
            f"      workload_role: {yaml_scalar(project['workload_role'])}",
            f"      canonical_twin_id: {yaml_scalar(project['canonical_twin_id'])}",
            f"      linked_repositories: {yaml_list(project['linked_repositories'])}",
            f"      linked_surfaces: {yaml_list(project['linked_surfaces'])}",
        ])
    lines.append("  findings:")
    for finding in account_hierarchy["findings"]:
        lines.extend([
            f"    - id: {yaml_scalar(finding['id'])}",
            f"      kind: {yaml_scalar(finding['kind'])}",
            f"      severity: {yaml_scalar(finding['severity'])}",
            f"      subject: {yaml_scalar(finding['subject'])}",
        ])
        if "declared_environment" in finding:
            lines.append(f"      declared_environment: {yaml_scalar(finding['declared_environment'])}")
        if "structural_environment" in finding:
            lines.append(f"      structural_environment: {yaml_scalar(finding['structural_environment'])}")
        lines.append(f"      rationale: {json.dumps(finding['rationale'])}")
    lines.append(f"  pending_live_bindings: {yaml_list(account_hierarchy['pending_live_bindings'])}")


def render_projection(
    sociosphere: dict[str, Any],
    ontogenesis: dict[str, Any],
    integration_map: dict[str, Any],
    account_hierarchy: dict[str, Any],
) -> str:
    lines: list[str] = []
    lines.extend([
        "generated_projection:",
        "  id: github-footprint-itops-generated",
        "  version: 0.1.0",
        f"  schema_ref: {SCHEMA_REF}",
        "  generator: tools/generate_github_footprint_itops_projection.py",
        "  sources:",
        f"    sociosphere: {sociosphere['snapshot']['source_repo']}",
        f"    ontogenesis: {ontogenesis['snapshot']['source_repo']}",
        "    integration_planes: source_inputs/integration-planes/ops-integration-map.v0.json",
        "    institutional_account: source_inputs/institutional-account/account-hierarchy.v0.json",
        "",
        "repositories:",
    ])

    for repo in sociosphere["repositories"]:
        repo_id = repo["id"]
        bindings = REPO_BINDINGS.get(repo_id, ["RepositoryArtifact"])
        lines.extend([
            f"  - id: {repo_id}",
            f"    layer: {repo['layer']}",
            f"    role: {repo['role']}",
            f"    description: {json.dumps(repo['description'])}",
            f"    topics: {yaml_list(repo['topics'])}",
            f"    binds: {yaml_list(bindings)}",
        ])

    lines.extend(["", "namespace_bindings:"])
    for binding in sociosphere["namespace_bindings"]:
        lines.extend([
            f"  - namespace: {binding['namespace']}",
            f"    canonical_repo: {binding['canonical_repo']}",
        ])

    lines.extend(["", "dependencies:"])
    for edge in sociosphere["dependencies"]:
        lines.extend([
            f"  - from: {edge['from']}",
            f"    to: {edge['to']}",
            f"    type: {edge['type']}",
        ])

    lines.extend(["", "surfaces:"])
    for surface_id, category, topics in SURFACES:
        lines.extend([
            f"  - id: {surface_id}",
            f"    category: {category}",
            f"    normalized_topics: {yaml_list(topics)}",
        ])

    lines.extend(["", "integration_planes:"])
    for plane in integration_map["integration_planes"]:
        lines.extend([
            f"  - id: {plane['id']}",
            f"    kind: {plane['kind']}",
            f"    status: {plane['status']}",
            f"    repo: {yaml_scalar(plane['repo'])}",
            f"    operations_role: {json.dumps(plane['operations_role'])}",
            f"    binds: {yaml_list(plane['binds'])}",
            f"    source_evidence: {yaml_list(plane['source_evidence'])}",
        ])

    render_account_hierarchy(lines, account_hierarchy)

    lines.extend(["", "ontogenesis_scaffold:"])
    lines.extend([f"  capabilities: {yaml_list(ontogenesis['capabilities'])}"])
    lines.append("  modules:")
    for module in ontogenesis["modules"]:
        lines.extend([
            f"    - id: {module['id']}",
            f"      kind: {module['kind']}",
            f"      description: {json.dumps(module['description'])}",
        ])
    lines.extend([
        f"  useful_classes: {yaml_list(ontogenesis['useful_classes'])}",
        f"  lifecycle_states: {yaml_list(ontogenesis['lifecycle_states'])}",
        "",
        "ibm_glo_bindings:",
    ])
    for local_class, glo_terms in IBM_GLO_BINDINGS.items():
        lines.append(f"  {local_class}: {yaml_list(glo_terms)}")

    lines.extend([
        "",
        "queries:",
        "  - id: canonical-source-for-ontogenesis",
        "    answer: ontogenesis",
        "  - id: operation-surfaces",
        "    answer: [\"cloud\", \"live\"]",
        "  - id: workflow-state-repositories",
        "    answer: [\"global-devsecops-intelligence\", \"agentplane\"]",
        "  - id: security-integration-planes",
        "    answer: [\"sherlock\", \"scoped-redteaming\"]",
        "  - id: world-model-and-graph-runtime-planes",
        "    answer: [\"gaia-world-model\", \"meshrush\"]",
        "  - id: institutional-account-environment-conflicts",
        "    answer: [\"finding-env-conflict-socioprophet-web\"]",
        "  - id: institutional-account-cloud-surface-projects",
        "    answer: [\"socioprophet-web\", \"prophet-platform\"]",
    ])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write generated projection")
    args = parser.parse_args()

    try:
        sociosphere = load_json(SOCIOSPHERE)
        ontogenesis = load_json(ONTOGENESIS)
        integration_map = load_json(INTEGRATION_PLANES)
        account_hierarchy = load_json(ACCOUNT_HIERARCHY)
        rendered = render_projection(sociosphere, ontogenesis, integration_map, account_hierarchy)
    except Exception as exc:  # noqa: BLE001 - CLI utility should surface direct error text
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.write:
        OUTPUT.write_text(rendered, encoding="utf-8")
        print(f"OK: wrote {OUTPUT}")
        return 0

    if not OUTPUT.exists():
        print(f"ERROR: missing generated projection {OUTPUT}; run with --write", file=sys.stderr)
        return 1
    current = OUTPUT.read_text(encoding="utf-8")
    if current != rendered:
        diff = difflib.unified_diff(
            current.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile=str(OUTPUT),
            tofile="generated",
        )
        print(f"ERROR: generated projection is stale: {OUTPUT}; run with --write", file=sys.stderr)
        print("".join(diff), file=sys.stderr)
        return 1
    print("OK: generated GitHub footprint ITOPS projection is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
