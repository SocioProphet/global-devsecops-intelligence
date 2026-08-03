# ResourceContract / Measurement telemetry ingestion

This profile makes `global-devsecops-intelligence` the first real **consumer** of sourceos-spec's
`Measurement` and `ResourceContract` (SourceOS-Linux/sourceos-spec, merged 2026-07-30).

## Why

Those two schemas exist to make two defects unrepresentable:

- a value nobody measured, reported as instrumented evidence;
- a limit that observes but never enforces — `Action taken: none`.

Two schemas whose purpose is catching *unused declarations* are worthless if they are themselves
declared by nobody. This profile is the consumer that closes that gap. It also completes a
producer → consumer → learning loop:

```text
producer:  a runner/gate emits a ResourceContract (limit + gate-eligible Measurement of peak)
consumer:  this plane normalizes it -> TelemetrySignal + EvidenceArtifact  (ops.* topics)
learning:  a SufficiencyVerdict on ops.learning.feedback.v1 is scored by sociosphere's
           proof_artifact contract, which feeds back which controls actually have teeth
```

## The verdict algebra is sociosphere's, not a new one

Gate-eligibility maps onto `sufficiency_type` from `sociosphere/catalog/evidence-contracts.yaml`,
so the loop speaks one language end to end:

| condition | verdict | meaning |
|---|---|---|
| `enforcement != observe` and `fired_count > 0` and peak gate-eligible | **PROVED** | the control has been observed to act on real load |
| `enforcement != observe` and `observedPeak.value > limit.value` and `fired_count == 0` | **VIOLATION** | never-fired control — a counterexample to the claim it is a control |
| peak not gate-eligible (`source != measured` or `unobserved > 0`) | **INCONCLUSIVE** | sufficiency unestablished; no verdict on the control can be drawn |
| `enforcement == observe` and `observedPeak.value > limit.value` | **INCONCLUSIVE** | a declared gauge, not a gate — no teeth-claim to prove or violate |

The **VIOLATION** row is the load-bearing one. A limit that *claimed teeth* and was exceeded in
production yet never once enforced is not an absence of news — it is evidence the control is
paper. The rule `never_fired_control_is_a_violation` forbids dropping it, summarizing it to a
healthy counter, or downgrading it to INCONCLUSIVE.

The `enforcement != observe` guard on that row is itself load-bearing. VIOLATION is a **broken
enforcement promise**, and `observe` mode makes no promise — it is the honest, declared "gauge,
not gate" (ResourceContract requires an `observeOnlyReason` for it). An observe-mode exceedance is
therefore **INCONCLUSIVE**, per `observe_mode_exceedance_is_inconclusive_not_violation`: flagging
it VIOLATION would accuse a gauge of failing to be a gate and punish honest declaration. The
exceedance is never hidden either way — it flows as a `resource-saturation` TelemetrySignal
regardless of verdict, so an operator can still decide to promote the gauge to an enforcing limit.

## Canonical objects and topics

- `TelemetrySignal` (`signal_class: resource-saturation`) → `ops.telemetry.signals.v1`
- `EvidenceArtifact` (the ResourceContract as governed, replayable evidence) → `ops.evidence.artifacts.v1`
- `SufficiencyVerdict` (PROVED / VIOLATION / INCONCLUSIVE) → `ops.learning.feedback.v1`

## Invariants preserved through normalization

- **Gate-eligibility is carried through, never recomputed.** It is a ceiling set by the producer
  that owns the instrument; a consumer may lower it, never raise it.
- **Scope is preserved.** A process-scoped and a tenant-scoped limit make different claims;
  collapsing them hides the fan-out under which a per-process limit is defeated by N cooperating
  processes each staying under it.
- **Acting enforcement requires a resolvable negative control**, mirroring the ResourceContract
  schema's own invariant — a claim to enforce with no demonstration that enforcement can act is
  inadmissible as evidence.

See `mappings/resource-contract-measurement-telemetry-v1.yaml` and the worked example
`examples/resource-contract-telemetry.example.json` (a build-runner CPU limit exceeded in
production that never throttled → VIOLATION).
