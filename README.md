# global-devsecops-intelligence

## Current repository state

- `docs/vision/ai4it-home-rewrite.md`
- `docs/architecture/api-interactions-decision.md`
- `docs/devops/devops-process-open.md`
- `docs/adr/0001-ops-domain-profile-and-external-seed-boundary.md`
- `third_party/ibm-itops/UPSTREAM.md`
- `third_party/ibm-itops/IMPORT-MANIFEST.v2.json`
- `third_party/ibm-itops/LICENSE.Apache-2.0`
- `mappings/ibm-itops-glo-to-ops-domain.md`

## What this is

An operations-domain profile for DevSecOps / AIOps / AI4IT operational intelligence: logs, telemetry, service desk automation, chatops, ticket clustering, reusable evidence artifacts, operational learning loops, and derived operational graph projections.

This repository defines the operations-domain specialization, including:
- AI4IT topic ladder
- ops entity extraction schemas
- mapping DSL
- story grouping
- explainability and feedback loops
- operational measurement plane
- external seed ontology imports relevant to the operations-domain profile
- mappings from external ontologies into the operations-domain profile
- evidence-oriented operational graph projections scoped to this profile

This repository does not own canonical platform storage standards, canonical wire contracts, or the sole canonical platform ontology / broader knowledge semantics.

Ownership boundaries:
- `socioprophet-standards-storage` owns base transport, storage, and interface invariants, including canonical envelope and wire contracts.
- `ontogenesis` and `socioprophet-standards-knowledge` own canonical ontology and broader knowledge semantics.
- `global-devsecops-intelligence` owns the operations-domain profile, external seed ontology imports relevant to that profile, mapping layers, and domain-scoped operational graph projections.

Institutional digital-twin semantics may appear here only insofar as they are needed to support the operations-domain profile. Where a concept has both a platform-wide canonical meaning and an operations-domain specialization, the canonical meaning remains upstream and this repository maintains only the specialization, binding, mapping, or projection.

## Current external seed ontology status

- IBM ITOPS is present here as a metadata-first external seed import under `third_party/ibm-itops/`.
- `GLO_V1.ttl` remains the preferred first payload for semantic alignment.
- Stage payloads (`ITOPS_S1`, `ITOPS_S2`, `ITOPS_S3`) remain deferred until vendoring, validation, and query strategy are approved.

Dependency direction:
`platform standards -> knowledge / ontology standards -> global-devsecops-intelligence operations-domain profile -> runtime implementations`
