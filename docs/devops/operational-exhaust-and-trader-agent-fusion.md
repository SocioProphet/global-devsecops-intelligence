# Operational Exhaust and Trader-Agent Fusion

## Purpose

This document defines the first operations-domain fusion model for platform telemetry, operational event exhaust, and trader-agent operational telemetry.

The goal is not to relocate canonical platform or market semantics into this repository.
The goal is to define how those upstream signals are projected into one ops-domain intelligence surface for:
- correlation,
- incident grouping,
- feedback loops,
- measurement,
- policy review,
- replay alignment,
- and operational learning.

## Why this needs to exist

Today, operational exhaust is produced across multiple planes:
- CI and delivery pipelines,
- runtime services and agent surfaces,
- policy/evidence and authorization lanes,
- market-data ingestion and replay lanes,
- trader-agent execution and learning loops.

If these are captured independently, the result is a fragmented observability posture.
We instead want one governed operational fusion surface.

## Authority split

- canonical storage, wire, and interface invariants remain upstream in `socioprophet-standards-storage`
- canonical ontology and broader knowledge semantics remain upstream in `ontogenesis` and `socioprophet-standards-knowledge`
- runtime and domain repositories continue to own domain-native event semantics
- `global-devsecops-intelligence` owns the **ops-domain projection**, mapping, grouping, and derived operational graph surfaces

## Fusion lanes

### 1. CI / delivery lane
Examples:
- build started / finished
- test suite started / finished
- deployment requested / applied / rolled back
- dependency risk detection
- provenance and attestation publication

### 2. Runtime / service / agent lane
Examples:
- service health
- queue pressure
- saturation and shed posture
- route or dependency degradation
- agent lifecycle transitions
- capability or tool availability changes

### 3. Policy / evidence lane
Examples:
- policy decision emitted
- authorization denied
- grant or delegation activated
- attestation verified / failed
- replay receipt emitted
- evidence bundle sealed

### 4. Market-data operations lane
Examples:
- feed connected / degraded / disconnected
- gap detected
- late or out-of-order observations detected
- replay requested / completed
- calendar or symbol-map version changes
- corporate-action restatement activity

### 5. Trader-agent execution lane
Examples:
- strategy run started / stopped
- model version selected
- feature snapshot pinned
- order intent created
- broker or venue acknowledgement
- fill / reject / cancel
- kill-switch or risk control activation
- execution-quality measurement and slippage evaluation

### 6. Trader-agent learning lane
Examples:
- post-trade evaluation completed
- replay/backtest parity result emitted
- policy violation review generated
- strategy promotion / demotion recommendation
- operator override or escalation

## Common required projection fields

Every projected operational event SHOULD carry:
- `event_id`
- `observed_at`
- `source_repo`
- `source_surface`
- `source_runtime`
- `environment_ref`
- `actor_ref` or `agent_ref`
- `trace_ref`
- `story_ref` when applicable
- `policy_ref` when applicable
- `evidence_ref` or `artifact_ref`
- `severity` or `operational_band`
- `projection_family`

## Trader-agent-specific projection fields

Trader-agent operational events SHOULD also carry, where applicable:
- `strategy_run_ref`
- `model_ref`
- `feature_snapshot_ref`
- `market_window_ref`
- `risk_policy_ref`
- `order_intent_ref`
- `execution_ref`
- `venue_ref`
- `portfolio_scope_ref`
- `replay_ref`
- `post_trade_evaluation_ref`

## Export and retention rules

- Raw sensitive payloads SHOULD remain in their canonical stores and be referenced here by artifact handles, hashes, or receipts.
- This repository SHOULD store projection-ready artifacts, mappings, and intelligence views, not become the canonical store for all source payloads.
- Derived operational graph projections may join CI/CD, runtime, policy/evidence, market-data, and trader-agent signals into one incident or learning story.

## External influence note

A relevant upstream influence for the security-automation side is Ge Chu / Alexei Lisitsa-style ontology- and BDI-agent-based automation of penetration testing.
This is relevant here as an **ops-domain seed influence** for automation, reasoning, and operational planning.
It does not alter the canonical ontology ownership boundary.

## Immediate next uses

- unify DevSecOps / AIOps telemetry with agent-plane telemetry
- provide a stable fusion grammar for trader-agent operational exhaust
- support cross-plane incident grouping
- support replay-aware operational learning
- support evidence-oriented audit and policy review
