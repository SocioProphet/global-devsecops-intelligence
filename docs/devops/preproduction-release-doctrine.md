# Preproduction Release Doctrine v0.1

## Status

Status: draft ops-domain doctrine.

Related ADR: `docs/adr/0003-preproduction-release-doctrine-boundary.md`.

## Purpose

This doctrine translates preproduction test-and-deploy controls into an open, vendor-neutral, evidence-oriented DevSecOps release-governance model.

The goal is not to make `global-devsecops-intelligence` the deployment runtime. The goal is to define the operational-intelligence projection that lets SocioProphet reason over release readiness, evidence completeness, policy drift, exception debt, rollback patterns, and promotion risk.

## Authority split

- `global-devsecops-intelligence` owns this ops-domain doctrine, traceability, profile, topics, mappings, and release-readiness interpretation.
- Platform standards repositories own canonical schema contracts after fields stabilize.
- Platform/runtime repositories own CI/CD jobs, emitters, validators, registry policy, signing integration, admission control, and deployment automation.
- Sociosphere owns repository inventory, ownership topology, dependency graph, and canonical-source namespace alignment.
- Graph/reasoning repositories own release-readiness queries and derived governance views.
- Governance-ledger repositories own tamper-evident release-state transition records.

## Doctrine primitives

### ChangeRecord

A `ChangeRecord` represents a controlled change to code, configuration, runtime topology, worker nodes, deployment manifests, release artifacts, or promotion state.

Required operational fields:

- change identifier;
- change type: `standard`, `emergency`, `breakglass`, or `remediation`;
- affected repositories and services;
- target environment;
- planned start and end window;
- expected outage or degradation duration;
- impact statement;
- rollback plan;
- linked PRs, issues, commits, and release tags;
- deployment readiness criteria;
- evidence bundle reference;
- exception references when gates are not fully satisfied.

### DeploymentBOM

A `DeploymentBOM` identifies what is actually being deployed.

It should include:

- release name and tag;
- tag checksum or release digest;
- application image references;
- base image references;
- artifact digests;
- signatures and signature verification status;
- dependency manifests;
- deploy manifests;
- infrastructure module references;
- runtime node or worker-pool references;
- external artifacts pulled without source modification;
- orphaned commits, meaning commits not tied to tracked work items.

### EvidenceBundle

An `EvidenceBundle` is the immutable evidence surface for a release decision.

It should reference:

- test logs and hashes;
- SAST, dependency, container, IaC, DAST, and dynamic scan results;
- scan log hashes;
- SBOMs;
- provenance attestations;
- artifact signing and verification results;
- deployment logs;
- admission-control results;
- network-policy verification;
- runtime security-tooling verification;
- post-installation validation;
- baseline update commit;
- rollback evidence when rollback occurred;
- open issues, mitigations, and accepted exceptions.

Raw sensitive payloads should stay in canonical stores and be referenced by artifact handles, hashes, or receipts.

### BaselineManifest

A `BaselineManifest` is the rebuild-the-world release state.

It should include:

- environment identifier;
- release label;
- service versions;
- image digests;
- artifact signatures;
- dependency lock state;
- runtime configuration references;
- worker-node or node-pool metadata;
- policy versions;
- network-policy versions;
- external artifact references;
- evidence bundle reference;
- previous baseline reference;
- baseline signature or digest.

### ReleaseException

A `ReleaseException` records a known gap that was not fixed before readiness or promotion.

It must include:

- finding or failed-control reference;
- reason not fixed immediately;
- impact statement;
- mitigation;
- owner;
- deadline or grace period;
- manual approval reference when required;
- linked issue.

Emergency paths do not remove evidence requirements. They defer normal approval only when business continuity or security requires immediate action. Emergency changes must be reconciled with post-event evidence, business justification, and an event log.

## Required control families

### PRC-001 Change governance

Every non-trivial change to release state requires a `ChangeRecord`.

Minimum evidence:

- linked issues, PRs, commits, and release tags;
- rollback plan;
- impact statement;
- target environment;
- owner and approver identity;
- readiness criteria.

Operational intelligence use:

- detect orphaned commits;
- detect direct changes without change records;
- group related work into release stories;
- measure exception debt and approval latency.

### PRC-002 Separation of duties

Manual approval must be separable from the author/reviewer identity when the release requires explicit approval.

Minimum evidence:

- approver identity;
- approver role;
- separation-of-duties result;
- approval timestamp;
- automation/manual approval mode.

Operational intelligence use:

- detect self-approval;
- detect functional or automation identities used outside allowed contexts;
- escalate high-risk emergency approvals.

### PRC-003 Evidence completeness

A release cannot be considered complete unless the evidence bundle accounts for required tests, scans, signatures, deployment logs, validation, and baseline state.

Minimum evidence:

- evidence bundle ref;
- immutable log hashes;
- artifact refs;
- open exceptions;
- validation result.

Operational intelligence use:

