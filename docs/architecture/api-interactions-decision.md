# API interactions decision (open rewrite)

This document rewrites the “Decisions: API Interactions” design note into an open, modular contract.
It defines how services query artifacts and how they command updates while preserving the event-stream-first model.

## Problem

Artifacts are published to event-stream topics when created/updated.
However, services also need:
- point queries (retrieve a specific artifact version or story slice),
- set queries (retrieve sets in a time window),
- command-like updates/feedback (apply feedback, request recomputation).

## Options considered

### Option A: all interaction via owning microservice
Call the owning service for GET/UPDATE; it proxies to the datastore.
Pros: clean ownership; extensible service APIs.
Cons: duplicated GET APIs and extra hop overhead for reads.

### Option B: GET via datastore API; updates via owning microservice (selected)
Reads go through a shared datastore/query API (single retrieval surface).
Updates go through the owning service (command surface), which writes to datastore, emits an event, and requestors read the result from the datastore.
Short-running ops not associated with a story may return directly.

## Open-source contract (we adopt Option B)

We implement a CQRS-like separation:
- Query Plane: stable datastore/query API for retrieving any artifact version/slice.
- Command Plane: per-artifact owning services that accept mutation requests and emit change events.

### Query plane requirements
- Artifact identity + versioning: (artifact_type, artifact_id, version)
- Story indices: story_id -> artifact_ids
- Time indices: utc_timestamp windows
- Multi-tenant filtering (if applicable): tenant_id

### Command plane requirements
- Idempotent mutation semantics where possible
- Every accepted mutation emits an event describing new/updated artifact availability
- Mutations associate to story_id when applicable

### Why this matters
This prevents read-path proxying, reduces API drift, and preserves service ownership for mutations while keeping the event-stream as the authoritative change log.
