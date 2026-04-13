# ADR 0001: Operations-Domain Profile and External Seed Ontology Boundary

## Status
Accepted

## Context
`global-devsecops-intelligence` is the operations-domain specialization for DevSecOps / AIOps-style operational intelligence. The repository already declares that ontology and knowledge semantics are owned upstream by `ontogenesis` and `socioprophet-standards-knowledge`, while this repository owns the operations-domain profile built on those upstream standards.

We also want to incorporate public ontologies such as IBM ITOPS as seed material. Without an explicit boundary, this repository could drift into becoming an ungoverned canonical ontology store, which would conflict with the declared ownership model.

## Decision
This repository SHALL own:
- the operations-domain profile for DevSecOps / AIOps / IT operations intelligence,
- external seed ontology imports relevant to that profile,
- mapping layers from external ontologies into the operations-domain profile,
- operational query patterns, extraction schemas, taxonomy profiles, and evidence-oriented constraints,
- derived operational graph projections that are scoped to the operations-domain profile.

This repository SHALL NOT be treated as the sole canonical home of platform-wide ontology semantics.
Canonical ontology and broader knowledge semantics remain upstream in the designated ontology / knowledge repositories.

Institutional digital-twin semantics may be projected here only insofar as they are needed to support the operations-domain profile. Where a concept has both a platform-wide canonical meaning and an operations-domain specialization, the canonical meaning remains upstream and this repository maintains only the specialization, binding, mapping, or projection.

## External seed ontology policy
External ontologies imported here MUST:
- preserve upstream provenance,
- preserve upstream licensing,
- record upstream file digests and retrieval metadata,
- declare a mapping status for classes and properties (`adopted`, `mapped`, `rejected`, `deferred`),
- avoid silently overwriting canonical platform semantics.

The first IBM ITOPS import in this repository is metadata-first. `GLO_V1.ttl` is the preferred first payload for semantic alignment. Stage payloads (`ITOPS_S1`, `ITOPS_S2`, `ITOPS_S3`) are deferred until mapping scope, binary artifact policy, and validation strategy are approved.

## Consequences
- This repository remains aligned with its declared role as an operations-domain profile.
- External ontology imports become reviewable and reproducible.
- Canonical institutional digital-twin semantics must still be governed upstream.
- The repository needs follow-on documentation updates in `README.md` and `MANIFEST.txt` to reflect this ADR.
