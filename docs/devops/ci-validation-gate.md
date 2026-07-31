# CI validation gate

This repository treats CI as the executable evidence boundary for the operations-domain profile.

## Required local gate

The expected local gate is:

```bash
make validate
make test
```

## What `make validate` covers

`make validate` currently runs:

- file-inventory (`MANIFEST.txt`) validation;
- service-desk metrics validation;
- model-fabric release-readiness validation;
- generated GitHub-footprint ITOPS projection freshness validation;
- GitHub-footprint ITOPS profile validation;
- client-runtime dump exposure validation;
- operational-exhaust fusion mapping validation.

The GitHub-footprint ITOPS validator checks the profile, generated projection, integration planes, institutional account hierarchy, sample, smoke checks, mapping ledger, source inputs, schema, and IBM GLO profile excerpt.

## What `make test` covers

`make test` runs pytest wrappers under `tools/tests`.

The tests should confirm that each validator can be invoked by the repository-local Python runtime and returns the expected success marker.

## CI rule

The GitHub Actions workflow `.github/workflows/validate.yml` must run both:

```bash
make validate
make test
```

A change is not considered operationally validated until those commands pass in CI or an equivalent locally captured validation transcript is attached to the review evidence.

## Inventory rule

`MANIFEST.txt` is the repository's declared file inventory. It is generated, not hand-maintained: the inclusion rule is every path reported by `git ls-files`, byte-sorted, with no exclusions. `third_party/` is inside the inventory — the external-seed boundary is expressed by ADR 0001 and the upstream import record, not by omitting vendored files from the list.

`tools/validate_manifest.py` enforces the inventory in both directions. It fails when a tracked file is absent from `MANIFEST.txt`, and it fails when `MANIFEST.txt` names a path that is no longer tracked. An absent or empty manifest, a manifest that parses to zero paths, and an unreadable tracked-file list are all failures rather than skips, so the check cannot report success on an empty read.

Regenerate after adding, removing, or renaming files:

```bash
make manifest-write
```

## Freshness rule

The generated GitHub-footprint ITOPS projection must match `tools/generate_github_footprint_itops_projection.py` and the pinned `source_inputs/` snapshots. If CI reports the projection as stale, regenerate it with:

```bash
python3 tools/generate_github_footprint_itops_projection.py --write
```

## Current limitation

This repository still uses lightweight token-based validation for parts of the generated projection. The target state is structured JSON/YAML/RDF validation with explicit dependency policy.
