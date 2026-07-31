#!/usr/bin/env python3
"""Validate the ResourceContract / Measurement telemetry ingestion profile.

This is the first-real-consumer check for sourceos-spec's Measurement + ResourceContract. It
does two things a token-count validator does not:

  1. It INDEPENDENTLY recomputes the SufficiencyVerdict from the worked example's raw inputs
     (observed peak vs limit, fired_count, gate-eligibility) and asserts the example's stated
     verdict matches. A validator that only checked the verdict STRING is present would pass a
     mislabeled example — the exact "declared, never checked" defect this whole plane exists to
     catch. So the verdict is derived here, not read.

  2. It MUTATION-TESTS that derivation: flip fired_count and the verdict must move to PROVED;
     flip the peak's gate-eligibility and it must move to INCONCLUSIVE. If the same verdict came
     back under all three input shapes, the rule would be a rubber stamp and this check would be
     proving nothing.

Dependency-light on purpose: the mapping is token-checked by substring presence (no pyyaml, no
`re`), and the verdict logic runs on the JSON example via stdlib json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "mappings" / "resource-contract-measurement-telemetry-v1.yaml"
EXAMPLE = ROOT / "examples" / "resource-contract-telemetry.example.json"
DOC = ROOT / "docs" / "devops" / "resource-contract-telemetry.md"

REQUIRED_FILES = [MAPPING, EXAMPLE, DOC]

# The mapping must DECLARE these — the canonical objects, the three verdicts, the load-bearing
# normalization rules, and the learning-feedback topic that closes the loop.
REQUIRED_MAPPING_TOKENS = [
    "profile: resource-contract-measurement-telemetry",
    "signal_class: resource-saturation",
    "TelemetrySignal",
    "EvidenceArtifact",
    "SufficiencyVerdict",
    "measurement_gate_eligible",
    "PROVED",
    "VIOLATION",
    "INCONCLUSIVE",
    "never_fired_control_is_a_violation",
    "unmeasured_peak_is_inconclusive_not_healthy",
    "carry_gate_eligibility_unrecomputed",
    "acting_enforcement_requires_resolvable_negative_control",
    "preserve_scope_against_fanout",
    "ops.telemetry.signals.v1",
    "ops.evidence.artifacts.v1",
    "ops.learning.feedback.v1",
]


def expected_verdict(*, peak_value, limit_value, fired_count, gate_eligible, enforcement):
    """The verdict algebra, reimplemented independently of the mapping prose and the example.

    Precedence matters and is deliberate:
      - not gate-eligible wins first: an unmeasured/partial peak cannot certify anything, so no
        verdict on the control can be drawn -> INCONCLUSIVE.
      - then an acting enforcement that has fired -> PROVED: the control was observed to act.
      - then an exceeded limit that never fired -> VIOLATION: the never-fired control. This
        holds in ANY mode, observe included — an observe-mode control must still record the
        breach, so silence when the limit was exceeded is itself the failure being asserted
        (see the mapping rule `never_fired_control_is_a_violation`, which carries no observe
        carve-out either).
      - otherwise (the limit held, or a control that did fire but — being observe-mode — proves
        no teeth) there is no counterexample -> INCONCLUSIVE (no news is not proof of teeth).
    """
    if not gate_eligible:
        return "INCONCLUSIVE"
    if enforcement != "observe" and fired_count > 0:
        return "PROVED"
    if peak_value > limit_value and fired_count == 0:
        return "VIOLATION"
    return "INCONCLUSIVE"


def main() -> int:
    failures: list[str] = []
    checks = 0

    # ── files + mapping tokens ──────────────────────────────────────────────────
    for f in REQUIRED_FILES:
        checks += 1
        if not f.is_file():
            failures.append(f"missing required file: {f.relative_to(ROOT)}")
    if failures:
        for m in failures:
            print(f"  {m}", file=sys.stderr)
        return 1

    mapping_text = MAPPING.read_text(encoding="utf-8")
    for tok in REQUIRED_MAPPING_TOKENS:
        checks += 1
        if tok not in mapping_text:
            failures.append(f"mapping missing required token: {tok!r}")
    print(f"  {'OK  ' if not failures else 'FAIL'} mapping declares "
          f"{len(REQUIRED_MAPPING_TOKENS)} required tokens (objects, verdicts, rules, topics)")

    # ── the teeth: derive the example's verdict and check it matches ────────────
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    rc = example["source_resource_contract"]
    peak = rc["observedPeak"]
    stated = example["normalized"]["SufficiencyVerdict"]["verdict"]

    got = expected_verdict(
        peak_value=peak["value"],
        limit_value=rc["limit"]["value"],
        fired_count=rc["firedCount"],
        gate_eligible=peak["gateEligible"],
        enforcement=rc["enforcement"],
    )
    checks += 1
    if got != stated:
        failures.append(
            f"example's stated verdict {stated!r} does not match the verdict derived from its "
            f"own inputs ({got!r}): peak={peak['value']} limit={rc['limit']['value']} "
            f"fired={rc['firedCount']} gateEligible={peak['gateEligible']}"
        )
        print(f"    FAIL example verdict mislabeled: stated {stated}, derived {got}")
    else:
        print(f"    OK   example verdict {stated} is what its own inputs derive "
              f"(peak {peak['value']} > limit {rc['limit']['value']}, fired {rc['firedCount']})")

    # sanity: the shipped example must actually exercise the load-bearing VIOLATION row, or this
    # profile's whole reason for existing is untested.
    checks += 1
    if stated != "VIOLATION":
        failures.append(
            "the shipped example must demonstrate the never-fired-control VIOLATION — that is "
            f"the load-bearing case; it currently demonstrates {stated}"
        )
    else:
        print("    OK   shipped example exercises the load-bearing VIOLATION row")

    # ── mutation test: the derivation must discriminate, not rubber-stamp ────────
    print("  mutation test — the verdict moves when the inputs move")
    base = dict(
        peak_value=peak["value"], limit_value=rc["limit"]["value"],
        fired_count=rc["firedCount"], gate_eligible=peak["gateEligible"],
        enforcement=rc["enforcement"],
    )
    mutations = [
        ("fired_count -> 3 (enforcement acted)", {**base, "fired_count": 3}, "PROVED"),
        ("gate_eligible -> False (unmeasured peak)", {**base, "gate_eligible": False}, "INCONCLUSIVE"),
        ("peak within limit, never fired", {**base, "peak_value": 0.10}, "INCONCLUSIVE"),
    ]
    for label, kw, want in mutations:
        checks += 1
        got_m = expected_verdict(**kw)
        if got_m != want:
            failures.append(f"mutation {label}: expected {want}, derived {got_m}")
        else:
            print(f"    OK   {label} -> {want}")
    # if every mutation returned VIOLATION we'd never get here clean — that's the rubber-stamp guard

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for m in failures:
            print(f"  {m}", file=sys.stderr)
        return 1

    print(f"\nOK resource-contract-measurement-telemetry: {checks} checks. The mapping declares "
          "the loop (telemetry/evidence/learning topics), and the worked example's VIOLATION "
          "verdict is derived from its own inputs and mutation-tested to discriminate PROVED / "
          "VIOLATION / INCONCLUSIVE.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
