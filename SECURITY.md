# Security Policy

## Scope

This repository contains operations-domain profiles, mappings, examples, validators, and third-party seed metadata. It should not contain secrets, credentials, private incident data, customer data, trading credentials, or sensitive infrastructure details.

## Reporting

Do not open a public issue for security-sensitive matters. Report security concerns through the maintainer security channel for the SocioProphet organization.

## Handling expectations

Security-sensitive reports should include:

- affected file or artifact path,
- observed risk,
- reproduction steps when safe,
- suggested remediation when known,
- whether any secret or private data may have been exposed.

## Repository hygiene

- Keep examples synthetic.
- Use references, hashes, or receipts instead of raw sensitive payloads.
- Preserve third-party license and provenance material for vendored seed content.
- Keep validation surfaces deterministic and reviewable.
