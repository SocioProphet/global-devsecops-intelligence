# DevSecOps Telemetry Surface Profile

## Purpose
This document defines the operations-domain telemetry surface for `global-devsecops-intelligence`.

It does **not** redefine upstream transport, storage, or canonical envelope invariants. Those remain owned by `socioprophet-standards-storage`.

This profile defines how telemetry is specialized for:
- AI4IT / operational intelligence,
- DevSecOps runtime and release control,
- incident, evidence, and ticket operations,
- reusable operational learning loops.

## Design position
The operations-domain telemetry surface is organized into six planes:
1. **product plane** — user-visible and operator-visible state transitions.
2. **control plane** — feature gates, experiments, dynamic config, and preflight control decisions.
3. **data plane** — queries, caches, fetches, batch jobs, model lookups, and artifact/materialization flows.
4. **failure plane** — recoverable, caught, uncaught, and user-perceived failures.
5. **recovery plane** — retries, scoped evictions, fallback rendering, backoff, circuit-open, rollbacks.
6. **security plane** — policy decisions, evidence-chain integrity, attestations, SBOM/VEX status, and supply-chain security findings.

## Canonical operational object families
This profile normalizes source telemetry into these operational object families:
- `TelemetrySignal`
- `DetectionSignal`
- `EvidenceArtifact`
- `FindingRecord`
- `PolicyDecision`
- `IntelligenceAssertion`
- `LearningFeedback`
- `CorrelationContext`

## Required correlation context
The operations profile requires the following identifiers whenever applicable:
- `trace_id`
- `span_id`
- `request_id`
- `pipeline_run_id`
- `build_id`
- `deploy_id`
- `environment`
- `artifact_digest`
- `ticket_id`
- `incident_id`
- `query_hash`
- `cache_key`
- `policy_decision_id`

## Operational event classes
The following event families are first-class in this profile:

### Platform/runtime
- `runtime.bootstrap.ready`
- `runtime.component.started`
- `runtime.component.stopped`
- `runtime.component.degraded`
- `runtime.error.caught`
- `runtime.error.uncaught`
- `runtime.recovery.executed`

### Pipeline / CI-CD
- `pipeline.run.started`
- `pipeline.run.finished`
- `pipeline.step.failed`
- `artifact.promoted`
- `release.blocked`
- `rollback.executed`

### Supply chain / security
- `sbom.generated`
- `vex.assertion.created`
- `attestation.verified`
- `attestation.failed`
- `policy.decision.emitted`
- `finding.ingested`
- `evidence.chain.broken`

### Incident / ops intelligence
- `incident.created`
- `incident.correlated`
- `ticket.clustered`
- `story.grouped`
- `evidence.linked`
- `operator.feedback.submitted`
- `learning.loop.materialized`

### Data / cache / model
- `query.cache.hit`
- `query.cache.miss`
- `query.cache.write_failed`
- `query.fetch.failed`
- `model.inference.completed`
- `model.inference.degraded`
- `dataset.materialized`

## Adapter policy
This profile accepts these upstream signal sources:
- OpenTelemetry runtime signals
- SARIF security findings
- CycloneDX xBOM metadata
- OpenVEX VEX statements
- STIX/TAXII intelligence feeds
- OPA/Rego policy decisions
- internal event-bus facts

All such sources MUST be normalized into the operational object families above before they are treated as durable DevSecOps intelligence.

## Topic bindings
Recommended domain topics:
- `ops.telemetry.signals.v1`
- `ops.security.findings.v1`
- `ops.policy.decisions.v1`
- `ops.evidence.artifacts.v1`
- `ops.learning.feedback.v1`
- `ops.incidents.lifecycle.v1`

## Recovery policy
This profile explicitly rejects broad destructive recovery as a default. Recovery events SHOULD identify:
- target namespace,
- target feature surface,
- cache or storage segment,
- policy justification,
- resulting operator impact.

## Relationship to upstream repos
- Upstream standards repo defines portable invariants.
- This repo defines the operations-domain specialization.
- Prophet Platform consumes both to implement runtime and deployment behavior.
