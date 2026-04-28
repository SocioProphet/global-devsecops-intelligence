# Agentic Service Desk Metrics

Global DevSecOps Intelligence aggregates delivery, execution, and quality metrics for agentic product-suite work.

## Role

Agentplane records per-run timing and evidence.

Global DevSecOps Intelligence aggregates timing, CI, validation, risk, rework, and merge-readiness metrics across repositories and agents.

SocioSphere rolls the aggregate into program/workstream dashboards.

Policy Fabric defines the required fields and merge gates.

Alexandrian Academy converts failures, latency patterns, and rework into lessons, eval cases, and retraining material.

## Core metrics

Each service-desk metric record should capture:

- time to first action
- time to first PR
- time to merge
- time to close
- turns to completion
- wall-clock execution time
- CI duration
- validation duration
- retry count
- rework count
- failure count
- blocked duration
- handoff count
- evidence completeness score
- scope compliance status
- merge gate status
- agent kind

## Data handling

Raw prompts, stdout, stderr, artifacts, and private data should be referenced by evidence refs unless explicitly safe to inline.

The first implementation pass defines deterministic examples and validation only. It does not claim live metrics collection.
