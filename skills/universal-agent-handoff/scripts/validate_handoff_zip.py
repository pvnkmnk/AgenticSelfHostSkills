#!/usr/bin/env python3
"""Validate a universal-agent-handoff repository directory or ZIP archive.

Exit status 0 means all required files and structural checks passed.
"""

from __future__ import annotations

import argparse
import re
import sys
import zipfile
from pathlib import Path

REQUIRED_FILES = (
    "HANDOFF_PROMPT.md",
    "MANIFEST.md",
    "01-context/project-brief.md",
    "02-status/current-status.md",
    "03-decisions/decision-log.md",
    "04-rules/project-rules.md",
    "05-workflows/bespoke-workflows.md",
    "08-operations/operational-notes.md",
    "06-skills/universal-agent-handoff/SKILL.md",
    "06-skills/universal-agent-handoff/scripts/validate_handoff_zip.py",
    "06-skills/universal-agent-handoff/scripts/run_handoff_validation.py",
    "06-skills/universal-agent-handoff/scripts/receive_handoff.py",
    "06-skills/universal-agent-handoff/references/validation-wrapper-guide.md",
    "06-skills/universal-agent-handoff/references/handoff-schema.md",
    "06-skills/universal-agent-handoff/templates/handoff-prompt.md",
    "06-skills/universal-agent-handoff/templates/handoff-repository-structure.md",
    "06-skills/universal-agent-handoff/templates/incomplete-tasks-open-decisions-checklist.md",
    "06-skills/universal-agent-handoff/templates/domain-customization-guide.md",
    "06-skills/universal-agent-handoff/templates/validate-handoff-ci.yml",
    "06-skills/universal-agent-handoff/templates/receiving-agent-quick-start-checklist.md",
    "06-skills/universal-agent-handoff/templates/receiving-agent-startup-task-list.md",
    "06-skills/universal-agent-handoff/references/fresh-manus-workspace-install-and-test.md",
    "06-skills/universal-agent-handoff/tests/test_validate_handoff_zip.py",
    "06-skills/universal-agent-handoff/tests/test_run_handoff_validation.py",
    "06-skills/universal-agent-handoff/tests/test_secret_masking_patterns.py",
    "06-skills/universal-agent-handoff/references/two-manus-instances-walkthrough.md",
)

SECRET_PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I),
    re.compile(r"(?:api[_-]?key|access[_-]?token|secret[_-]?key|password)\s*[:=]\s*['\"]?[^\s'\"]{12,}", re.I),
)


def normalize_member(name: str) -> str:
    """Remove the single archive root directory from a ZIP member path."""
    parts = Path(name).parts
    return "/".join(parts[1:]) if len(parts) > 1 else ""


def validate_zip(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        archive = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as exc:
        return [f"Not a valid ZIP archive: {exc}"]
    with archive:
        members = archive.namelist()
        files = {normalize_member(name) for name in members if not name.endswith("/")}
        roots = {Path(name).parts[0] for name in members if Path(name).parts}
        if len(roots) != 1:
            errors.append(f"ZIP must contain exactly one top-level directory; found {sorted(roots)}")
        if any(".." in Path(name).parts for name in members):
            errors.append("ZIP contains a path traversal member")
        missing = [item for item in REQUIRED_FILES if item not in files]
        if missing:
            errors.append("Missing required files: " + ", ".join(missing))
        for name in members:
            if name.endswith("/"):
                continue
            try:
                text = archive.read(name).decode("utf-8")
            except UnicodeDecodeError:
                continue
            if any(pattern.search(text) for pattern in SECRET_PATTERNS):
                errors.append(f"Possible secret-like content found in {name}")
    return errors


def validate_directory(path: Path) -> list[str]:
    errors: list[str] = []
    files = {item.relative_to(path).as_posix() for item in path.rglob("*") if item.is_file()}
    missing = [item for item in REQUIRED_FILES if item not in files]
    if missing:
        errors.append("Missing required files: " + ", ".join(missing))
    for item in path.rglob("*"):
        if not item.is_file():
            continue
        try:
            text = item.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            errors.append(f"Possible secret-like content found in {item.relative_to(path)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path, help="Handoff repository directory or ZIP archive")
    args = parser.parse_args()
    if not args.package.exists():
        print(f"ERROR: package does not exist: {args.package}", file=sys.stderr)
        return 2
    errors = validate_zip(args.package) if args.package.suffix.lower() == ".zip" else validate_directory(args.package)
    if errors:
        print("HANDOFF VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"HANDOFF VALIDATION PASSED: {args.package}")
    print(f"Checked {len(REQUIRED_FILES)} required files and archive safety rules.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
