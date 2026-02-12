# AI4IT / AIOps capability statement (open rewrite)

This document rewrites and generalizes the internal “Home” wiki narrative into an open-source, vendor-neutral specification-level capability statement.
We preserve the functional content (data types, pipeline stages, feedback loops) while removing proprietary product branding and replacing it with modular interfaces.

## Core thesis

AI for IT Operations (“AIOps”) reduces operational pain by turning high-volume, multi-modal operational exhaust (logs, metrics, alerts/events, tickets, topology, deployment config, chat) into:
1) early detection and prediction,
2) noise reduction via correlation/grouping,
3) fault localization + blast radius,
4) action recommendations,
5) closed-loop improvement across DevSecOps.

## Input data types (first-class signals)

Operational environments generate: metrics, alerts/events, logs, tickets, topology, deployment configurations, and chat conversations.
Metrics are typically structured; logs/alerts/events are semi-structured; tickets and chats are largely unstructured.
Logs and metrics can be leading indicators; alerts/tickets/chats are often lagging indicators.

## Event management (required functional surface)

An “event” is any noteworthy change (e.g., service unavailable, disk reaching capacity).
Event management includes collection, classification, normalization, deduplication, enrichment, correlation, and grouping.
The primary goal is operator focus: reduce noise while elevating high-risk/high-impact situations.

Entity-based correlation is a key mechanism: extract mentions of application/infrastructure components, resolve them to topology, and use them to strengthen grouping and diagnosis.

## Diagnosis pipeline (required model/service surfaces)

### Anomaly detection and prediction
- Learn “normal” behavior from logs and metrics; detect deviations without relying solely on static thresholds.
- Produce explainable outputs with back-pointers to evidence (e.g., specific log lines / metric segments).

### Topology + fault localization + blast radius
- Maintain static topology (build/deploy-derived) and dynamic topology (runtime-discovered, time-versioned).
- Resolve extracted entities to topology resources at the incident time.
- Traverse dependency graphs to estimate impacted components (blast radius).

## Resolution assistance (required retrieval + NLP surface)

Ingest prior incident/ticket records; retrieve relevant prior cases (“top-k”).
Extract compact entity-action (“noun-verb”) phrases to support operator decisions.
Regardless of technique (rules, ML, LLM), outputs must include structured provenance for auditability.

## Insight delivery + action execution (required interface surfaces)

Deliver insights both:
- in ChatOps (real-time, in-context), and
- in dashboards (interactive exploration).

Support action execution via runbooks, including automation where safe, and feedback capture for continuous improvement.

## Model lifecycle management (open governance)

Models can be unsupervised and continuously retrained on fresh data.
Administrators must have access to training/retraining scripts and be able to retrain on-demand.
The system must not be a black box: explanations and data provenance are mandatory.

## Shift-left and closed-loop DevSecOps

Use incident outcomes to reinforce earlier lifecycle gates (build/test/security/deploy).
Correlate incidents with root causes such as under-tested changes or known vulnerabilities and feed this back into CI gates and deployment policy.

## Pillars (product decomposition)

- AI for Support
- AI for Proactive Issue Avoidance
- AI for Continuous Compliance
