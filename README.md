# global-devsecops-intelligence

> Operations-domain profile for DevSecOps / AIOps / AI4IT operational intelligence.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Profile status: draft](https://img.shields.io/badge/profile-draft-yellow)](#status)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)](CONTRIBUTING.md)

---

## Table of contents

- [What this is](#what-this-is)
- [Repository structure](#repository-structure)
- [Ownership boundaries](#ownership-boundaries)
- [Status](#status)
- [Documentation](#documentation)
- [Validation](#validation)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

---

## What this is

This repository defines the **operations-domain specialization** for DevSecOps / AIOps / AI4IT operational intelligence, covering:

- AI4IT topic ladder and maturity model
- Ops entity extraction schemas and mapping DSL
- Story grouping, explainability, and feedback loops
- Operational measurement plane
- External seed ontology imports relevant to the operations-domain profile (currently IBM ITOPS)
- Mapping layers from external ontologies into the operations-domain profile
- Evidence-oriented operational graph projections scoped to this profile
- GitHub footprint alignment against workspace topology, ontology scaffolding, website surface taxonomy, operations integration planes, and institutional account hierarchy
- operational exhaust fusion across CI/CD, runtime, policy/evidence, market/execution, and trader-agent lanes

This repository does **not** own canonical platform storage standards, canonical wire contracts, or the sole canonical platform ontology / broader knowledge semantics.

---

## Repository structure

```
global-devsecops-intelligence/
├── docs/
│   ├── adr/                    # Architecture decision records
│   ├── architecture/           # Architecture and design notes
│   ├── devops/                 # DevOps process documentation
│   └── vision/                 # Vision and capability statements
├── examples/                   # Example and generated operational profile instances
├── mappings/                   # Ontology mapping ledgers
├── open-ai4it-spec/            # Open AI4IT contracts, schemas, and modules
│   ├── contracts/
│   │   ├── schemas/            # JSON Schema contracts
│   │   └── topics/             # Topic taxonomy
│   ├── docs/glossary/          # Terminology glossary
│   └── modules/openentitymap/  # Mapping DSL schema
├── profiles/                   # Machine-readable domain profiles
├── schemas/                    # Generated-projection schema contracts
├── source_inputs/              # Pinned upstream/manual source extracts for deterministic generators
├── tests/                      # Profile smoke checks and pytest wrappers
├── third_party/
│   └── ibm-itops/              # IBM ITOPS external seed import (metadata + curated excerpt)
├── tools/                      # Local validators and generators
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.txt
├── Makefile
├── README.md
└── SECURITY.md
```

---

## Ownership boundaries

| Repository | Owns |
|---|---|
| `socioprophet-standards-storage` | Base transport, storage, and interface invariants; canonical envelope and wire contracts |
| `ontogenesis` / `socioprophet-standards-knowledge` | Canonical ontology and broader knowledge semantics |
| **`global-devsecops-intelligence`** | Operations-domain profile; external seed ontology imports relevant to that profile; mapping layers; domain-scoped operational graph projections |

Institutional digital-twin semantics may appear here only insofar as they are needed to support the operations-domain profile. Where a concept has both a platform-wide canonical meaning and an operations-domain specialization, the canonical meaning remains upstream and this repository maintains only the specialization, binding, mapping, or projection.

Dependency direction:
```
platform standards → knowledge / ontology standards → global-devsecops-intelligence → runtime implementations
```

---

## Status

### External seed ontology

| Seed | Status | Notes |
|---|---|---|
| IBM ITOPS / `GLO_V1.ttl` | metadata-first import + curated profile excerpt | Full payload remains pending; curated profile excerpt is available at `third_party/ibm-itops/GLO_V1-profile-excerpt.ttl` |
| `ITOPS_S1`, `ITOPS_S2`, `ITOPS_S3` | deferred | Deferred until vendoring, validation, and query strategy are approved |

### GitHub-footprint alignment

| Plane | Provider | Status |
|---|---|---|
| Repository inventory / role ontology / dependency graph | `sociosphere` | active, pinned extract under `source_inputs/sociosphere/` |
| Provenance / policy / ontology-alignment scaffold | `ontogenesis` | active, pinned extract under `source_inputs/ontogenesis/` |
| Operations integration planes | GAIA World Model, Meshrush, Sherlock, SCOPED red-teaming | active/manual source extract under `source_inputs/integration-planes/` |
| Institutional account hierarchy | `socioprophet.ai` cloud-account hierarchy seed | manual seed under `source_inputs/institutional-account/`; live export pending |
| Normalized operational taxonomy for surfaces, workflow states, and capability routing | website surface inventory + public docs | active |
| Machine-readable profile | `profiles/github-footprint-itops-expansion.yaml` | draft `v0.1.0` |
| Example instance pack | `examples/github-footprint-itops-sample.yaml` | draft `v0.1.0` |
| Generated projection | `examples/github-footprint-itops-generated.yaml` | generated from `source_inputs/` |
| Generated-projection schema | `schemas/github-footprint-itops-generated.schema.json` | active contract |
| Generator | `tools/generate_github_footprint_itops_projection.py` | checked by `make validate` |
| Smoke checks | `tests/github-footprint-itops-smoke.yaml` + `tools/validate_github_footprint_itops.py` | active |

See [`docs/architecture/github-footprint-itops-alignment.md`](docs/architecture/github-footprint-itops-alignment.md) and [`docs/architecture/institutional-account-hierarchy-itops.md`](docs/architecture/institutional-account-hierarchy-itops.md) for the integration model.

### Operational-exhaust fusion

| Artifact | Status |
|---|---|
| `docs/devops/operational-exhaust-and-trader-agent-fusion.md` | draft |
| `profiles/operational-exhaust-fusion-profile.v0.yaml` | draft |
| `docs/adr/0002-operational-exhaust-and-trader-agent-fusion-boundary.md` | accepted |

---

## Documentation

| Document | Description |
|---|---|
| [`docs/vision/ai4it-home-rewrite.md`](docs/vision/ai4it-home-rewrite.md) | AI4IT / AIOps capability statement |
| [`docs/architecture/api-interactions-decision.md`](docs/architecture/api-interactions-decision.md) | CQRS-style API interactions design |
| [`docs/architecture/github-footprint-itops-alignment.md`](docs/architecture/github-footprint-itops-alignment.md) | GitHub footprint and website-surface alignment |
| [`docs/architecture/institutional-account-hierarchy-itops.md`](docs/architecture/institutional-account-hierarchy-itops.md) | Institutional account hierarchy semantics, findings, and live-binding obligations |
| [`docs/devops/devops-process-open.md`](docs/devops/devops-process-open.md) | DevOps process and branching policy |
| [`docs/adr/0001-ops-domain-profile-and-external-seed-boundary.md`](docs/adr/0001-ops-domain-profile-and-external-seed-boundary.md) | ADR 0001: ops-domain profile and external seed boundary |
| [`docs/adr/0002-operational-exhaust-and-trader-agent-fusion-boundary.md`](docs/adr/0002-operational-exhaust-and-trader-agent-fusion-boundary.md) | ADR 0002: operational exhaust and trader-agent fusion boundary |
| [`docs/devops/operational-exhaust-and-trader-agent-fusion.md`](docs/devops/operational-exhaust-and-trader-agent-fusion.md) | Ops-domain fusion model for platform and trader-agent exhaust |
| [`profiles/github-footprint-itops-expansion.yaml`](profiles/github-footprint-itops-expansion.yaml) | Machine-readable GitHub footprint ITOPS profile |
| [`examples/github-footprint-itops-sample.yaml`](examples/github-footprint-itops-sample.yaml) | Hand-authored GitHub footprint ITOPS instance pack |
| [`examples/github-footprint-itops-generated.yaml`](examples/github-footprint-itops-generated.yaml) | Generated projection from pinned source inputs, integration planes, and institutional account hierarchy |
| [`schemas/github-footprint-itops-generated.schema.json`](schemas/github-footprint-itops-generated.schema.json) | Schema contract for the generated GitHub-footprint ITOPS projection |
| [`profiles/operational-exhaust-fusion-profile.v0.yaml`](profiles/operational-exhaust-fusion-profile.v0.yaml) | Machine-readable operational exhaust fusion profile |
| [`mappings/ibm-itops-glo-to-ops-domain.md`](mappings/ibm-itops-glo-to-ops-domain.md) | IBM ITOPS GLO → ops-domain mapping ledger |
| [`open-ai4it-spec/docs/glossary/TERMS.md`](open-ai4it-spec/docs/glossary/TERMS.md) | Terminology glossary |
| [`third_party/ibm-itops/UPSTREAM.md`](third_party/ibm-itops/UPSTREAM.md) | IBM ITOPS upstream provenance and retrieval metadata |
| [`source_inputs/README.md`](source_inputs/README.md) | Source input snapshot policy |

For a guided tour of the documentation tree, see [`docs/README.md`](docs/README.md).

---

## Validation

Run all local validators:

```bash
make validate
```

The validation target currently covers:

- service-desk metrics examples
- model-fabric release-readiness scorecards
- generated GitHub-footprint projection freshness
- GitHub-footprint ITOPS profile, generated projection, integration planes, institutional account hierarchy, sample, smoke checks, mapping ledger, source inputs, schema, and IBM GLO profile excerpt

Regenerate the GitHub-footprint projection from pinned source inputs:

```bash
python3 tools/generate_github_footprint_itops_projection.py --write
```

Run all pytest wrappers:

```bash
make test
```

---

## Contributing

Contributions, issue reports, and discussion are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request or issue, and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Security

To report a security vulnerability, please follow the process described in [SECURITY.md](SECURITY.md). Do not open a public issue for security matters.

---

## License

This repository is licensed under the [MIT License](LICENSE).

Third-party materials vendored under `third_party/` carry their own upstream licenses — see the corresponding `LICENSE.*` files and `UPSTREAM.md` files for details.
