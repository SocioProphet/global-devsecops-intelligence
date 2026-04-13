# IBM ITOPS GLO to operations-domain profile mapping ledger

Status model used in this file:
- `adopted`: carried directly into the ops-domain profile with minor normalization
- `mapped`: represented through a narrower or differently-scoped local concept
- `rejected`: not used as a canonical meaning in this repository
- `deferred`: potentially useful, but not yet stabilized for this profile

## First-pass class and relation decisions

| IBM GLO concept | Status | Ops-domain interpretation | Notes |
|---|---|---|---|
| `Organization` | mapped | organizational actor / owner / tenant / provider org | Too broad to use as a single canonical local class without specialization. |
| `Company` | mapped | company / business actor subtype | Retained only as a business-actor specialization when relevant to operations. |
| `Project` | rejected | not the canonical meaning for cloud project/account | IBM GLO treats `Project` as a `WorkProduct`; we will not equate that with GCP/Firebase/GitHub project containers. |
| `System` | adopted | system | Good operational root for interacting components. |
| `TechnicalSystem` | adopted | technical system | Useful for runtime / infrastructure system framing. |
| `Service` | adopted | service | Kept, but interpreted operationally rather than purely economically. |
| `Incident` | mapped | incident / issue / interruption event | Operationally valuable, but the upstream label/comment semantics need local normalization. |
| `State` | mapped | observed state / operational state | Mapped to observed state, not treated as the sole source of lifecycle semantics. |
| `Rule` | deferred | policy / rule / control | Needs alignment with policy and control surfaces upstream. |
| `Standard` | deferred | standard / compliance artifact | Likely useful, but not yet stabilized in this repo. |
| `TechnicalStandard` | deferred | technical standard | Same as above. |
| `Document` | adopted | document / evidence artifact | Useful for runbooks, tickets, KB entries, and evidence packaging. |
| `WorkProduct` | mapped | work artifact | Useful as a generic artifact class, not as a cloud resource class. |
| `partOf` | adopted | generic containment / composition edge | Useful, but not sufficient by itself for governance inheritance. |
| `hasPart` | adopted | inverse composition edge | Same caveat as `partOf`. |
| `sameReferentAs` | deferred | identity / resolution equivalence | Needs tighter identity governance before use. |
| `provenance` | adopted | provenance annotation | Directly useful for evidence-first import policy. |

## Immediate implications

1. IBM GLO is helpful as an upper / bridge ontology for operations-domain semantics.
2. IBM GLO is not sufficient as the canonical institutional digital-twin model.
3. Cloud-account hierarchy, deployment topology, IAM, DNS, certificates, and evidence lineage still need local domain classes and constraints.
4. The preferred first vendored payload remains `GLO_V1.ttl`; stage payloads stay deferred until query and validation strategy are in place.
