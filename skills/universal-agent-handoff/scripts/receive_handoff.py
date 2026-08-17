#!/usr/bin/env python3
"""Safely unpack and verify a received handoff ZIP.

The original ZIP is never modified. Extraction is staged and only promoted to
--output after archive safety and repository validation succeed.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path


def fail(message: str) -> int:
    print(f"RECEIVING HANDOFF NOT ACCEPTED: {message}", file=sys.stderr)
    print("Preserve the original ZIP and request a corrected handoff or clarification.", file=sys.stderr)
    return 1


def safe_members(archive: zipfile.ZipFile) -> tuple[list[str], str | None]:
    members = archive.namelist()
    roots = {Path(name).parts[0] for name in members if Path(name).parts}
    if len(roots) != 1:
        return members, f"expected exactly one top-level directory, found {sorted(roots)}"
    for name in members:
        path = Path(name)
        if path.is_absolute() or ".." in path.parts:
            return members, f"unsafe path in archive member: {name}"
    try:
        bad_member = archive.testzip()
    except (OSError, zipfile.BadZipFile) as exc:
        return members, f"archive integrity check could not complete: {exc}"
    if bad_member is not None:
        return members, f"CRC or compressed-data integrity check failed at {bad_member}"
    return members, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path, help="Received handoff ZIP")
    parser.add_argument("--output", type=Path, required=True, help="New directory for the verified repository")
    args = parser.parse_args()

    zip_path = args.zip_path.resolve()
    output = args.output.resolve()
    if not zip_path.is_file():
        return fail(f"ZIP file does not exist: {zip_path}")
    if output.exists():
        return fail(f"output directory already exists; refusing to overwrite: {output}")

    try:
        archive = zipfile.ZipFile(zip_path)
    except (OSError, zipfile.BadZipFile) as exc:
        return fail(f"archive cannot be opened as a valid ZIP: {exc}")

    with archive:
        try:
            _, error = safe_members(archive)
        except (OSError, zipfile.BadZipFile) as exc:
            return fail(f"archive safety check failed: {exc}")
        if error:
            return fail(error)
        parent = output.parent
        parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{output.name}.staging-", dir=parent))
        try:
            try:
                archive.extractall(staging)
            except (OSError, zipfile.BadZipFile) as exc:
                return fail(f"extraction failed: {exc}")
            roots = [item for item in staging.iterdir() if item.is_dir()]
            if len(roots) != 1:
                return fail(f"extraction produced {len(roots)} top-level directories; expected one")
            repository = roots[0]
            validator = repository / "06-skills/universal-agent-handoff/scripts/validate_handoff_zip.py"
            if not validator.is_file():
                return fail("required packaged validator is missing after extraction")
            completed = subprocess.run([sys.executable, str(validator), str(repository)], cwd=repository)
            if completed.returncode != 0:
                return fail("repository validation failed after extraction")
            repository.rename(output)
            print(f"RECEIVING HANDOFF ACCEPTED: {output}")
            print("Next: read MANIFEST.md, current status, project rules, decisions, checklist, and HANDOFF_PROMPT.md.")
            return 0
        finally:
            if staging.exists():
                shutil.rmtree(staging, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
