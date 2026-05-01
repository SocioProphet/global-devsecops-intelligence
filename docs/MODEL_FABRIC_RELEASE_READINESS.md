# Model Fabric Release Readiness Scorecard

This scorecard records release-readiness evidence for the model-fabric toolchain.

It is not a production certification. A readiness score is an operational signal for promotion review only.

## Covered tools

- `model-router`
- `guardrail-fabric`
- `model-governance-ledger`
- `agent-registry`
- `prophet-cli`
- `homebrew-prophet`

## Scored dimensions

Each scored dimension contributes `0.125` to the readiness score:

- release dry-run present;
- release dry-run workflow present;
- Homebrew development formula present;
- stable release artifact present;
- SHA-256 present;
- SBOM present;
- provenance present;
- formula test present.

The scorecard intentionally separates partial readiness from certification. Stable release readiness remains blocked until immutable release artifacts, SBOM, provenance, SHA-256, and formula test evidence exist.

## Policy relationship

The scorecard is evaluated against Policy Fabric release promotion rules. Policy Fabric owns the promotion rules; Global DevSecOps Intelligence owns operational readiness tracking and reporting.

## Local validation

```bash
make validate
python3 -m pytest -q tools/tests
```
