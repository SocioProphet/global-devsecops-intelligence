#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOCIOSPHERE = ROOT / "source_inputs" / "sociosphere" / "repository-map.v0.json"
ONTOGENESIS = ROOT / "source_inputs" / "ontogenesis" / "module-map.v0.json"
INTEGRATION_PLANES = ROOT / "source_inputs" / "integration-planes" / "ops-integration-map.v0.json"
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
    return "[" + ", ".join(values) + "]"


def append_mapping(lines: list[str], mapping: dict[str, Any], indent: str) -> None:
    for key, value in mapping.items():
        if isinstance(value, list):
            if all(isinstance(item, str) for item in value):
                lines.append(f"{indent}{key}: {yaml_list(value)}")
            else:
                lines.append(f"{indent}{key}:")
                for item in value:
                    if isinstance(item, dict):
                        first = True
                        for item_key, item_value in item.items():
                            prefix = "- " if first else "  "
                            lines.append(f"{indent}  {prefix}{item_key}: {yaml_scalar(item_value)}")
                            first = False
                    else:
                        lines.append(f"{indent}  - {yaml_scalar(item)}")
        else:
            lines.append(f"{indent}{key}: {yaml_scalar(value)}")


def render_projection(sociosphere: dict[str, Any], ontogenesis: dict[str, Any], integration_map: dict[str, Any]) -> str:
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
        "    answer: [cloud, live]",
        "  - id: workflow-state-repositories",
        "    answer: [global-devsecops-intelligence, agentplane]",
        "  - id: security-integration-planes",
        "    answer: [sherlock, scoped-redteaming]",
        "  - id: world-model-and-graph-runtime-planes",
        "    answer: [gaia-world-model, meshrush]",
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
        rendered = render_projection(sociosphere, ontogenesis, integration_map)
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
        print(f"ERROR: generated projection is stale: {OUTPUT}; run with --write", file=sys.stderr)
        return 1
    print("OK: generated GitHub footprint ITOPS projection is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
