#!/usr/bin/env python3
"""Validate the ResourceContract / Measurement telemetry ingestion profile.

This is the first-real-consumer check for sourceos-spec's Measurement + ResourceContract. It
does two things a token-count validator does not:

  1. It INDEPENDENTLY recomputes the SufficiencyVerdict from the worked example's raw inputs
     (observed peak vs limit, fired_count, gate-eligibility, enforcement mode) and asserts the
     example's stated verdict matches. A validator that only checked the verdict STRING is
     present would pass a mislabeled example — the exact "declared, never checked" defect this
     whole plane exists to catch. So the verdict is derived here, not read.

  2. It MUTATION-TESTS that derivation across all four verdict-relevant input axes, so the rule
     is proven to DISCRIMINATE rather than rubber-stamp. `tools/tests/test_resource_contract_
     verdict.py` pins the same algebra in the pytest suite (`make test`) so a regression is
     caught even if this example file changes.

The mapping is checked with ANCHORED regex over COMMENT-STRIPPED lines, not bare substring
presence. That distinction is the point of this file: a required object, rule, or topic that is
deleted from the mapping's structure but still mentioned in prose or a comment must NOT pass —
otherwise the validator is satisfiable by its own documentation, which is the paper-control
shape it exists to reject. (Substring matching, and a docstring that claimed `re` while using
neither, were both flagged on this file's first review — fixed here.)

Dependency-light on purpose: `re` + stdlib `json`, no pyyaml.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "mappings" / "resource-contract-measurement-telemetry-v1.yaml"
EXAMPLE = ROOT / "examples" / "resource-contract-telemetry.example.json"
DOC = ROOT / "docs" / "devops" / "resource-contract-telemetry.md"

REQUIRED_FILES = [MAPPING, EXAMPLE, DOC]

# Anchored, structural patterns — each must match a real YAML key / list-item at line start
# (after comments are stripped), never merely appear in prose. This is what makes the check
# resistant to "removed from structure, still named in a comment" regressions.
REQUIRED_STRUCTURAL_PATTERNS = [
    r"^profile:\s*resource-contract-measurement-telemetry\b",
    r"^\s*TelemetrySignal:\s*$",
    r"^\s*EvidenceArtifact:\s*$",
    r"^\s*SufficiencyVerdict:\s*$",
    r"^\s*signal_class:\s*resource-saturation\b",
    r"^\s*-\s*measurement_gate_eligible\b",
    # the three verdicts as KEYS under `verdicts:`, not as words in a sentence
    r"^\s*PROVED:",
    r"^\s*VIOLATION:",
    r"^\s*INCONCLUSIVE:",
    # the five normalization rules, by id
    r"^\s*-\s*id:\s*carry_gate_eligibility_unrecomputed\b",
    r"^\s*-\s*id:\s*never_fired_control_is_a_violation\b",
    r"^\s*-\s*id:\s*observe_mode_exceedance_is_inconclusive_not_violation\b",
    r"^\s*-\s*id:\s*unmeasured_peak_is_inconclusive_not_healthy\b",
    r"^\s*-\s*id:\s*acting_enforcement_requires_resolvable_negative_control\b",
    r"^\s*-\s*id:\s*preserve_scope_against_fanout\b",
    # the three ops topics, as mapping keys
    r"^\s*ops\.telemetry\.signals\.v1:",
    r"^\s*ops\.evidence\.artifacts\.v1:",
    r"^\s*ops\.learning\.feedback\.v1:",
]


def _strip_yaml_comments(text: str) -> str:
    """Drop `#` comments so structural checks cannot be satisfied by commentary.

    The mapping carries no `#` inside quoted values, so cutting each line at its first `#` is
    sufficient and keeps this dependency-light (no YAML parser). Full-line comments become empty
    lines; inline comments (e.g. `- measurement_gate_eligible # carried through`) lose the tail.
    """
    out = []
    for line in text.splitlines():
        h = line.find("#")
        out.append(line if h < 0 else line[:h])
    return "\n".join(out)


def expected_verdict(*, peak_value, limit_value, fired_count, gate_eligible, enforcement):
    """The verdict algebra, reimplemented independently of the mapping prose and the example.

    Precedence, and why each step is where it is:

      1. not gate-eligible  -> INCONCLUSIVE. An unmeasured or partially-observed peak cannot
         certify anything, so no verdict on the control can be drawn. This wins first.

      2. enforcement != "observe" AND fired_count > 0  -> PROVED. A control that CLAIMS teeth
         (throttle/refuse/terminate) and was observed to act on real load.

      3. enforcement != "observe" AND peak > limit AND fired_count == 0  -> VIOLATION. A control
         that CLAIMED teeth, was exceeded, and never once bit — a counterexample to the claim
         that it is a control. The `enforcement != "observe"` guard is load-bearing: VIOLATION
         is a BROKEN ENFORCEMENT PROMISE, and `observe` mode makes no such promise. It is the
         honest, declared "I am a gauge, not a gate" (ResourceContract requires an
         `observeOnlyReason` for it). Flagging an observe-mode exceedance as VIOLATION would
         accuse a gauge of failing to be a gate, punish honest declaration, and train the
         learning loop to demand fixes for things explicitly declared not-controls. The
         exceedance is NOT hidden by this — it still flows as a resource-saturation
         TelemetrySignal regardless of verdict; only the teeth-verdict is withheld.

      4. otherwise -> INCONCLUSIVE. The limit held, or the contract is observe-mode: no
         counterexample and no teeth proven. No news is not proof of teeth.
    """
    if not gate_eligible:
        return "INCONCLUSIVE"
    if enforcement != "observe" and fired_count > 0:
        return "PROVED"
    if enforcement != "observe" and peak_value > limit_value and fired_count == 0:
        return "VIOLATION"
    return "INCONCLUSIVE"


def main() -> int:
    failures: list[str] = []
    checks = 0

    # ── files ───────────────────────────────────────────────────────────────────
    for f in REQUIRED_FILES:
        checks += 1
        if not f.is_file():
            failures.append(f"missing required file: {f.relative_to(ROOT)}")
    if failures:
        for m in failures:
            print(f"  {m}", file=sys.stderr)
        return 1

    # ── mapping STRUCTURE (anchored, comment-stripped) ──────────────────────────
    mapping_body = _strip_yaml_comments(MAPPING.read_text(encoding="utf-8"))
    for pat in REQUIRED_STRUCTURAL_PATTERNS:
        checks += 1
        if not re.search(pat, mapping_body, re.MULTILINE):
            failures.append(f"mapping missing required STRUCTURE (anchored): {pat!r}")
    print(f"  {'OK  ' if not failures else 'FAIL'} mapping declares "
          f"{len(REQUIRED_STRUCTURAL_PATTERNS)} required structural elements "
          "(anchored keys/list-items over comment-stripped lines, not prose)")

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
            f"fired={rc['firedCount']} gateEligible={peak['gateEligible']} "
            f"enforcement={rc['enforcement']!r}"
        )
        print(f"    FAIL example verdict mislabeled: stated {stated}, derived {got}")
    else:
        print(f"    OK   example verdict {stated} is what its own inputs derive "
              f"(enforcement {rc['enforcement']}, peak {peak['value']} > "
              f"limit {rc['limit']['value']}, fired {rc['firedCount']})")

    checks += 1
    if stated != "VIOLATION":
        failures.append(
            "the shipped example must demonstrate the never-fired-control VIOLATION — that is "
            f"the load-bearing case; it currently demonstrates {stated}"
        )
    else:
        print("    OK   shipped example exercises the load-bearing VIOLATION row")

    # ── mutation test across ALL FOUR axes, incl. the observe-mode carve-out ────
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
        ("enforcement -> observe, same exceedance (gauge, not gate)",
         {**base, "enforcement": "observe"}, "INCONCLUSIVE"),
    ]
    for label, kw, want in mutations:
        checks += 1
        got_m = expected_verdict(**kw)
        if got_m != want:
            failures.append(f"mutation {label}: expected {want}, derived {got_m}")
        else:
            print(f"    OK   {label} -> {want}")

    if failures:
        print(f"\n{len(failures)} failure(s) of {checks} checks:", file=sys.stderr)
        for m in failures:
            print(f"  {m}", file=sys.stderr)
        return 1

    print(f"\nOK resource-contract-measurement-telemetry: {checks} checks. The mapping's "
          "structure is anchored (not satisfiable by prose), and the worked example's VIOLATION "
          "verdict is derived from its own inputs and mutation-tested to discriminate PROVED / "
          "VIOLATION / INCONCLUSIVE, including the observe-mode carve-out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
