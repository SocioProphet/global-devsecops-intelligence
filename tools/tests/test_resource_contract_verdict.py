"""Teeth tests for the ResourceContract/Measurement verdict algebra.

The verdict function `expected_verdict` in tools/validate_resource_contract_telemetry.py is the
correctness core of the whole profile — it decides PROVED / VIOLATION / INCONCLUSIVE, which is
what sociosphere's learning loop consumes. On first review that function shipped with a real
precedence bug: an observe-mode contract that exceeded its limit was returned as VIOLATION, which
accuses a declared gauge of failing to be a gate. It went unnoticed because the algebra was only
exercised indirectly by the validator script's own example, never in the pytest suite.

These tests pin every precedence branch in `make test`, so a regression is caught even if the
worked example file changes. Each case names the input axis it isolates.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_resource_contract_telemetry.py"


def _load():
    spec = importlib.util.spec_from_file_location("rc_telemetry_validator", VALIDATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


expected_verdict = _load().expected_verdict


# A gate-eligible, exceeded, never-fired throttle contract — the canonical VIOLATION.
BASE = dict(
    peak_value=0.94, limit_value=0.5, fired_count=0, gate_eligible=True, enforcement="throttle",
)


def test_canonical_violation():
    """A throttle that was exceeded and never fired is a broken enforcement promise."""
    assert expected_verdict(**BASE) == "VIOLATION"


def test_gate_ineligible_wins_first():
    """An unmeasured/partial peak cannot certify anything — INCONCLUSIVE outranks everything,
    even an apparent exceedance."""
    assert expected_verdict(**{**BASE, "gate_eligible": False}) == "INCONCLUSIVE"


def test_enforcement_acted_is_proved():
    """A control that claimed teeth and was observed to fire on real load."""
    assert expected_verdict(**{**BASE, "fired_count": 3}) == "PROVED"


def test_within_limit_is_inconclusive():
    """No exceedance, nothing fired: no counterexample and no teeth proven. No news is not
    proof of teeth."""
    assert expected_verdict(**{**BASE, "peak_value": 0.10}) == "INCONCLUSIVE"


def test_observe_mode_exceedance_is_inconclusive_not_violation():
    """The bug this module exists to pin. An observe-mode contract makes NO enforcement promise,
    so an exceedance cannot violate one. It must be INCONCLUSIVE, never VIOLATION."""
    assert expected_verdict(**{**BASE, "enforcement": "observe"}) == "INCONCLUSIVE"


def test_observe_mode_never_proves_teeth():
    """Even if an observe-mode contract shows fired_count > 0 (it should not, but defensively),
    observe mode cannot PROVE enforcement teeth — it isn't an enforcing mode."""
    assert expected_verdict(**{**BASE, "enforcement": "observe", "fired_count": 5}) != "PROVED"


@pytest.mark.parametrize("mode", ["throttle", "refuse", "terminate"])
def test_all_enforcing_modes_violate_when_exceeded_and_unfired(mode):
    """The VIOLATION rule applies to every mode that claims teeth, not just throttle."""
    assert expected_verdict(**{**BASE, "enforcement": mode}) == "VIOLATION"


def test_verdict_is_always_one_of_three():
    """The algebra is total: every input shape yields exactly one of the three verdicts."""
    verdicts = {
        expected_verdict(
            peak_value=p, limit_value=0.5, fired_count=f, gate_eligible=g, enforcement=e
        )
        for p in (0.10, 0.94)
        for f in (0, 3)
        for g in (True, False)
        for e in ("observe", "throttle", "refuse", "terminate")
    }
    assert verdicts <= {"PROVED", "VIOLATION", "INCONCLUSIVE"}
