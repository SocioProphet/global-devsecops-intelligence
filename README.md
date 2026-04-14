# global-devsecops-intelligence

> Operations-domain profile for DevSecOps / AIOps / AI4IT operational intelligence.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Profile status: draft](https://img.shields.io/badge/profile-draft-yellow)](#status)
[![Contributions welcome](https://img.shields.io/badge/contributions-welcome-brightgreen)](CONTRIBUTING.md)

---

## Table of contents

- [What this is](#what-this-is)
- [Repository structure](#repository-structure)
- [Ownership boundaries](#ownership-boundaries)
- [Status](#status)
- [Documentation](#documentation)
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
- GitHub footprint alignment against workspace topology, ontology scaffolding, and website surface taxonomy

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
├── mappings/                   # Ontology mapping ledgers
├── open-ai4it-spec/            # Open AI4IT contracts, schemas, and modules
│   ├── contracts/
│   │   ├── schemas/            # JSON Schema contracts
│   │   └── topics/             # Topic taxonomy
│   ├── docs/glossary/          # Terminology glossary
│   └── modules/openentitymap/  # Mapping DSL schema
├── profiles/                   # Machine-readable domain profiles
├── third_party/
│   └── ibm-itops/              # IBM ITOPS external seed import (metadata-first)
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── MANIFEST.txt
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
| IBM ITOPS / `GLO_V1.ttl` | metadata-first import | Preferred first payload for semantic alignment — see `third_party/ibm-itops/` |
| `ITOPS_S1`, `ITOPS_S2`, `ITOPS_S3` | deferred | Deferred until vendoring, validation, and query strategy are approved |

### GitHub-footprint alignment

| Plane | Provider | Status |
|---|---|---|
| Repository inventory / role ontology / dependency graph | `sociosphere` | active |
| Provenance / policy / ontology-alignment scaffold | `ontogenesis` | active |
| Normalized operational taxonomy for surfaces, workflow states, and capability routing | website surface inventory + public docs | active |
| Machine-readable profile | `profiles/github-footprint-itops-expansion.yaml` | draft `v0.1.0` |

See [`docs/architecture/github-footprint-itops-alignment.md`](docs/architecture/github-footprint-itops-alignment.md) for the full integration model.

---

## Documentation

| Document | Description |
|---|---|
| [`docs/vision/ai4it-home-rewrite.md`](docs/vision/ai4it-home-rewrite.md) | AI4IT / AIOps capability statement |
| [`docs/architecture/api-interactions-decision.md`](docs/architecture/api-interactions-decision.md) | CQRS-style API interactions design |
| [`docs/architecture/github-footprint-itops-alignment.md`](docs/architecture/github-footprint-itops-alignment.md) | GitHub footprint and website-surface alignment |
| [`docs/devops/devops-process-open.md`](docs/devops/devops-process-open.md) | DevOps process and branching policy |
| [`docs/adr/0001-ops-domain-profile-and-external-seed-boundary.md`](docs/adr/0001-ops-domain-profile-and-external-seed-boundary.md) | ADR 0001: ops-domain profile and external seed boundary |
| [`mappings/ibm-itops-glo-to-ops-domain.md`](mappings/ibm-itops-glo-to-ops-domain.md) | IBM ITOPS GLO → ops-domain mapping ledger |
| [`open-ai4it-spec/docs/glossary/TERMS.md`](open-ai4it-spec/docs/glossary/TERMS.md) | Terminology glossary |
| [`third_party/ibm-itops/UPSTREAM.md`](third_party/ibm-itops/UPSTREAM.md) | IBM ITOPS upstream provenance and retrieval metadata |

For a guided tour of the documentation tree, see [`docs/README.md`](docs/README.md).

---

## Contributing

Contributions, issue reports, and discussion are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request or issue, and follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Security

To report a security vulnerability, please follow the process described in [SECURITY.md](SECURITY.md). Do not open a public issue for security matters.

---

## License

This repository is licensed under the [Apache License 2.0](LICENSE).

Third-party materials vendored under `third_party/` carry their own upstream licenses — see the corresponding `LICENSE.*` files and `UPSTREAM.md` files for details.
