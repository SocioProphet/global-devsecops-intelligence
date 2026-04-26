# Broker Operational Intelligence Binding

## Purpose

This repository is the operations-domain intelligence layer for the cross-cloud services broker model.

It does not own the broker standard or broker runtime. It ingests broker operational exhaust and projects it into evidence-backed operational intelligence.

## Inputs

Broker reasoning inputs include:

- broker request events
- provider-binding decisions
- policy decisions
- exception records
- service-instance lifecycle events
- evidence-pack completeness updates
- cost-meter updates
- AgentPlane validation, placement, run, and replay artifacts
- SocioSphere hardening and propagation findings
- Academy training and evaluation promotion signals

## Reasoning outputs

This repo should define or project:

- `BrokerRiskFinding`
- `ProviderBindingRecommendation`
- `PortabilityTierAssessment`
- `EvidenceCompletenessFinding`
- `CostAnomalyFinding`
- `PolicyExceptionAgingFinding`
- `ServiceClassCoverageGap`

## Operational graph entities

Recommended entities:

- `ServiceClass`
- `ProviderClass`
- `ProviderBinding`
- `PolicyPack`
- `PolicyDecision`
- `ExceptionRecord`
- `ServiceRequest`
- `ServiceInstance`
- `EvidencePack`
- `CostMeter`
- `RunArtifact`
- `ReplayArtifact`
- `Incident`
- `Repo`
- `PR`
- `WorkflowRun`
- `HardeningFinding`
- `LearningObject`

## Design invariant

This repository reasons over broker exhaust. It must not become the canonical standards home or the broker runtime implementation.
