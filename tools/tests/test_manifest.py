from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "tools" / "validate_manifest.py"

# Keep fixture repositories independent of any ambient git configuration so the
# tracked-file list under test is exactly what the fixture stages.
GIT_ENV = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull}


def run_validator(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(repo / "tools" / "validate_manifest.py"), *args],
        cwd=repo,
        text=True,
        capture_output=True,
        check=False,
        env=GIT_ENV,
    )


def git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, env=GIT_ENV)


def make_fixture_repo(tmp_path: Path) -> Path:
    """Build a throwaway git repository carrying a copy of the validator.

    The validator resolves its own root from ``__file__``, so a copy under
    ``<fixture>/tools/`` validates the fixture rather than this repository. The
    teeth below can then be exercised for real without mutating the tree.
    """
    repo = tmp_path / "fixture"
    (repo / "tools").mkdir(parents=True)
    shutil.copy2(VALIDATOR, repo / "tools" / "validate_manifest.py")
    (repo / "docs").mkdir()
    (repo / "docs" / "note.md").write_text("note\n", encoding="utf-8")
    (repo / "kept.md").write_text("kept\n", encoding="utf-8")
    (repo / "MANIFEST.txt").write_text("", encoding="utf-8")
    git(repo, "init", "-q")
    git(repo, "add", "-A")
    git(repo, "-c", "user.email=fixture@example.invalid", "-c", "user.name=fixture", "commit", "-q", "-m", "fixture")
    assert run_validator(repo, "--write").returncode == 0
    return repo


def manifest_of(repo: Path) -> Path:
    return repo / "MANIFEST.txt"


def test_repository_manifest_matches_tracked_tree() -> None:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr + result.stdout
    assert "OK: validated MANIFEST.txt" in result.stdout


def test_fixture_repo_validates_clean(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    result = run_validator(repo)
    assert result.returncode == 0, result.stderr + result.stdout
    assert "OK: validated MANIFEST.txt" in result.stdout


def test_tracked_file_missing_from_manifest_fails(tmp_path: Path) -> None:
    """Tooth 1: a file lands in the tree and nobody updates the manifest."""
    repo = make_fixture_repo(tmp_path)
    (repo / "docs" / "added.md").write_text("added\n", encoding="utf-8")
    git(repo, "add", "docs/added.md")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "missing 1 tracked file(s)" in result.stderr
    assert "docs/added.md" in result.stderr
    assert "OK:" not in result.stdout


def test_manifest_entry_for_deleted_file_fails(tmp_path: Path) -> None:
    """Tooth 2: the manifest keeps naming a path the tree no longer has."""
    repo = make_fixture_repo(tmp_path)
    git(repo, "rm", "-q", "docs/note.md")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "no longer tracked" in result.stderr
    assert "docs/note.md" in result.stderr
    assert "OK:" not in result.stdout


def test_invented_manifest_entry_fails(tmp_path: Path) -> None:
    """Tooth 2, other shape: a path that was never tracked at all."""
    repo = make_fixture_repo(tmp_path)
    manifest = manifest_of(repo)
    manifest.write_text(manifest.read_text(encoding="utf-8") + "zz-never-existed.md\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "no longer tracked" in result.stderr
    assert "zz-never-existed.md" in result.stderr


def test_absent_manifest_fails(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest_of(repo).unlink()

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "missing MANIFEST.txt" in result.stderr


def test_empty_manifest_fails(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest_of(repo).write_text("", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "is empty" in result.stderr


def test_header_only_manifest_fails(tmp_path: Path) -> None:
    """A manifest that parses to zero paths must not read as 'nothing to check'."""
    repo = make_fixture_repo(tmp_path)
    manifest = manifest_of(repo)
    header = [line for line in manifest.read_text(encoding="utf-8").splitlines() if line.startswith("#")]
    manifest.write_text("\n".join(header) + "\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "lists no files" in result.stderr


def test_manifest_without_inclusion_rule_fails(tmp_path: Path) -> None:
    """The declared rule is part of the record and cannot be silently dropped."""
    repo = make_fixture_repo(tmp_path)
    manifest = manifest_of(repo)
    stripped = [
        line
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if not line.startswith("# inclusion rule:")
    ]
    manifest.write_text("\n".join(stripped) + "\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "no longer declares its inclusion rule" in result.stderr


def test_unsorted_manifest_fails(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest = manifest_of(repo)
    lines = manifest.read_text(encoding="utf-8").splitlines()
    paths = [line for line in lines if line and not line.startswith("#")]
    comments = [line for line in lines if not line or line.startswith("#")]
    manifest.write_text("\n".join(comments + list(reversed(paths))) + "\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "not byte-sorted" in result.stderr


def test_unreadable_tracked_list_fails(tmp_path: Path) -> None:
    """No git metadata means no tracked-file list, which is a failure, not a skip."""
    repo = make_fixture_repo(tmp_path)
    shutil.rmtree(repo / ".git")

    result = run_validator(repo)
    assert result.returncode == 1, result.stdout + result.stderr
    assert "could not list tracked files" in result.stderr
    assert "OK:" not in result.stdout
