# IBM ITOPS Ontology External Seed

This subtree tracks the metadata-first import of IBM's ITOPS ontology into this repository as an external seed for the operations-domain profile.

## Current local materials

- `IMPORT-MANIFEST.v2.json` is the authoritative import manifest for the IBM seed in this repository.
- `LICENSE.Apache-2.0` preserves the upstream Apache 2.0 license material for the vendored subtree.
- `mappings/ibm-itops-glo-to-ops-domain.md` records the first-pass adopt / map / reject / defer decisions for IBM GLO concepts.

## Preferred first payload

`GLO_V1.ttl` is the preferred first payload for semantic alignment because it provides the upper / bridge ontology used by the staged ITOPS releases.

## Deferred staged payloads

The following staged payloads remain deferred until vendoring, validation, and query strategy are approved:

1. `ITOPS_S1_PUB.ttl.zip`
2. `ITOPS_S2_PUB.ttl.zip`
3. `ITOPS_S3_PUB.ttl.zip`

## Retrieval URLs

- `GLO_V1.ttl`: https://raw.githubusercontent.com/IBM/ITOPS-ontology/master/GLO_V1.ttl
- `ITOPS_S1_PUB.ttl.zip`: https://raw.githubusercontent.com/IBM/ITOPS-ontology/master/ITOPS_S1_PUB.ttl.zip
- `ITOPS_S2_PUB.ttl.zip`: https://raw.githubusercontent.com/IBM/ITOPS-ontology/master/ITOPS_S2_PUB.ttl.zip
- `ITOPS_S3_PUB.ttl.zip`: https://raw.githubusercontent.com/IBM/ITOPS-ontology/master/ITOPS_S3_PUB.ttl.zip

## License

Upstream source: Apache 2.0.
Canonical upstream repository: https://github.com/IBM/ITOPS-ontology
