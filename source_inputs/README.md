# Source input snapshots

This directory contains pinned, reviewable source extracts used by local validators and generators.

The intent is not to replace the upstream sources. The intent is to make `global-devsecops-intelligence` validation deterministic without requiring CI to read other repositories, cloud APIs, or public websites at runtime.

## Current inputs

- `sociosphere/repository-map.v0.json` — curated extract from `SocioProphet/sociosphere` repository registry, role ontology, dependency graph, and canonical-source map.
- `ontogenesis/module-map.v0.json` — curated extract from `SocioProphet/ontogenesis` module/lifecycle surface.
- `integration-planes/ops-integration-map.v0.json` — curated operations-plane map for GAIA World Model, Meshrush, Sherlock, and SCOPED red-teaming.
- `institutional-account/account-hierarchy.v0.json` — manual seed for the `socioprophet.ai` institutional account hierarchy, cloud folders, cloud projects, environment classification findings, and pending live cloud bindings.

## Refresh rule

When upstream `sociosphere`, `ontogenesis`, integration-plane repositories, or institutional account state changes materially, update these snapshots and regenerate derived examples with:

```bash
python3 tools/generate_github_footprint_itops_projection.py --write
make validate
```

These snapshots are evidence inputs, not canonical sources. Canonical source ownership remains with the upstream repositories and provider systems named in each snapshot.

## Important boundary

The institutional-account snapshot is currently a manual seed. It is not a live GCP/Firebase export. Treat its findings as seed findings until a live provider export pipeline exists.
