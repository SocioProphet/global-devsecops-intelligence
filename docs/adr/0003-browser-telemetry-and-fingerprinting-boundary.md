# ADR 0003: Browser telemetry and fingerprinting boundary

Status: accepted

Date: 2026-05-04

## Context

Browser console traces often contain a mixed stream of compatibility warnings, capability checks, preference surfaces, analytics traffic, first-party telemetry, third-party collector failures, and content-security-policy diagnostics. These traces are operationally useful, but they are easy to over-classify.

The operations-domain profile needs a conservative boundary that distinguishes:

- fingerprinting-capable surfaces
- confirmed telemetry collection
- blocker-detection substrate
- proven adaptive adversarial probing

The last category requires stronger evidence than parser warnings or blocked analytics requests alone.

## Decision

`global-devsecops-intelligence` will model browser telemetry findings as operations-domain intelligence records with explicit confidence and causality fields.

The domain profile may classify a trace as `fingerprinting_capable_substrate` when it includes capability/preference surfaces plus outbound telemetry lanes. It may classify `blocker_detection_substrate` when differentiated collector reachability is observed. It must not classify `adaptive_probe_chain` unless there is a call-stack, replay, code path, differential payload, or retry branch proving that the surface result changed behavior.

Raw runtime evidence, upstream architecture mappings, and server-side intake code paths must remain separate linked findings until a causal bridge is proven.

## Consequences

Positive consequences:

- Findings remain evidence-grade and auditable.
- Browser compatibility noise is not over-promoted to hostile intent.
- Confirmed metadata intake can be documented without conflating it with high-entropy capability harvesting.
- Runtime and replay work can consume the same finding schema.

Negative consequences:

- Some suspicious traces will remain conservatively labeled as `adaptive_branching_unproven` until replay or bundle evidence exists.
- The profile requires more fields than a simple narrative incident note.

## Repository boundary

This repository owns the operations-domain classification, finding profile, mappings, and examples. Runtime contracts and replay execution should land downstream in platform or execution-control repositories.

## Acceptance criteria

A browser telemetry finding is acceptable in this repository when it includes:

1. observed surfaces;
2. telemetry lanes;
3. reachability outcomes;
4. adaptive-branching status;
5. evidence references;
6. recommended next evidence step;
7. explicit confidence labels.
