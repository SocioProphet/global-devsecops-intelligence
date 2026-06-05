# Preproduction Release Traceability Matrix v0.1

## Status

Status: draft traceability matrix.

Related doctrine: `docs/devops/preproduction-release-doctrine.md`.

## Purpose

This matrix maps preproduction release doctrine requirements into operational evidence, enforcement primitives, repository ownership, and graph-query targets.

| Control | Control objective | Required evidence | Enforcement primitive | Owning ops-domain repo | Runtime owner | Failure mode | Graph query target |
|---|---|---|---|---|---|---|---|
| PRC-001 | Every non-trivial release change has a ChangeRecord. | Linked PRs, issues, commits, release tag, rollback plan, impact, target environment, readiness criteria. | CI release checklist, PR template, release workflow validation. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Deploy or promote without change record. | Changes with artifacts but no ChangeRecord. |
| PRC-002 | Manual approval preserves separation of duties. | Approver identity, approver role, approval timestamp, SoD result, automation/manual mode. | Branch protection, approval workflow, policy engine. | `SocioProphet/global-devsecops-intelligence` | Policy/runtime repo | Self-approval or unauthorized functional identity approval. | Approvals where approver overlaps author/reviewer. |
| PRC-003 | Evidence bundle accounts for required release evidence. | EvidenceBundle ref, log hashes, scans, tests, signatures, deployment logs, validation, baseline ref. | Evidence bundle validator. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Missing or mutable evidence. | Releases with incomplete evidence bundle. |
| PRC-004 | Deployable artifacts are digest-pinned, signed, and provenance-linked. | Artifact digest, signature verification result, SBOM ref, provenance ref, trusted artifact repository ref. | Registry policy, signing verification, admission control. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Unsigned, unverifiable, or unpinned artifact. | Deployments whose artifact lacks signature/SBOM/provenance. |
| PRC-005 | Secrets/certificates are referenced, not embedded. | Secret refs, certificate refs, leak-scan result, no-inline-secret assertion. | Secret scanner, deploy manifest validator, admission control. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Secret material in image, manifest, log, issue, or evidence artifact. | Evidence artifacts or deploy inputs with secret-leak findings. |
| PRC-006 | Vulnerability scans are current and findings are governed. | Scan type, target code/image level, timestamp, result ref, log hash, finding issues, exceptions. | SAST/dependency/container/IaC/DAST scanner gates. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Stale scan, new critical finding, expired exception. | Findings past grace period or releases with stale scan evidence. |
| PRC-007 | Service validation proves deployed artifact readiness. | Test plan, test result, test log hash, post-install validation, failed-test exceptions. | Test workflow, deployment verification, readiness scorecard. | `SocioProphet/global-devsecops-intelligence` | Service/runtime repo | Declared ready without adequate validation. | Services with failed validation but promoted state. |
| PRC-008 | Network/runtime security posture is checked after deployment. | Network-policy check, operational access path check, runtime security tooling check, drift issues. | Drift checker, policy controller, runtime inventory collector. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Policy drift or missing security tooling. | Environments with repeated network/runtime drift. |
| PRC-009 | Baseline manifest is updated after deployment. | Baseline ref, baseline commit, previous baseline, release label, image/artifact digests, external artifact refs. | Baseline emitter, repo commit check, drift detector. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Environment cannot be reconstructed; baseline stale. | Deployments without matching baseline update. |
| PRC-010 | Production promotion uses a trusted artifact path. | Source and target environment, trusted repository ref, promotion actor, artifact digest, signature result, evidence bundle. | Promotion workflow, registry policy, environment protection. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Bypassed promotion path or missing deployable signature. | Production artifacts not promoted through trusted path. |
| PRC-011 | Rollback and emergency paths produce reconciliation evidence. | Trigger, actor, rollback artifact/baseline, emergency business justification, event log, reconciliation issue, final evidence bundle. | Emergency workflow, incident/change reconciliation, governance ledger. | `SocioProphet/global-devsecops-intelligence` | Platform/runtime repo | Emergency or rollback action not reconciled. | Emergency changes without reconciliation issue/evidence. |

## Evidence object mapping

| Evidence object | Ops-domain meaning | Candidate canonical owner after promotion |
|---|---|---|
| `ChangeRecord` | Controlled release-state change. | Platform standards / policy fabric. |
| `DeploymentBOM` | Exact deployable set and dependency/artifact inventory. | Platform standards. |
| `EvidenceBundle` | Immutable release-decision evidence surface. | Platform standards + governance ledger. |
| `BaselineManifest` | Rebuildable deployed-state declaration. | Platform standards + platform runtime. |
| `ReleaseException` | Accepted control/finding gap with owner, mitigation, and deadline. | Policy fabric + governance ledger. |
| `PromotionEvent` | Trusted artifact movement between environments. | Platform runtime + governance ledger. |
| `RollbackEvent` | Reversion to prior artifact/baseline. | Platform runtime + governance ledger. |
| `EmergencyReconciliation` | Post-event evidence and justification for emergency/breakglass path. | Policy fabric + governance ledger. |

## Open implementation backlog

1. Promote stable fields into platform-standard JSON schemas.
2. Add runtime emitters for EvidenceBundle and BaselineManifest.
3. Wire promotion events into governance ledger.
4. Add Sociosphere graph nodes for controls, evidence objects, artifacts, environments, owners, and dependencies.
5. Add Hellgraph queries for missing evidence, stale scans, unsigned artifacts, baseline drift, and unreconciled emergency changes.