- readiness score;
- missing evidence queries;
- recurring evidence-gap analysis.

### PRC-004 Supply-chain integrity

Deployable artifacts should be digest-pinned, signed, and associated with SBOM and provenance evidence.

Minimum evidence:

- artifact digest;
- signature verification result;
- SBOM ref;
- provenance ref;
- trusted artifact repository ref.

Operational intelligence use:

- detect unsigned or unverifiable deployables;
- detect missing SBOM or provenance;
- correlate provenance gaps with rollback or incident patterns.

### PRC-005 Secrets and certificates

Secrets and certificates must be referenced through managed stores and runtime acquisition paths, not embedded in artifacts, logs, manifests, or evidence documents.

Minimum evidence:

- secret reference class;
- certificate reference class;
- scanner result for leaked secret checks;
- deployment path proving no secret material is inline.

Operational intelligence use:

- classify leaked-secret findings;
- block public evidence contamination;
- track secret-handling drift.

### PRC-006 Vulnerability scanning

Security scanning must be current enough for the release decision and must account for new and pre-existing findings.

Minimum evidence:

- scan type;
- scan target and code/image level;
- scan timestamp;
- scan result ref;
- scan log hash;
- open finding issues;
- exception records for accepted findings.

Operational intelligence use:

- detect stale scans;
- detect unresolved findings past grace period;
- cluster recurring vulnerabilities by repo, service, image, and dependency.

### PRC-007 Service validation

Service-specific test and post-installation validation must run for the deployed artifact and environment.

Minimum evidence:

- test plan ref;
- test result ref;
- test log hash;
- deployment verification result;
- failed-test exceptions where applicable.

Operational intelligence use:

- distinguish readiness signal from certification;
- track test escape patterns;
- correlate failed validation with rollback and incident data.

### PRC-008 Network and runtime security posture

Post-deploy checks must verify network policy, access path constraints, runtime hardening, and required security tooling.

Minimum evidence:

- network policy check result;
- bastion or operational access path result when applicable;
- runtime security tooling result;
- drift issues.

Operational intelligence use:

- detect policy drift;
- detect missing security tooling;
- identify release environments with repeated hardening gaps.

### PRC-009 Baseline update

The baseline must be updated after deployment so the environment can be reconstructed and audited.

Minimum evidence:

- baseline manifest ref;
- baseline commit ref;
- previous baseline ref;
- release label;
- image and artifact digests;
- external artifact refs.

Operational intelligence use:

- detect deploys without baseline updates;
- compare actual runtime state with declared baseline;
- drive drift remediation.

### PRC-010 Promotion boundary

Production promotion must occur through a trusted artifact path and produce a promotion event with evidence.

Minimum evidence:

- source environment;
- target environment;
- trusted artifact repository ref;
- promotion actor;
- promoted artifact digest;
- deployable signature verification;
- evidence bundle ref.

Operational intelligence use:

- detect bypassed promotion paths;
- track promotion latency;
- correlate promotion quality with incident outcomes.

### PRC-011 Rollback and emergency reconciliation

Rollback and emergency deployment paths are first-class release states.

Minimum evidence:

- rollback trigger;
- rollback actor;
- rollback artifact or baseline;
- emergency business justification;
- event log;
- reconciliation issue;
- final evidence bundle.

Operational intelligence use:

- detect unreconciled emergency work;
- cluster rollback causes;
- measure rollback readiness.

## Readiness semantics

This doctrine separates readiness from certification.

Readiness is an operational signal based on evidence completeness and control posture. Certification or hard promotion gating belongs to downstream policy repositories and runtime enforcement systems.

Allowed readiness states:

- `blocked`: one or more blocking controls are absent or failed;
- `partial`: evidence exists but required controls are incomplete;
- `ready_for_review`: evidence is complete enough for manual release review;
- `ready_for_promotion`: all profile-level controls are satisfied, subject to downstream policy;
- `emergency_reconcile`: emergency deployment occurred and reconciliation evidence is pending;
- `complete`: release is deployed, validated, baseline-updated, and evidence-linked.

## Operational topics

Initial topic names for release-governance projection:

- `change.record.created`
- `change.record.approved`
- `evidence.bundle.attached`
- `scan.completed`
- `scan.exception.opened`
- `deployment.started`
- `deployment.signature.failed`
- `deployment.rollback.started`
- `deployment.rollback.completed`
- `baseline.updated`
- `promotion.requested`
- `promotion.completed`
- `admission.rejected`
- `policy.drift.detected`
- `security.tooling.absent`
- `breakglass.invoked`
- `breakglass.reconciled`

## Immediate next uses

- build release-readiness scorecards from evidence bundles;
- connect release events to Sociosphere ownership and dependency topology;
- generate Hellgraph queries for missing evidence, stale scans, missing baseline updates, unsigned artifacts, and unreconciled emergency changes;
- promote stable profile fields into platform standards and runtime validators.
