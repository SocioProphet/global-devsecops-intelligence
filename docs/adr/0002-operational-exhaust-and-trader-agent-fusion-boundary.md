# ADR 0002: Operational Exhaust and Trader-Agent Fusion Boundary

## Status
Proposed

## Context

`global-devsecops-intelligence` already defines itself as the operations-domain specialization for DevSecOps / AIOps / AI4IT operational intelligence.
That declared scope already includes logs, telemetry, reusable evidence artifacts, operational measurement, learning loops, and derived operational graph projections.

Two pressure points now need an explicit boundary decision:

1. platform operational exhaust is being emitted across CI/CD, runtime services, agent surfaces, policy/evidence lanes, and deployment control planes;
2. trader-agent systems will emit the same class of operational exhaust, but with market-data, strategy-run, execution, risk-control, and replay-specific fields.

Without an explicit boundary, these streams could drift into:
- repo-local telemetry silos,
- duplicated observability grammars across platform vs trader-agent systems,
- or accidental redefinition of canonical storage, wire, or ontology semantics inside an ops-domain repository.

## Decision

This repository SHALL own the **operations-domain projection** for operational exhaust fusion across:
- CI/CD and delivery telemetry,
- runtime/service/agent health telemetry,
- policy/evidence receipts,
- market-data and execution operations telemetry,
- trader-agent learning-loop and post-run operational feedback signals.

This repository SHALL NOT become the canonical home for:
- canonical wire contracts,
- canonical storage semantics,
- canonical market or portfolio ontology semantics,
- or the sole canonical platform ontology.

Canonical boundaries remain:
- `socioprophet-standards-storage` for base transport, storage, and interface invariants,
- `ontogenesis` and `socioprophet-standards-knowledge` for canonical ontology and broader knowledge semantics,
- domain runtimes and standards repositories for domain-native event semantics.

This repository only owns:
- the ops-domain projection,
- the mapping of upstream events into ops-domain operational intelligence,
- story grouping and correlation,
- operational measurement and feedback loops,
- and derived operational graph views.

## Consequences

- Platform telemetry and trader-agent telemetry can share one evidence grammar and one fusion layer without collapsing their canonical semantics into the same upstream model.
- Sensitive raw payloads should be referenced by artifact handles, hashes, and evidence receipts rather than copied wholesale into ops-domain projections.
- Trader-agent telemetry can be fused with DevSecOps / AIOps telemetry for incident analysis, policy review, and operational learning while preserving domain ownership boundaries.
- External influences such as Ge Chu / Alexei Lisitsa-style ontology- and BDI-agent-based security automation may be used as mapped seed influences for the ops-domain profile, but must not replace canonical platform ontology ownership.

## Follow-on requirements

- Add a machine-readable operational exhaust fusion profile.
- Add ops-domain mappings for trader-agent operational projections.
- Add runtime-side emitter guidance so platform and trader-agent systems emit compatible evidence-oriented exhaust.
