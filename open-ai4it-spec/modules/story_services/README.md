# story_services

The `story_services` module is the AI4IT reference architecture's third stage:
turning grouped alerts/incidents into things an SRE can act on. It covers four
independently-replaceable services:

| Service | Reference role | Status in this repo |
|---|---|---|
| `incident_similarity/` | Similar Incidents Service — rank prior incidents against SRE search terms | **BUILT** (contract + deterministic scorer + teeth) |
| grouping | Event Grouping Service — assemble alerts/anomalies into incident "stories" | GAP (spec only; topics declared in `contracts/topics/topics.yaml`) |
| story localization | Localization Service — locate the failing component within a story | GAP (blast-radius primitive exists estate-side: `sociosphere/gbrg`) |
| topology / blast radius | Topology Service / ASM overlay | GAP (graph substrate exists estate-side: `hellgraph`) |

## incident_similarity (built)

A sovereign, dependency-free equivalent of a Watson-AIOps-style *Similar
Incidents Service*. It is **consume-not-fork**: no IBM/Watson code, MIT-licensed
Python standard library only.

- **Contract:** `contracts/schemas/incident-similarity-query.schema.json` (SRE
  search terms + optional scoring overrides) and
  `contracts/schemas/incident-similarity-result.schema.json` (ranked matches with
  per-signal explainability, an Assay verdict, and a SHA-256 provenance receipt).
- **Scorer:** `incident_similarity/scorer.py` — deterministic, offline, no
  wall-clock. Four signals (lexical Jaccard, entity overlap, topology proximity,
  recency) combined under normalized weights; stable tie-break by `incident_id`.
- **Estate primitives reused (not reinvented):**
  - *Receipt spine* — every result is sealed under a `sha256:` trace hash over
    the normalized inputs and the ranked output (mirrors sourceos-spec
    `ReasoningReceipt.traceHash`; SHA-256 is the FIPS-180-4 algorithm, not a
    FIPS-140 module claim).
  - *The Assay* — each match carries an `ok`/`sad`/`bad` verdict with
    `method: computed`, projected from the score at read time and
    re-projectable if thresholds change.
  - *HellGraph topology* — the `topology_distance` field (hop count from the
    query focus service in the service graph) feeds the topology signal; the
    scorer stays offline and testable while that field is fed by the live graph
    in production.
- **Teeth:** `tools/validate_incident_similarity.py` (wired into `make validate`)
  and `tools/tests/test_incident_similarity.py` enforce golden reproducibility,
  determinism, receipt integrity, verdict soundness, schema conformance, and
  rejection of malformed inputs — proven to fail on a perturbed golden.

Run it:

```
python3 open-ai4it-spec/modules/story_services/incident_similarity/scorer.py \
  --query examples/incident-similarity/query.example.json \
  --corpus examples/incident-similarity/corpus.example.json
make incident-similarity-validate
```
