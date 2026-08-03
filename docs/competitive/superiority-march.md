# The Superiority March

> The plan to answer [`where-we-stand.md`](where-we-stand.md): close **every** capability gap, but
> do each one **faster, more secure, more ergonomic, and fully open** than the incumbent — so a gap
> becomes a differentiated win, not parity. Generated register is the scoreboard; this is the march.

## Doctrine (how "we win, and open" is different from "we catch up")

Every incumbent capability we're behind on is either (a) SaaS/closed, (b) advisory not enforced, or
(c) audit-logged but not cryptographically verifiable. Our answer to each is the same shape:

- **Faster** — scale-to-zero, event-driven, deterministic-first (the model is a thin edge, not the gate).
- **More secure** — fail-closed by default; every action pre-gated by policy AND sealed into evidence.
- **More ergonomic** — agent-native (MCP) + one-command golden paths; the platform is drivable by an agent.
- **Fully open** — MIT, self-hosted, our own Gitea/zot/runners; no external SaaS, no lock-in, and
  **standards-based** provenance (cosign/SLSA/in-toto) so trust is externally verifiable, not self-issued.

## The sequenced moves (dependency order; each closes ranked gaps)

| # | Move | Closes (gap register) | Our open edge over the leader | Status |
|---|------|----------------------|-------------------------------|--------|
| 1 | **Governed MCP ops surface** on the control plane | `agent-native-mcp-ops-surface` (#1, 8 ahead) | Qovery/Port gate pre-exec + audit-log (SaaS). We add **fail-closed + hash-sealed receipts on every tool call**, fully open, scale-to-zero. | **executing** |
| 2 | **Wire observability** (Prometheus/Grafana/Loki/Tempo behind the OTel collector) | keystone for #2/chaos/autoscale | Open OTel stack, self-hosted; unblocks metric-gated everything. | next |
| 3 | **Metric-gated progressive delivery** (canary/blue-green + auto-rollback + our sealed promotion gate) | `progressive-delivery-auto-rollback` (#2, 6 ahead) | Argo Rollouts analysis, but **gated by our sealed APPROVE verdict** and evidenced — auto-rollback *and* provenance. | sequenced |
| 4 | **Standards-based attestation** (emit cosign/SLSA/in-toto via our `zot`) alongside receipts | `attestation-provenance-slsa`, and repairs the "self-issued receipts" weakness | **Externally verifiable** provenance (public-log-compatible) + our governed enforcement wrapper on top. | sequenced |
| 5 | **Service mesh** (Istio mTLS + gateway; MeshSpace-style header routing) | mesh net-new (diagrams) | Open Istio, sovereign; enables canary traffic-shifting. | sequenced |
| 6 | **Autonomous fix-and-verify remediation** (re-vendor executor + reviewer → propose+validate fix) | `autonomous-remediation-agents`, `malicious-package-detection` | Endor/Harness fix (SaaS). Ours: sealed, fail-closed, open; add reachability + malicious-package signal to the loop. | sequenced |
| 7 | **Broad-ecosystem dependency intelligence** (reachability + confidence + malicious-package) | `vuln-db-broad-scanning`, `reachability-exploitability`, `broad-ecosystem-dep-automation` | Consume OSS advisory data (OSV) + reachability; keep it sovereign + receipted. | sequenced |
| 8 | **Developer portal + inner-loop dev-environments** (Nocalhost-style DevSpace + web console) | `web-ui-developer-portal`, dev-env diagrams | Open catalog + golden paths over CapD; agent-driven via move #1. | sequenced |
| 9 | **Compliance evidence automation** (map sealed receipts + attestations → SOC2/FedRAMP controls) | `compliance-certifications` | Turn our provenance into audit evidence; open control mappings. | sequenced |

## Meet-or-beat on the reference diagrams

- **Nocalhost DevSpace/MeshSpace, Istio mesh** → moves #5, #8 (we're behind; open Istio + DevSpace).
- **Sovereign Agentic Cloud-Shell, Agent Governance Architecture** → move #1 realizes these; they are *our* design — the march makes them real and shipped.
- **Karpathy wiki pipeline** → already realized: this intelligence suite *is* structured-knowledge + generated projections.
- **prophet-platform readiness (Have/Partial/Net-new)** → observability keystone = move #2; mesh/canary/chaos = moves #3/#5.

## Non-skimp clause

Each move ships the nice-to-haves that make it ergonomic, not just the minimum: MCP tool schemas +
elicitation, one-command golden paths, sealed receipts on every action, and standards-based
attestation — because "more ergonomic and fully open" is the whole point of the march.
