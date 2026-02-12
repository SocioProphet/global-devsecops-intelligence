# DevOps process (open rewrite)

This document generalizes the DevOps wiki into an open-source set of reproducible practices.
We preserve intent (design review, branching, testing, CI, release artifacts, container constraints, microservice templates), while removing proprietary tool references and replacing them with OSS-equivalent patterns.

## Why DevOps
DevOps exists to ensure high quality code, agile delivery, and reliable artifacts; it also scaffolds collaboration and skill growth.

## End-to-end flow (required gates)
1. Create stories: design stories + implementation stories, decomposed into few-day units.
2. Design: written design + test plan covering security, performance, model lifecycle, documentation, and interlocks.
3. Review design: complexity-dependent; impacted squads participate; approve only when requirements/security/perf commitments are met.
4. Implement: branch from dev; follow coding guidelines.
5. Test: unit + integration + deployment verification + performance + security.
6. Code review: iterative PR review; converge on agreement.
7. Merge to dev: only after CI gates succeed; dev remains releasable.
8. Release: tag; PR dev->main; publish immutable artifacts.

## Git policy (open contract)
- dev is integration; main (or master) is release-only.
- Protect dev/main:
  - require PR reviews
  - require status checks
  - restrict direct pushes
  - enforce for admins
- Prefer squash merge with curated summary commits.

## Testing taxonomy (required)
- Unit: correctness in isolation (mocks/stubs); success and failure modes.
- Integration: end-to-end with real dependencies or realistic doubles.
- DVT: validate installation/readiness after install/upgrade.
- Performance: benchmark small-to-large; ensure lightweight dev/trial footprint + production scalability.
- Security: SAST + dependency scanning + optional DAST; periodic pen tests; developers must triage scan reports.

Suggested default gates:
- 100% tests pass on dev
- >=80% coverage target (exceptions documented)

## Code review checklist
Readability, correctness, no leaked credentials, proper logging, CI green, meaningful tests, security hygiene, performance/resource sizing, and shared understanding.

## CI/CD automation (open equivalent)
Typical pipeline:
- checkout
- build container(s)
- unit tests
- coverage
- lint
- publish build metadata/badges
Optional:
- push images from dev/main
- REST/contract tests
- performance tests
- model quality tests
- chat notifications

## Release artifacts (open constraints)
- Use any OCI registry (e.g., GHCR/Harbor/Quay).
- Prefer minimal/certified base images.
- Enforce rootless runtime: containers run as non-root.
- Provide service templates:
  - Java: standard health/metrics/logging
  - Python: FastAPI-style template + typed schemas + self-documenting endpoints

## Third-party dependency governance
Identify dependencies during design; prefer maintained OSS with compatible licenses; keep third-party code isolated and consume via APIs; scan licenses/deps in CI.
Avoid copying code from random sources without license compliance.
