# Incident Similarity Service (AI4IT Pipeline 3)

## Where this sits

The AI4IT reference architecture (an IBM Watson-AIOps-style design) has three
pipelines:

1. **Log Anomaly** — ingest large log volumes, detect anomalies per log.
2. **Event Grouping** — group events/alerts + log anomalies into incident
   "stories".
3. **Incident Similarity** — match incidents to the search terms an SRE
   provides.

This document specifies the first buildable slice of **Pipeline 3**, the
*Similar Incidents Service*, delivered as a sovereign contract + deterministic
scorer under `open-ai4it-spec/modules/story_services/incident_similarity/`.

We build our own equivalent (MIT / standard-library Python); we do not vendor or
fork any IBM/Watson proprietary component. The IBM ITOPS seed under
`third_party/ibm-itops/` remains an ontology seed only (see ADR 0001), not code.

## Contract

- **Query** (`incident-similarity-query.schema.json`): the SRE's free-text
  `terms`, a `query_id`, an optional `as_of_utc` (so the recency signal is
  time-independent and reproducible), optional `top_k`, and optional `weights` /
  `thresholds` overrides.
- **Result** (`incident-similarity-result.schema.json`): ranked `matches`, each
  with the raw per-signal `signals`, an `explainability` breakdown
  (`matched_terms` + `weighted_contributions`), an Assay `verdict`, plus a
  `receipt` sealing the whole computation under a SHA-256 trace hash.

These align with the AI4IT event envelope (`contracts/schemas/event-envelope.schema.json`):
a result maps onto an `insight` message whose `explainability` is the per-match
breakdown, whose `story_id` is the query id, and whose `feedback` slot is where
SRE thumbs-up/down would later close the loop.

## Scoring model (deterministic)

Final score is a weighted, normalized sum of four signals in `[0, 1]`:

| Signal | Definition | Default weight |
|---|---|---|
| `lexical` | Jaccard of query tokens vs incident title+summary+tags+entities | 0.5 |
| `entity_overlap` | Jaccard of query tokens vs incident entity tokens | 0.2 |
| `topology` | `1 / (1 + topology_distance)` (hops in the service graph) | 0.2 |
| `recency` | `1 / (1 + age_days)` measured against `as_of_utc` | 0.1 |

Weights are renormalized to sum 1. Ranking is score-descending with a stable
`incident_id` tie-break. Every emitted float is rounded to 6 decimals so output
is byte-reproducible across platforms — the precondition for the golden-file
teeth.

## Reused estate primitives

- **Receipt spine (provenance).** `build_receipt` seals the normalized query
  terms, sorted corpus ids, weights, thresholds, and the ranked `(id, score)`
  list under `sha256(...)` and emits `trace_hash: "sha256:<64 hex>"`. This is the
  same provenance discipline as sourceos-spec `ReasoningReceipt` and the
  platform `EvidenceReceipt`, kept offline and self-verifying. SHA-256 is the
  **FIPS-180-4 algorithm** — this is not a FIPS-140 cryptographic-module claim.
- **The Assay (ok/sad/bad).** `project_verdict` renders `(method, score)` to a
  verdict at read time: `ok` above the `ok` threshold, `sad` (real but
  low-confidence / unassayed) between `sad` and `ok`, `bad` below. `method` is
  always `computed` because the score is deterministic arithmetic, never
  generative. Because the verdict is a projection, history is re-judgeable if
  thresholds are recalibrated — the validator recomputes it and fails on drift.
- **HellGraph topology.** `topology_distance` is the hop count from the query's
  focus service to a candidate in the service topology graph. Modeling it as an
  input field keeps the scorer deterministic and unit-testable offline while, in
  production, the field is populated from the live HellGraph service graph.

## Teeth

`tools/validate_incident_similarity.py` (in `make validate`, run in CI) asserts:
golden reproducibility, determinism, receipt integrity, Assay projection
soundness, JSON-Schema conformance, and — both ways — that malformed inputs are
refused and a tampered result is detected as drift. `tools/tests/test_incident_similarity.py`
pins the same properties under pytest.

## What this deliberately is not (roadmap)

- No dense/embedding leg. Estate has `hellgraph/ts/src/bm25.ts`,
  `retrieval.ts` (RRF/MMR), and `sherlock-engine` (BM25⊕dense via RRF over
  Qdrant) — a hybrid upgrade path exists but is out of scope for this
  deterministic, dependency-free first slice.
- No event grouping / log-anomaly detection — those are Pipelines 2 and 1 and
  remain GAPs (tracked in the AIOps program issue).
- No live ASM ingestion — the topology signal consumes a distance field rather
  than discovering topology itself.
