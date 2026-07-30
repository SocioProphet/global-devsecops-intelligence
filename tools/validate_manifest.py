#!/usr/bin/env python3
"""Validate MANIFEST.txt against the repository's tracked file list."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.txt"

# Sentinel line that must remain in the manifest header. The inclusion rule is
# part of the record; it must not be quietly deleted while the list survives.
RULE = "# inclusion rule: every path reported by `git ls-files`, byte-sorted, no exclusions."

HEADER = [
    "# MANIFEST.txt - inventory of every file tracked in this repository.",
    "#",
    "# Generated. Do not hand-edit; regenerate with:",
    "#   make manifest-write     (or: python3 tools/validate_manifest.py --write)",
    "#",
    "# The rule below was inferred from the previously hand-maintained contents of",
    "# this file, then frozen here so it can be enforced rather than merely stated.",
    "#",
    RULE,
    "#",
    "# What that means, and why:",
    "# - No exclusions. `.github/workflows/validate.yml` was already listed, so",
    "#   repository-automation files are in scope and are not filtered out.",
    "# - `third_party/` is IN. All four vendored IBM ITOPS seed files were already",
    "#   listed. The external-seed boundary is expressed by ADR 0001 and by",
    "#   `third_party/ibm-itops/UPSTREAM.md`, not by omitting the files from this",
    "#   inventory: what ships in the tree is what the inventory records.",
    "# - Byte-sorted (`LC_ALL=C sort`), which is also `git ls-files` order. The",
    "#   previous list was byte-sorted apart from one hand-edit that hoisted",
    "#   `docs/README.md` above two adjacent uppercase filenames; that has been",
    "#   normalised so the inventory is reproducible from the tree.",
    "# - Blank lines and lines starting with `#` are comments. Every other line is",
    "#   exactly one repository-relative path.",
    "#",
    "# Enforced by tools/validate_manifest.py via `make validate`, which fails both",
    "# when a tracked file is absent from this list and when this list names a path",
    "# that is no longer tracked.",
    "",
]

MAX_REPORTED = 10


def fail(message: str) -> int:
    print(f"ERROR: {message}", file=sys.stderr)
    return 1


def summarise(paths: list[str]) -> str:
    shown = ", ".join(paths[:MAX_REPORTED])
    extra = len(paths) - MAX_REPORTED
    return f"{shown} (+{extra} more)" if extra > 0 else shown


def tracked_files() -> list[str]:
    """Return the repository's tracked paths, byte-sorted.

    Raises rather than returning an empty list: an unreadable or empty tracked
    tree is a validation failure, never a silent pass.
    """
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit status {result.returncode}"
        raise RuntimeError(f"could not list tracked files with `git ls-files`: {detail}")
    paths = [path for path in result.stdout.split("\0") if path]
    if not paths:
        raise RuntimeError(
            "`git ls-files` reported no tracked files; refusing to validate "
            "MANIFEST.txt against an empty tracked-file list"
        )
    return sorted(paths)


def render(paths: list[str]) -> str:
    return "\n".join(HEADER + paths) + "\n"


def parse(text: str) -> list[str]:
    entries = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate MANIFEST.txt")
    args = parser.parse_args()

    try:
        tracked = tracked_files()
    except RuntimeError as exc:
        return fail(str(exc))

    if args.write:
        MANIFEST.write_text(render(tracked), encoding="utf-8")
        print(f"OK: wrote {MANIFEST.name} with {len(tracked)} tracked files")
        return 0

    if not MANIFEST.exists():
        return fail(f"missing {MANIFEST.name}; regenerate with `make manifest-write`")
    text = MANIFEST.read_text(encoding="utf-8")
    if not text.strip():
        return fail(f"{MANIFEST.name} is empty; regenerate with `make manifest-write`")
    if RULE not in text:
        return fail(
            f"{MANIFEST.name} no longer declares its inclusion rule; the header line "
            f"'{RULE}' must be present"
        )

    entries = parse(text)
    if not entries:
        return fail(
            f"{MANIFEST.name} lists no files; it must record every tracked path, "
            f"and this repository tracks {len(tracked)}"
        )

    problems = []

    duplicates = sorted({entry for entry in entries if entries.count(entry) > 1})
    if duplicates:
        problems.append(
            f"{MANIFEST.name} lists {len(duplicates)} path(s) more than once: {summarise(duplicates)}"
        )

    missing = sorted(set(tracked) - set(entries))
    if missing:
        problems.append(
            f"{MANIFEST.name} is missing {len(missing)} tracked file(s): {summarise(missing)}"
        )

    stale = sorted(set(entries) - set(tracked))
    if stale:
        problems.append(
            f"{MANIFEST.name} lists {len(stale)} path(s) that are no longer tracked: "
            f"{summarise(stale)}"
        )

    if not problems and entries != sorted(entries):
        problems.append(f"{MANIFEST.name} is not byte-sorted")

    if not problems and text != render(tracked):
        problems.append(
            f"{MANIFEST.name} does not match its generated form (header or spacing drift)"
        )

    if problems:
        for problem in problems:
            fail(problem)
        print("hint: regenerate with `make manifest-write`", file=sys.stderr)
        return 1

    print(f"OK: validated {MANIFEST.name} against {len(tracked)} tracked files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
