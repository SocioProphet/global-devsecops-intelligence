# Browser telemetry finding model

Status: draft v0.1

This note defines the operations-domain model for browser telemetry and browser capability-surface findings. It is intentionally scoped to classification, evidence handling, and domain mapping. It does not define canonical platform wire contracts, canonical storage contracts, or the full platform ontology.

## Purpose

Browser runtimes expose many surfaces that can be used for legitimate compatibility handling, diagnostics, telemetry, abuse prevention, or fingerprinting. Console traces often mix all of these classes together. The operations intelligence plane needs a finding model that separates observed facts from inferred intent.

The model supports two linked record types:

1. Browser trace classification: what was observed in a runtime/browser trace.
2. Upstream architecture mapping: where the relevant intake, evidence, telemetry, or replay surface lives in the SocioProphet estate.

The model deliberately avoids promoting a finding to adaptive adversarial probing unless the evidence shows a bridge from capability/preference checks to branching, retry behavior, or outbound payload mutation.

## Finding classes

| Class | Meaning | Evidence threshold |
|---|---|---|
| `capability_surface` | Browser or runtime support state is observable or queried. | API call, warning tied to a queryable feature, or instrumented trace. |
| `preference_surface` | User/OS preference state is observable or queried. | Media query, client hint, accessibility preference, or equivalent. |
| `telemetry_lane` | A network path can carry diagnostics, analytics, or event payloads. | Fetch, XHR, beacon, websocket, collector request, or server-side intake. |
| `collector_reachability` | Collector path succeeds, fails, or is blocked in a distinguishable way. | Network status, CSP report, blocked request, timeout, or retry state. |
| `blocker_detection_substrate` | The observed reachability matrix could support blocker detection. | At least two differentiated collector outcomes or a first-party fallback path. |
| `adaptive_branching_unproven` | Surfaces exist, but no code path proves behavior changes from the result. | Default conservative label when call-stack/payload bridge is absent. |
| `adaptive_probe_chain` | A support/preference/reachability result changes behavior or payloads. | Same stack, causal trace, differential payload, or retry branch. |

## Confidence states

| State | Definition |
|---|---|
| `observed` | Directly seen in trace, code, or runtime artifact. |
| `inferred` | Supported by surrounding evidence, but not directly observed. |
| `unproven` | Plausible but lacking a causal bridge. |
| `refuted` | Contradicted by code, trace, or controlled replay. |

## Required separation

A single investigation should keep these records separate unless a causal bridge exists:

- Runtime/browser trace evidence.
- Upstream repository architecture evidence.
- Server-side intake evidence.
- Replay/instrumentation evidence.

For example, a browser trace may prove capability-surface exposure and telemetry reachability. A repository may separately prove browser metadata intake and evidence publication. Those findings are related, but they should not be collapsed into one emitter-attribution claim without call-stack, bundle, or payload proof.

## Minimal finding envelope

A browser telemetry finding should capture:

- finding identifier
- source class and source origin
- observed surfaces
- telemetry lanes
- reachability outcomes
- confidence labels
- adaptive-branching status
- raw evidence references
- upstream architecture links
- recommended next evidence step

## Non-goals

This profile does not authorize stealth collection, browser exploitation, or bypass logic. Controlled replay belongs in an execution/evidence plane and must emit auditable artifacts. Public web/runtime surfaces should use the model for transparency, minimization, and policy binding, not for expanding high-entropy collection.
