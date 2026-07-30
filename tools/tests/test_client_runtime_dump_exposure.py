"""Teeth tests for the ClientRuntimeDumpExposure synthetic-only guard.

The guard in tools/validate_client_runtime_dump_exposure.py shipped with
double-escaped patterns (``\\\\.`` and ``[^\\\\s]``), which require a literal
backslash inside an email address or URL. It therefore matched nothing while
still printing ``OK: ... synthetic-only guard``.

These tests pin the guard in both directions:
  * known positives are matched and are refused end to end;
  * the committed synthetic example pack still passes.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_client_runtime_dump_exposure.py"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "client-runtime-dump-exposure"
POSITIVES = FIXTURES / "forbidden-positives.txt"
ALLOWED = FIXTURES / "allowed-synthetic.txt"


def _fixture_lines(path: Path) -> list[str]:
    lines = [
        line
        for raw in path.read_text(encoding="utf-8").splitlines()
        for line in [raw.strip()]
        if line and not line.startswith("#")
    ]
    assert lines, f"fixture {path} yielded no cases"
    return lines


def _load_validator():
    spec = importlib.util.spec_from_file_location(
        "validate_client_runtime_dump_exposure", VALIDATOR
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATOR_MODULE = _load_validator()


def test_validator_passes_on_committed_artifacts() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "synthetic-only guard" in result.stdout


def test_forbidden_regexes_are_not_double_escaped() -> None:
    """A doubled backslash disarms the guard silently. Fail loudly instead."""
    for regex in VALIDATOR_MODULE.FORBIDDEN_REGEXES:
        assert "\\\\" not in regex.pattern, (
            "double-escaped pattern requires a literal backslash in the candidate "
            f"value and can never match: {regex.pattern!r}"
        )


@pytest.mark.parametrize("line", _fixture_lines(POSITIVES))
def test_known_positives_are_matched(line: str) -> None:
    hits = [
        match.group(0)
        for regex in VALIDATOR_MODULE.FORBIDDEN_REGEXES
        for match in regex.finditer(line)
    ]
    assert hits, f"guard did not match known positive: {line!r}"


@pytest.mark.parametrize("line", _fixture_lines(ALLOWED))
def test_allowed_synthetic_lines_are_not_matched(line: str) -> None:
    hits = [
        match.group(0)
        for regex in VALIDATOR_MODULE.FORBIDDEN_REGEXES
        for match in regex.finditer(line)
    ]
    assert not hits, f"guard flagged a legitimate synthetic line {line!r}: {hits}"


def test_reject_forbidden_accepts_the_committed_example_pack() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            VALIDATOR_MODULE.DOC,
            VALIDATOR_MODULE.PROFILE,
            VALIDATOR_MODULE.SAMPLE,
            VALIDATOR_MODULE.SMOKE,
        )
    )
    VALIDATOR_MODULE.reject_forbidden("committed example pack", combined)


def _mirror_artifact_tree(destination: Path) -> Path:
    """Copy the validator and the four artifacts it reads into a scratch tree.

    The validator resolves its inputs from ``__file__``, so a mirrored tree lets
    a test poison an artifact without touching the working copy.
    """
    for source in (
        VALIDATOR,
        VALIDATOR_MODULE.DOC,
        VALIDATOR_MODULE.PROFILE,
        VALIDATOR_MODULE.SAMPLE,
        VALIDATOR_MODULE.SMOKE,
    ):
        target = destination / source.relative_to(ROOT)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return destination / VALIDATOR.relative_to(ROOT)


def _run_mirrored(validator_copy: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(validator_copy)],
        cwd=validator_copy.parents[1],
        text=True,
        capture_output=True,
        check=False,
    )


def test_mirrored_tree_passes_before_poisoning(tmp_path: Path) -> None:
    """Control for the poisoning test: the mirror itself must be clean."""
    result = _run_mirrored(_mirror_artifact_tree(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("line", _fixture_lines(POSITIVES))
def test_validator_refuses_poisoned_artifact(line: str, tmp_path: Path) -> None:
    validator_copy = _mirror_artifact_tree(tmp_path)
    sample_copy = tmp_path / VALIDATOR_MODULE.SAMPLE.relative_to(ROOT)
    sample_copy.write_text(
        sample_copy.read_text(encoding="utf-8") + f"{line}\n", encoding="utf-8"
    )

    result = _run_mirrored(validator_copy)
    assert result.returncode != 0, (
        f"validator accepted a poisoned artifact containing {line!r}\n"
        + result.stdout
        + result.stderr
    )
    assert "forbidden non-synthetic diagnostic tokens" in result.stderr
    assert "synthetic-only guard" not in result.stdout
