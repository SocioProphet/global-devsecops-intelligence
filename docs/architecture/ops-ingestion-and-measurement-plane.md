# Ops Ingestion and Measurement Plane

## Purpose

This document defines the operations-domain ingestion and measurement plane for `global-devsecops-intelligence`.

The goal is to normalize logs, telemetry, tickets, chatops events, anomalies, incident stories, metering, and explainability into a governed AI4IT operational intelligence layer that can be consumed by support, premium support, search, runtime evaluation, and bounded agent execution.

## Repository boundary

`global-devsecops-intelligence` owns the operations-domain profile built on top of upstream platform and ontology standards.

It does **not** own:

- base transport and storage invariants
- canonical ontology semantics
- generic runtime execution fabrics

Those are upstream concerns owned by `socioprophet-standards-storage`, `ontogenesis`, and runtime repos such as `prophet-platform` and `agentplane`.

## Required upstream dependencies

### Semantic layer
`ontogenesis` defines the semantic classes and relationships for:

- `LogEvent`
- `TelemetryEvent`
- `TicketEvent`
- `ChatOpsEvent`
- `AnomalyFinding`
- `IncidentStory`
- `MeterRecord`
- `OpsRecommendation`
- `OpsEvidenceArtifact`
- `SupportOpsContext`

### Transport and storage layer
`socioprophet-standards-storage` defines:

- canonical envelopes
- wire contracts
- storage portability and retention profiles
- schema versioning rules
- base validation gates

## Ingestion pipeline

```text
Raw source
  -> envelope / transport validation
  -> semantic class resolution
  -> ops entity extraction
  -> topic ladder classification
  -> grouping / correlation
  -> anomaly detection and scoring
  -> metering normalization
  -> explainability packaging
  -> evidence artifact generation
  -> downstream query / support / eval / memory consumers
```

## Accepted source classes

### Logs
Application logs, service logs, security logs, audit logs, infrastructure logs, deployment logs.

### Telemetry
Metrics, traces, counters, SLO signals, resource saturation, quality and latency signals.

### Service desk and workflow
Ticket systems, case systems, change approvals, escalation workflows, support summaries.

### ChatOps and collaboration
Matrix room events, support-room events, human-agent workflow annotations, collaboration-derived incident evidence.

## Canonical processing stages

### 1. Entity extraction
Extract services, systems, environments, tenants, teams, route surfaces, workflow identifiers, ticket IDs, knowledge assets, and support interactions.

### 2. Topic ladder mapping
Map observations into the AI4IT topic ladder so downstream consumers can reason over a stable operational taxonomy.

### 3. Story grouping
Convert fragmented observations into coherent `IncidentStory` and `OperationalStory` groupings.

### 4. Anomaly processing
An anomaly is not merely a spike. It must become a typed, explainable finding with confidence, severity, scope, and evidence lineage.

### 5. Metering normalization
Metering must include not only cost and usage, but support load, asset reuse rate, recommendation acceptance, anomaly frequency, time to resolution, premium-support uplift, and runbook effectiveness.

### 6. Explainability packaging
Every operationally significant grouping should support an explainability layer that can be surfaced in support and Matrix chatops contexts.

### 7. Evidence artifact generation
Create reusable evidence bundles that can be attached to support responses, recommendations, escalations, promotions, and replay workflows.

## Downstream consumers

### Support and premium support
Support agents consume normalized incident stories, anomaly findings, meter records, and evidence artifacts rather than raw telemetry.

### Sherlock query plane
`Sherlock-search` should query this repo's normalized ops-domain plane rather than inspect raw source streams directly.

### Memory Mesh
`memory-mesh` receives long-horizon retained operational memory derived from normalized findings and resolution outcomes.

### Meshrush
`meshrush` consumes short-horizon pressure from fresh anomaly and metering outputs for rapid adaptation.

### Prophet Platform
`prophet-platform` hosts runtime APIs, dashboards, preview, and evaluation services over the normalized ops-domain objects.

### Agentplane
`agentplane` can execute bounded diagnostics, remediation bundles, replay, or evidence-linked actions using normalized operational context.

## Hard rules

1. No support or premium-support action should rely on raw telemetry directly.
2. No anomaly should be surfaced without explainability lineage and evidence references.
3. Metering must be queryable at both generic and tier-aware support scopes.
4. Story grouping and ops-domain interpretation happen here before downstream consumption.

## Immediate implementation tranche

1. Define the ops-domain object model and schema contracts.
2. Add entity extraction and topic-ladder mapping semantics.
3. Add anomaly, story-grouping, and metering normalization contracts.
4. Expose runtime query surfaces to Sherlock, support agents, and evaluation services.
