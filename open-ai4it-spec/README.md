# Open AI4IT Contracts & Modules (rewrite)

This repo skeleton is an **open-source re-specification** of an AI-for-IT event pipeline and entity-extraction system.
We preserve the functional ideas (topic ladder, message envelope, mapping-driven extraction) while removing vendor coupling.

## What is contractually stable (must not drift)
- Event Envelope: `contracts/schemas/event-envelope.schema.json`
- Entity Extraction Output keys: `contracts/schemas/entity-output.schema.json`
- Mapping DSL schema: `modules/openentitymap/mapping.schema.json`
- Topic taxonomy + release profiles: `contracts/topics/topics.yaml`

## Modules (independently replaceable)
- source_adapters/: ingest vendor data -> emit raw topics
- normalizers/: raw -> normalized
- openentitymap/: mapping-driven entity extraction for alerts/incidents/logs
- template_miner/: propose templates + mapping skeletons from corpora
- story_services/: grouping, story localization, incident similarity, topology/blast radius

## Time conventions
- Prefer `<descriptor>_utc_timestamp` for domain timestamps; add numeric `timestamp` only when the platform requires it (event bus ordering).
