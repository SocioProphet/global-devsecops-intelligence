# Open AI4IT Contracts & Modules (rewrite)

This repo skeleton captures the AI4IT operations-domain profile of an AI-for-IT event pipeline and entity-extraction system.
It preserves the functional ideas relevant to this repository (topic ladder, ops extraction, mapping-driven specialization) while avoiding vendor coupling.

Canonical platform storage, transport, and interface invariants are owned upstream by `socioprophet-standards-storage`.
Canonical ontology and knowledge semantics are owned upstream by `ontogenesis` and `socioprophet-standards-knowledge`.

Within this repository, the operations-domain profile that should remain aligned includes:
- Entity Extraction Output keys: `contracts/schemas/entity-output.schema.json`
- Mapping DSL schema: `modules/openentitymap/mapping.schema.json`
- Topic taxonomy + release profiles: `contracts/topics/topics.yaml`

The local event envelope material here is a repository copy/example for integration work, not the canonical ownership source.

## Modules (independently replaceable)
- source_adapters/: ingest vendor data -> emit raw topics
- normalizers/: raw -> normalized
- openentitymap/: mapping-driven entity extraction for alerts/incidents/logs
- template_miner/: propose templates + mapping skeletons from corpora
- story_services/: grouping, story localization, incident similarity, topology/blast radius

## Time conventions
- Prefer `<descriptor>_utc_timestamp` for domain timestamps; add numeric `timestamp` only when the platform requires it (event bus ordering).
