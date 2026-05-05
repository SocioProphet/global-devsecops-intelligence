from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_github_footprint_itops_projection_is_current() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "generate_github_footprint_itops_projection.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "OK: generated GitHub footprint ITOPS projection is current" in result.stdout


def test_github_footprint_itops_validator_passes() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_github_footprint_itops.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "OK: validated GitHub footprint ITOPS" in result.stdout
