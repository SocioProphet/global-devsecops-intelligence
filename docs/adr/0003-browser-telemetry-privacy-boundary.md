# ADR 0003: Browser telemetry privacy boundary

Status: accepted

Date: 2026-05-04

## Context

Browser console traces often contain a mixed stream of compatibility warnings, capability checks, preference surfaces, analytics traffic, first-party telemetry, third-party collector failures, and content-security-policy diagnostics. These traces are operationally useful, but they are easy to over-classify.

The operations-domain profile needs a conservative boundary that distinguishes:

- privacy-relevant browser surfaces
- confirmed telemetry collection
- collector reachability substrate
- confirmed behavioral coupling

The last category requires stronger evidence than parser warnings or blocked analytics requests alone.

## Decision

`global-devsecops-intelligence` will model browser telemetry findings as operations-domain intelligence records with explicit confidence and causality fields.

The domain profile may classify a trace as `privacy_relevant_surface` when it includes capability or preference surfaces plus outbound telemetry lanes. It may classify `collector_reachability_substrate` when differentiated collector reachability is observed. It must not classify `confirmed_behavioral_coupling` unless there is a call-stack, replay, code path, differential payload, or retry branch proving that the surface result changed behavior.

Raw runtime evidence, upstream architecture mappings, and server-side intake code paths must remain separate linked findings until a causal bridge is proven.

## Consequences

Positive consequences:

- Findings remain evidence-grade and auditable.
- Browser compatibility noise is not over-promoted to intent.
- Confirmed metadata intake can be documented without conflating it with high-entropy capability collection.
- Runtime and replay work can consume the same finding schema.

Negative consequences:

- Some suspicious traces will remain conservatively labeled as `causality_status: unproven` until replay or bundle evidence exists.
- The profile requires more fields than a simple narrative incident note.

## Repository boundary

This repository owns the operations-domain classification, finding profile, mappings, and examples. Runtime contracts and replay execution should land downstream in platform or execution-control repositories.

## Acceptance criteria

A browser telemetry finding is acceptable in this repository when it includes:

1. observed surfaces;
2. telemetry lanes;
3. reachability outcomes;
4. causality status;
5. evidence references;
6. recommended next evidence step;
7. explicit confidence labels.
