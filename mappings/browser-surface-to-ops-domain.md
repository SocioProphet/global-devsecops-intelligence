# Browser surface to operations-domain mapping

Status: draft v0.1

This mapping ledger binds browser telemetry and privacy-risk observations to the operations-domain profile. It is a classification and evidence-routing map, not an authorization to expand browser collection.

## Mapping table

| Browser/runtime observation | Ops-domain class | Confidence default | Notes |
|---|---|---|---|
| Performance entry support observation | `capability` | `observed` when call or warning is present | Treat as a browser-support bit. |
| Media preference observation | `preference` | `observed` when query or warning is present | Treat user/OS preference exposure as privacy-relevant. |
| Experimental CSS parse warning | `parser_compatibility` | `observed` | Do not classify as behavioral coupling without query or telemetry bridge. |
| First-party delivery path success | `delivery_path` | `observed` | Record endpoint class, not raw payload, unless evidence policy permits. |
| External collector limited or unavailable | `policy_outcome` | `observed` | May support reachability matrix. |
| CSP delivery-path limit | `policy_outcome` | `observed` | Preserve policy directive and origin reference. |
| Runtime metadata intake | `metadata_intake` | `observed` when source code or server record exists | Separate from feature/preference collection. |
| Payload changes after support/reachability result | `confirmed_behavioral_coupling` | `observed` only with stack, replay, or differential payload | Requires stronger evidence than console warnings. |

## Finding split rule

If a browser trace and an upstream repository both contain relevant evidence, create separate linked findings unless the same runtime, bundle, or call stack connects them.

Example split:

1. Browser trace finding: capability/preference surface plus delivery-path reachability.
2. Upstream architecture finding: browser metadata intake plus evented evidence routing.

These may be related. They are not the same emitter attribution without a causal bridge.

## Repository placement

- `global-devsecops-intelligence`: operations-domain classes, profile, mapping, examples.
- `prophet-platform`: runtime contract, eval fixture, API/query integration.
- `agentplane`: controlled replay and evidence bundle.
- public web/intake repos: transparency and minimization updates only.

## Overclassification guardrails

Do not classify compatibility warnings as confirmed behavioral coupling.

Do not classify collector or delivery-path limits as intentional fallback logic without retry, payload, stack, or replay evidence.

Do not attribute a browser trace to an upstream repo solely because the repo has a related telemetry or evidence architecture.

Do retain suspicious but unproven chains as `causality_status: unproven` so follow-up replay can settle them.
