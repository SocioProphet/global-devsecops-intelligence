# Client Runtime Dump Exposure Finding v0.1

## Status

Status: draft finding family.

Related standard: `SocioProphet/socioprophet-standards-knowledge#61` / `docs/standards/052-client-runtime-object-dump-forensics.md`.

## Purpose

`ClientRuntimeDumpExposure` captures a DevSecOps intelligence pattern where a browser console capture, developer-tools object expansion, support paste, screenshot, issue comment, model prompt, telemetry event, or notebook cell exposes sensitive client runtime state.

The triggering application event may be harmless, but the copied runtime graph can leak identity, authentication-adjacent values, page state, route identifiers, build metadata, telemetry session IDs, and framework internals.

## Finding family

Finding family: `ClientRuntimeDumpExposure`

Primary risk: secret and identity exposure through over-broad diagnostic artifacts.

Secondary risk: false root-cause analysis from treating a cyclic browser/runtime graph as a normal application payload.

## Sensitive field classes

GDI detection and review workflows SHOULD flag the following classes:

- `cookie:` fields and semicolon-delimited cookie material;
- authentication and session markers such as `auth`, `session`, `token`, `sid`, `client-auth-info`, `puid`, and `did`;
- display names, relay email addresses, account email addresses, avatar URLs, and user identifiers;
- private page URLs, route IDs, object IDs, conversation IDs, tenant IDs, and workspace IDs;
- client telemetry IDs, RUM IDs, trace IDs, source-map paths, build IDs, sequence IDs, and generated bundle identifiers;
- live DOM object dumps, `Window`, `Document`, native `Event`, and DOM element objects logged by reference;
- framework internal containers and cyclic runtime graph fields such as `__reactContainer`, `alternate`, `stateNode`, `containerInfo`, and `memoizedState`.

## Severity guidance

Severity is assigned by exposed data class, not by the original client-side error.

| Severity | Condition |
|---|---|
| High | Cookies, session tokens, auth metadata, or credential-equivalent material appear in raw or redistributed artifacts. |
| Medium | Account identifiers, relay emails, private page/conversation/tenant route IDs, telemetry IDs, or build IDs appear without cookies. |
| Low | The artifact is redacted and only structural runtime graph metadata remains. |
| Informational | Synthetic fixture or documentation-only example with no real user/client values. |

A decorative image or favicon failure is not itself a security incident. It becomes security-relevant when the diagnostic artifact leaks sensitive state or crosses a trust boundary before redaction.

## Expected evidence boundaries

Evidence artifacts MUST NOT include real cookies, real account metadata, real private URLs, or real client session identifiers.

Acceptable evidence includes:

- synthetic unsafe fixture with fake secret-looking markers;
- redacted safe fixture preserving structure and field classes;
- bounded summary record;
- source-card or image-loader failure class without live native event object payload;
- redaction transform metadata.

## Recommended controls

1. Quarantine raw runtime dumps before indexing or publication.
2. Redact before pasting into issues, PRs, support tickets, model prompts, notebooks, or telemetry streams.
3. Reject raw `cookie:`, `client-auth-info`, session IDs, email addresses, and private route IDs in public evidence artifacts.
4. Prefer bounded diagnostic records over raw native `Event`, `Window`, `Document`, or DOM element objects.
5. Capture root-cause stacks at assignment, logger, and network boundaries rather than expanding live objects recursively.
6. Preserve only redacted structural shape for knowledge indexing.

## Detection notes

A simple first-line detector can operate as a lexical guard over diagnostic text. It should flag high-signal tokens and then require redaction review. It does not need to prove exploitability.

Recommended first-line patterns:

```text
cookie:
client-auth-info
session
sid=
token
_puid
oai-
__reactContainer
ownerDocument
containerInfo
memoizedState
Window https://
HTMLDocument https://
```

Pattern lists SHOULD be tuned per ingestion surface to avoid blocking legitimate source code references. Public evidence and issue/comment bodies should be stricter than private quarantined evidence stores.

## Knowledge/operations mapping

This finding family maps to the operations-domain profile as:

- `EvidenceArtifact` when a dump or redacted sample enters the evidence plane;
- `WorkflowState` when the artifact is quarantined, redacted, reviewed, approved, or rejected;
- `OperationalService` when tied to support, telemetry, incident review, or CI evidence ingestion;
- `SecurityControl` when implemented as a pre-ingestion redaction gate;
- `ProvenanceRecord` when recording redaction transforms and lineage.

## Acceptance criteria for implementation

- `ClientRuntimeDumpExposure` profile exists.
- Safe synthetic example exists.
- Smoke checks describe high/medium/low severity expectations.
- Validator rejects missing profile/example/smoke artifacts and required sensitive-field vocabulary omissions.
- No real cookie, relay email, account ID, private route, or real client telemetry value is committed.

## Non-goals

- Do not store real browser dumps in this repo.
- Do not create a proprietary telemetry dependency.
- Do not diagnose a third-party product bug as a SocioProphet runtime defect without source evidence.
- Do not overfit the detector to a single browser or JavaScript framework.
