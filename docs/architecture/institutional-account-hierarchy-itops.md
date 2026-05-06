# Institutional account hierarchy in the ITOPS projection

## Purpose

This document defines how `global-devsecops-intelligence` represents institutional organization, cloud-folder, cloud-project, and environment-classification state inside the operations-domain projection.

This is an operations-domain projection, not the canonical platform ontology. Canonical ontology mechanics remain upstream in `ontogenesis`; this repository owns the operational view, findings, mappings, and validation surfaces needed for DevSecOps / AIOps / IT operations intelligence.

## Current source input

The current seed lives at:

- `source_inputs/institutional-account/account-hierarchy.v0.json`

The current generated projection emits this source under:

- `examples/github-footprint-itops-generated.yaml` → `institutional_account_hierarchy`

The current seed is manually derived from observed cloud-resource hierarchy and conversation context. It is not yet a live GCP/Firebase export.

## Modeled entities

### InstitutionalOrganization

Represents the top-level institutional account boundary, currently seeded as `socioprophet.ai`.

Required fields:

- `id`
- `kind`
- `provider`
- `display_name`
- `canonical_twin_id`

### CloudFolder

Represents cloud folder hierarchy. The initial seed includes:

- `production`
- `shared`

Required fields:

- `id`
- `kind`
- `provider`
- `display_name`
- `parent`
- `canonical_twin_id`

### CloudProject

Represents provider project / account containers that can bind to repositories, public surfaces, runtime systems, or deployment lanes.

Required fields:

- `id`
- `kind`
- `provider`
- `display_name`
- `parent`
- `declared_environment`
- `structural_environment`
- `workload_role`
- `canonical_twin_id`
- `linked_repositories`
- `linked_surfaces`

## Findings

The projection currently emits two seed findings:

| Finding | Meaning |
|---|---|
| `EnvironmentClassificationConflict` | Project naming or declared environment conflicts with structural placement. |
| `LiveCloudExportPending` | The account hierarchy is still a manual seed and needs live provider export before authoritative drift reporting. |

The current concrete environment conflict is:

- subject: `socioprophet-web`
- declared environment: `development`
- structural environment: `production_shared`

## Pending live bindings

The following bindings are deliberately listed as pending until live collection exists:

- `iam_policy_bindings`
- `service_accounts`
- `billing_accounts`
- `dns_zones`
- `dns_records`
- `certificates`
- `log_sinks`
- `monitoring_scopes`
- `firebase_projects`
- `public_endpoints`

These are required before the system can claim authoritative operational drift reporting.

## Query obligations

The account hierarchy projection should eventually answer:

1. Which cloud projects are production, shared, development, or conflicted?
2. Which project display names conflict with folder-derived structural environment?
3. Which repositories deploy into or control each cloud project?
4. Which public website surfaces map to each cloud project?
5. Which cloud projects lack IAM, logging, monitoring, DNS, certificate, or endpoint evidence?
6. Which account hierarchy findings are warnings versus authoritative drift?

## Validation obligations

Validation must fail if:

- the institutional account source input is missing;
- the generated projection omits `institutional_account_hierarchy`;
- `socioprophet.ai` is missing as the institutional organization;
- no `CloudProject` is present;
- the `EnvironmentClassificationConflict` finding is dropped;
- the pending live-binding list is removed before a replacement live-export mechanism exists.

## Promotion path

The expected maturity path is:

1. manual seed — current state;
2. live provider export snapshot;
3. deterministic normalized account projection;
4. drift findings with evidence references;
5. policy-gated remediation recommendations;
6. integration with incident/story grouping and operational-exhaust fusion.
