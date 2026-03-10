# global-devsecops-intelligence

## Added in v2: DevOps, API interactions, and Home/vision rewrites

- `docs/vision/ai4it-home-rewrite.md`
- `docs/architecture/api-interactions-decision.md`
- `docs/devops/devops-process-open.md`


## What this is

An AI4IT / Watson-style operational intelligence backend and measurement plane for logs, telemetry, service desk automation, chatops, ticket clustering, reusable evidence artifacts, and operational learning loops.

This repository defines the operations-domain specialization, including:
- AI4IT topic ladder
- ops entity extraction schemas
- mapping DSL
- story grouping
- explainability and feedback loops
- operational measurement plane

This repository does not own platform storage standards or knowledge standards.

Ownership boundaries:
- `socioprophet-standards-storage` owns base transport, storage, and interface invariants, including canonical envelope and wire contracts.
- `ontogenesis` and `socioprophet-standards-knowledge` own ontology and knowledge semantics.
- `global-devsecops-intelligence` owns the operations-domain profile built on those upstream standards.

Dependency direction:
`platform standards -> knowledge / ontology standards -> global-devsecops-intelligence domain profile -> runtime implementations`
