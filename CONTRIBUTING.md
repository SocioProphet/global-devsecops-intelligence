# Contributing to global-devsecops-intelligence

Thank you for your interest in contributing. This document describes how to contribute effectively to this repository while staying aligned with its ownership boundaries and governance model.

---

## Table of contents

- [Code of Conduct](#code-of-conduct)
- [Scope of this repository](#scope-of-this-repository)
- [Ways to contribute](#ways-to-contribute)
- [Development workflow](#development-workflow)
- [Branching and merging policy](#branching-and-merging-policy)
- [Pull request process](#pull-request-process)
- [Architecture Decision Records (ADRs)](#architecture-decision-records-adrs)
- [Ontology and mapping contributions](#ontology-and-mapping-contributions)
- [External seed ontology import policy](#external-seed-ontology-import-policy)
- [Documentation standards](#documentation-standards)
- [Commit message conventions](#commit-message-conventions)

---

## Code of Conduct

All contributors are expected to follow the [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before participating.

---

## Scope of this repository

Before contributing, confirm that your change belongs here:

**This repository owns:**
- The operations-domain profile for DevSecOps / AIOps / AI4IT operational intelligence
- External seed ontology imports relevant to that profile (under `third_party/`)
- Mapping layers from external ontologies into the operations-domain profile (under `mappings/`)
- Operational query patterns, extraction schemas, taxonomy profiles, and evidence-oriented constraints
- Derived operational graph projections scoped to the operations-domain profile

**This repository does not own:**
- Canonical platform storage standards or wire contracts (`socioprophet-standards-storage`)
- Canonical ontology and broader knowledge semantics (`ontogenesis`, `socioprophet-standards-knowledge`)
- Platform-wide digital-twin semantics that are not specifically an operations-domain specialization

If your contribution belongs to an upstream repository, please open the issue or PR there instead.

---

## Ways to contribute

- **Bug reports and corrections** — factual errors, broken links, or inconsistencies in documentation or schemas
- **Profile and schema improvements** — refinements to the operations-domain profile, entity extraction schemas, or mapping DSL
- **Ontology mapping ledger updates** — new adopt/map/reject/defer decisions for external seed concepts
- **New ADRs** — significant decisions about this repository's design or governance
- **Documentation improvements** — clarity, completeness, or structure of existing docs
- **New external seed imports** — additional third-party ontologies relevant to the operations domain (subject to import policy below)

---

## Development workflow

1. Fork the repository and create a branch from `dev` (not `main`).
2. Make your changes following the standards in this document.
3. Run any applicable validation (schema linting, link checking) locally before opening a PR.
4. Open a pull request against `dev` with a clear description.
5. Address review feedback iteratively.
6. A maintainer will merge to `dev` once all checks pass and review is approved.
7. Releases are cut by merging `dev` → `main` with a version tag.

---

## Branching and merging policy

- `main` is the release branch. Direct pushes are not permitted.
- `dev` is the integration branch. All feature/fix work merges here first.
- Feature branches should be short-lived and named descriptively (e.g., `feat/add-incident-mapping`, `fix/glo-provenance-adoption`, `docs/adr-0002`).
- Prefer squash merge with a curated summary commit when merging feature branches into `dev`.

---

## Pull request process

1. Use the pull request template provided in `.github/PULL_REQUEST_TEMPLATE.md`.
2. Link any related issues in the PR description.
3. Keep PRs focused — one logical change per PR where possible.
4. All PRs require at least one approving review from a maintainer.
5. CI status checks must pass before merge.
6. Update `CHANGELOG.md` with a summary of changes under the `[Unreleased]` section.
7. Update `MANIFEST.txt` if you add or remove files.

---

## Architecture Decision Records (ADRs)

Significant design decisions that affect the repository's structure, governance model, or external boundaries should be documented as ADRs in `docs/adr/`.

ADR format:
```
# ADR NNNN: <short title>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR NNNN

## Context
<Why this decision was needed>

## Decision
<What was decided>

## Consequences
<What follows from this decision>
```

ADRs are numbered sequentially. File them as `docs/adr/NNNN-<slug>.md`. Once accepted, ADRs should not be edited — supersede them with a new ADR if the decision changes.

---

## Ontology and mapping contributions

When contributing to the mapping ledger (`mappings/`) or the operations-domain profile:

- Use the four-status model: `adopted`, `mapped`, `rejected`, `deferred`.
- Provide a brief rationale for every status decision.
- Do not promote an external concept to `adopted` if it conflicts with an upstream canonical meaning without first consulting the upstream repository owners.
- Record any new controlled vocabulary terms in the relevant profile YAML.

---

## External seed ontology import policy

All external ontologies imported under `third_party/` MUST:

1. **Preserve upstream provenance** — include an `UPSTREAM.md` with the canonical source URL, license, and retrieval metadata.
2. **Preserve upstream licensing** — include the upstream `LICENSE` file verbatim.
3. **Record upstream file digests** — include a manifest (e.g., `IMPORT-MANIFEST.v2.json`) with GitHub blob SHAs and/or cryptographic SHA-256 digests.
4. **Declare a mapping status** for all classes and properties in the mapping ledger.
5. **Not silently overwrite canonical platform semantics** — all conflicts must be declared explicitly.

Stage payloads (large binary or compressed files) remain deferred until vendoring, validation, and query strategy are approved by maintainers.

---

## Documentation standards

- Write in plain, direct English.
- Use Markdown for all documentation.
- Prefer tables over bullet lists for structured comparisons.
- Every new directory under `docs/` should have a `README.md` or be documented in the docs index (`docs/README.md`).
- New schemas should include a `description` field for every property.
- Avoid proprietary product branding and vendor-specific naming in open-spec documents.

---

## Commit message conventions

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <short summary>
```

Common types used in this repository:

| Type | Use for |
|---|---|
| `feat` | New profile content, schemas, or mappings |
| `fix` | Corrections to existing content |
| `docs` | Documentation-only changes |
| `chore` | Maintenance tasks (MANIFEST, CI, tooling) |
| `adr` | Adding or superseding an ADR |
| `import` | New or updated third-party seed import |
| `refactor` | Restructuring without functional change |

Example:
```
feat(mappings): adopt IBM GLO State as operational state

Map State to observed operational state per ADR 0001 decision on external
seed boundary. Added rationale note for scope limitation.
```
