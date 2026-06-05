# ADR 0003: Preproduction Release Doctrine Boundary

## Status

Proposed

## Context

`global-devsecops-intelligence` owns the operations-domain profile for DevSecOps / AIOps / AI4IT operational intelligence. Existing boundary ADRs already keep canonical storage, wire, and ontology semantics upstream while allowing this repository to own operational projections, mappings, evidence-oriented constraints, story grouping, measurement, and feedback loops.

The preproduction release doctrine adds a second pressure point: release governance is both an operational-intelligence concern and a platform-enforcement concern. If the doctrine is stored only as prose, it cannot drive graph queries, evidence completeness checks, release-readiness scoring, or operational learning. If it is stored only as platform code, it loses the audit and explanatory semantics required by DevSecOps intelligence.

## Decision

This repository SHALL own the ops-domain projection of preproduction release governance, including:

- release-control doctrine and control objectives;
- traceability from source clauses to evidence artifacts and enforcement points;
- operational topics and entity mappings for change records, evidence bundles, deployment BOMs, baseline manifests, findings, exceptions, approvals, and promotion events;
- release-readiness scoring inputs and derived operational graph views;
- feedback-loop semantics for failed gates, recurring exceptions, rollback patterns, and drift.

This repository SHALL NOT become the canonical implementation home for:

- platform storage or wire contracts;
- registry, signing, admission-controller, or CI/CD runtime enforcement;
- canonical platform ontology semantics;
- source-of-truth artifact custody.

Canonical boundaries remain:

- platform standards repositories own schema contracts when the profile is promoted into a platform-wide interface;
- runtime/platform repositories own emitters, validators, CI jobs, registry policy, and admission-control enforcement;
- Sociosphere owns repository inventory, dependency topology, ownership, and canonical-source namespace alignment;
- graph/reasoning repositories own query execution and policy reasoning surfaces;
- governance-ledger repositories own tamper-evident release-state transition records.

## Consequences

- The release doctrine becomes inspectable as operational intelligence before it is hardened into platform enforcement.
- Evidence bundles, baseline manifests, deployment BOMs, and change records can be tracked as ops-domain entities without forcing this repository to own their canonical platform schemas.
- Readiness remains a signal unless a downstream policy repository explicitly upgrades a control into a hard promotion gate.
- Emergency and exception flows stay first-class: they must produce evidence, reconciliation tasks, and graph-visible debt rather than disappearing into ad hoc manual procedure.

## Follow-on requirements

- Add the preproduction release doctrine document.
- Add a traceability matrix mapping doctrine requirements to evidence and enforcement primitives.
- Add a machine-readable profile and smoke test so control semantics remain stable.
- Later promote stable fields into platform standards and runtime validators.
