# Documentation index

This directory contains the operations-domain profile documentation for `global-devsecops-intelligence`.

## Architecture

- [`architecture/api-interactions-decision.md`](architecture/api-interactions-decision.md) — CQRS-style query/command interaction model.
- [`architecture/github-footprint-itops-alignment.md`](architecture/github-footprint-itops-alignment.md) — GitHub footprint, website surface, IBM ITOPS, and ontogenesis alignment model.

## ADRs

- [`adr/0001-ops-domain-profile-and-external-seed-boundary.md`](adr/0001-ops-domain-profile-and-external-seed-boundary.md) — repository ownership boundary and external seed policy.
- [`adr/0002-operational-exhaust-and-trader-agent-fusion-boundary.md`](adr/0002-operational-exhaust-and-trader-agent-fusion-boundary.md) — operational exhaust and trader-agent fusion boundary.

## DevOps / operations

- [`devops/devops-process-open.md`](devops/devops-process-open.md) — open DevOps process baseline.
- [`devops/operational-exhaust-and-trader-agent-fusion.md`](devops/operational-exhaust-and-trader-agent-fusion.md) — platform, agent, market-data, and trader-agent operational exhaust fusion model.

## Vision

- [`vision/ai4it-home-rewrite.md`](vision/ai4it-home-rewrite.md) — AI4IT / AIOps capability statement.

## Related profile artifacts

- [`../profiles/github-footprint-itops-expansion.yaml`](../profiles/github-footprint-itops-expansion.yaml)
- [`../profiles/operational-exhaust-fusion-profile.v0.yaml`](../profiles/operational-exhaust-fusion-profile.v0.yaml)
- [`../mappings/ibm-itops-glo-to-ops-domain.md`](../mappings/ibm-itops-glo-to-ops-domain.md)
- [`../examples/github-footprint-itops-sample.yaml`](../examples/github-footprint-itops-sample.yaml)
- [`../examples/github-footprint-itops-generated.yaml`](../examples/github-footprint-itops-generated.yaml)
- [`../source_inputs/README.md`](../source_inputs/README.md)
- [`../source_inputs/sociosphere/repository-map.v0.json`](../source_inputs/sociosphere/repository-map.v0.json)
- [`../source_inputs/ontogenesis/module-map.v0.json`](../source_inputs/ontogenesis/module-map.v0.json)

## Generator and validation entrypoints

- [`../tools/generate_github_footprint_itops_projection.py`](../tools/generate_github_footprint_itops_projection.py) — deterministic projection generator from pinned source inputs.
- [`../tools/validate_github_footprint_itops.py`](../tools/validate_github_footprint_itops.py) — local validation for the profile, generated projection, sample, smoke checks, mapping ledger, source inputs, and IBM GLO excerpt.
