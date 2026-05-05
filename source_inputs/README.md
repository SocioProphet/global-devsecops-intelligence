# Source input snapshots

This directory contains pinned, reviewable source extracts used by local validators and generators.

The intent is not to replace the upstream sources. The intent is to make `global-devsecops-intelligence` validation deterministic without requiring CI to read other repositories or public websites at runtime.

## Current inputs

- `sociosphere/repository-map.v0.json` — curated extract from `SocioProphet/sociosphere` repository registry, role ontology, dependency graph, and canonical-source map.
- `ontogenesis/module-map.v0.json` — curated extract from `SocioProphet/ontogenesis` module/lifecycle surface.

## Refresh rule

When upstream `sociosphere` or `ontogenesis` changes materially, update these snapshots and regenerate derived examples with:

```bash
python3 tools/generate_github_footprint_itops_projection.py --write
make validate
```

These snapshots are evidence inputs, not canonical sources. Canonical source ownership remains with the upstream repositories named in each snapshot.
