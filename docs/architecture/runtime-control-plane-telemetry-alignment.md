# Runtime Control Plane Telemetry Alignment

## Purpose
This document updates the operations telemetry profile after the current platform movement across `prophet-platform`, `policy-fabric`, `agentplane`, and this repository.

The existing telemetry surface profile remains the baseline. This document binds it to the newer evidence and operational intelligence surfaces.

## Current operational anchors
Operational telemetry SHOULD normalize signals from:

- model-fabric release readiness scorecards,
- broker operational intelligence bindings,
- agentic service desk metrics,
- Policy Fabric diff hygiene gate reports,
- AgentPlane agentic PR work orders,
- Prophet Platform runtime dry-run records,
- Prophet Platform live cluster preflight records,
- identity context records,
- parity-readiness records.

## Required canonical references
Every runtime-control-plane operational signal SHOULD preserve:

- `artifact_digest`
- `policy_decision_id`
- `agentplane_run_id`
- `agentic_pr_work_order_id`
- `diff_hygiene_gate_report_id`
- `service_desk_metric_ref`
- `release_readiness_scorecard_ref`
- `runtime_dry_run_record_ref`
- `live_cluster_preflight_record_ref`
- `identity_context_ref`

## Signal families
The operations profile SHOULD distinguish:

- `ops.release_readiness.*`
- `ops.diff_hygiene.*`
- `ops.agentic_pr.*`
- `ops.service_desk.*`
- `ops.runtime_preflight.*`
- `ops.policy_decision.*`
- `ops.identity_context.*`
- `ops.learning_feedback.*`

## Drift detection
The operations layer SHOULD detect drift between:

- upstream standards and platform runtime docs,
- policy-fabric gates and platform policy telemetry,
- agentplane work orders and platform agent run telemetry,
- identity context schemas and runtime identity references,
- release readiness scorecards and actual promotion evidence.

## Redaction and evidence handling
Raw bootstrap captures, browser console dumps, signed URLs, and session-bearing artifacts MUST be redacted before ingestion into durable operational evidence stores.

The canonical object should keep a redaction receipt rather than raw sensitive material.

## Follow-on implementation
The next implementation tranche SHOULD add schema-backed examples that map:

- Policy Fabric diff hygiene reports to `DetectionSignal` and `PolicyDecision`,
- AgentPlane work orders to `CorrelationContext` and `LearningFeedback`,
- platform runtime records to `EvidenceArtifact`,
- readiness scorecards to `IntelligenceAssertion`.
