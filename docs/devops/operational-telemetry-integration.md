# Operational Telemetry Integration

## Goal
Land telemetry as a governed DevSecOps intelligence fabric rather than as disconnected logs.

## Integration rules
1. Every state-changing platform operation SHOULD emit a durable fact event.
2. Every high-severity failure MUST emit:
   - a telemetry signal,
   - a policy/audit record where relevant,
   - a correlation reference to evidence artifacts.
3. CI/CD, policy, evidence, and runtime telemetry MUST join on shared correlation context.
4. Operational learning loops MUST consume only normalized signals, not raw transport-specific records.

## Sources
This profile expects ingestion from:
- platform runtime telemetry,
- build pipelines,
- release automation,
- policy engines,
- software supply-chain scanners,
- evidence-native assessment services,
- service desk and incident systems.

## Control objectives
- Detect release-path fractures before promotion.
- Preserve causal traceability from runtime symptom to build artifact and policy decision.
- Promote evidence-native operations rather than anecdotal RCA.
- Make recovery actions measurable and reviewable.

## Minimum required joins
The operational intelligence backend SHOULD be able to answer:
- Which build introduced the signal spike?
- Which policy decision blocked or allowed the deployment?
- Which artifact digest and attestation set were active?
- Which cache or query identity failed?
- Which evidence artifact was attached to the resulting ticket or incident?
- Which learning feedback records should update the next control decision?

## Implementation recommendation
- Use OTEL for collection and semantic structure.
- Normalize security outputs from SARIF/CycloneDX/VEX/STIX/TAXII into canonical operational objects.
- Publish durable facts onto topic families aligned with the architecture profile.
- Keep raw adapters separate from the canonical operational graph.
