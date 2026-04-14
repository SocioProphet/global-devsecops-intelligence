# GitHub footprint and website-surface alignment for the IT operations profile

## Purpose

This document expands the IBM ITOPS seed import by binding it to three live SocioProphet evidence planes:

1. `sociosphere` as the repository / role / dependency / canonical-source spine for the GitHub footprint,
2. `ontogenesis` as the ontology-generation, provenance, policy, and alignment scaffold,
3. the live website and documentation surfaces as the public-safe operational taxonomy for surfaces, workflows, routing, and state.

The result is not a generic IT operations ontology. It is a SocioProphet-shaped operations-domain profile that can describe repository topology, runtime systems, public-facing surfaces, capability routing, and evidence-bearing operational workflows together.

## Evidence planes

### 1. Sociosphere repository intelligence plane

`sociosphere` already exposes the GitHub footprint as governed data:

- canonical repo inventory in `registry/canonical-repos.yaml`
- role and semantic bindings in `registry/repository-ontology.yaml`
- dependency edges in `registry/dependency-graph.yaml`
- canonical namespace ownership in `governance/CANONICAL_SOURCES.yaml`

This means our IT operations profile should treat repository metadata, role assignment, dependency direction, and canonical source ownership as first-class operational graph inputs, not as side notes.

### 2. Ontogenesis semantic and lifecycle plane

`ontogenesis` provides the framework for:

- seed ontology creation and refinement under uncertainty
- ontology linking and boundary mappings
- provenance capture and policy-aware validation
- SHACL / JSON-LD / mapping / example / test surfaces

Within the current `ontogenesis.ttl`, the most immediately useful classes for this repository are `Provenance`, `EvaluationEvent`, `PolicyDecision`, and `Receipt`, because they let us model evidence-bearing workflow transitions and promotion / reversal logic over repository and surface changes.

### 3. Website surface and operational-taxonomy plane

The public website and docs provide a normalized surface taxonomy we can use safely in the open layer:

- documentation is the deeper system-detail surface
- organizations is the deployment / institutional adoption surface
- AI, Developer, Cloud, and Live are technical surfaces with operations-facing topic sets
- digital trust links identity, connected capability, recovery, and failure handling
- governed AI and the Agent Plane define bounded execution, role separation, workflow states, evidence emission, review, promotion, and reversal
- provider capability routing defines capability types and visible provider connection states

This public taxonomy is valuable because it already expresses the outward operational footprint in language that is aligned to the product surface and safe to publish.

## What the IBM ITOPS seed should be expanded with locally

IBM GLO remains useful as a bridge ontology for `System`, `TechnicalSystem`, `Service`, `Document`, `WorkProduct`, `Incident`, `State`, `partOf`, and `provenance`.

However, the SocioProphet footprint requires local operations-domain classes that IBM GLO does not provide directly.

### Required local classes

- `RepositoryArtifact`
- `RepositoryRole`
- `RepositoryLayer`
- `CanonicalSourceNamespace`
- `DependencyEdge`
- `WebsiteSurface`
- `SurfaceCategory`
- `SurfaceStatus`
- `CapabilityType`
- `ProviderConnectionState`
- `WorkflowRole`
- `WorkflowState`
- `EvidenceArtifact`
- `PromotionGate`
- `ReversalPath`

### Why these classes are needed

A GitHub repository is not identical to a runtime system. A repository is a governed source artifact boundary that may define, test, document, or deploy one or more systems or services.

A public-facing website surface is not identical to a repository either. A surface is a trust and audience boundary with its own normalized topics, docs paths, and deployment posture.

The operations profile therefore needs both artifact-level and runtime-level modeling, with explicit joins between them.

## First-pass mappings

### Repository and runtime mapping

- `RepositoryArtifact` maps primarily to IBM GLO `Document` + `WorkProduct`
- `RuntimeSystem` maps primarily to IBM GLO `System` / `TechnicalSystem`
- `OperationalService` maps primarily to IBM GLO `Service`
- `EvidenceArtifact` maps to IBM GLO `Document` + `WorkProduct`, and to `ontogenesis` `Receipt` / `Provenance`

### Workflow and governance mapping

- workflow transitions should emit `EvaluationEvent`
- review / gate decisions should bind to `PolicyDecision`
- promotion / reversibility evidence should bind to `Receipt` and `Provenance`

### Surface taxonomy mapping

Website surfaces should be modeled as governed public-facing operational surfaces with:

- category
- status
- normalized topics
- related surfaces
- docs path / landing path
- trust boundary notes

## GitHub footprint interpretation for this repository

The current footprint should be interpreted through at least these anchors:

- `sociosphere`: workspace controller, orchestrator, canonical source registry, dependency-policy spine
- `ontogenesis`: ontology generation and alignment substrate
- `global-devsecops-intelligence`: intelligence / security / governance-facing operations-domain profile
- `prophet-platform`: platform and service interface surface
- `agentplane`: operator workflow and bounded execution surface
- `regis-entity-graph`: governed actor / relationship graph surface
- `policy-fabric`: policy and validation surface

## Website surfaces that should influence the operations profile now

The immediate website-derived expansions that matter for the IT operations profile are:

- `organizations` → deployment, institutions, governance, trust, capability
- `documentation` → architecture, reference, trust, platform, governance
- `ai` → intelligence, platform, automation, builders, trust
- `developer` → platform, builders, integration, capability, APIs
- `cloud` → platform, operations, deployment, trust, hosting
- `live` → platform, operations, deployment, signal, demonstration
- `digital-trust` → trust, governance, identity, platform, public-positioning
- `entity-analytics` → trust, platform, governance, identity, proof artifacts

## Operational vocabulary imported from the website docs

### Workflow roles

- requester
- reviewer
- executor
- auditor
- safeguarding / governance authority

### Workflow states

- proposed
- approved
- executing
- degraded
- paused
- completed
- reviewed
- reversed
- remediated

### Capability types

- coding
- research
- browsing
- local execution
- recovery / fallback

### Provider connection states

- not connected
- connecting
- connected
- needs re-auth
- limited capability
- failed test
- revoked

These should become local controlled vocabularies in the operations-domain profile.

## Immediate design implications

1. The IT operations footprint must include repository governance, not just runtime incidents.
2. Capability routing, provider health, workflow state, and evidence emission are public operational semantics already present on the website and should be reflected in the ontology expansion.
3. `ontogenesis` should remain the place where broader ontology and validation mechanics live; this repository should specialize them into an operations-domain profile.
4. IBM GLO should remain a bridge ontology, not the sole canonical meaning for repository or surface identity.
5. `global-devsecops-intelligence` should eventually add a machine-readable GitHub-footprint profile that binds repositories, surfaces, and workflow/capability vocabularies into one operational graph.
