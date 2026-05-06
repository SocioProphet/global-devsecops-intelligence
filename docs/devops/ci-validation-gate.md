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

- service-desk metrics validation;
- model-fabric release-readiness validation;
- generated GitHub-footprint ITOPS projection freshness validation;
- GitHub-footprint ITOPS profile validation;
- client-runtime dump exposure validation.

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

## Current limitation

This repository still uses lightweight token-based validation for parts of the generated projection. The target state is structured JSON/YAML/RDF validation with explicit dependency policy.
