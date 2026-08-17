#!/usr/bin/env python3
"""Run local handoff validation, secret scanning, packaging, and ZIP checks.

By default, suspected sensitive data fails the workflow before a ZIP is made.
With --mask-sensitive, text files are copied to a temporary staging directory,
matched values are replaced there, and only the masked copy is packaged. The
source repository is never modified by this script.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SENSITIVE_PATTERNS = (
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I)),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("OpenAI-style key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("bearer token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}\b", re.I)),
    ("credential assignment", re.compile(r"\b(api[_-]?key|access[_-]?token|secret[_-]?key|client[_-]?secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{12,}['\"]?", re.I)),
)


def find_file(root: Path, candidates: tuple[str, ...]) -> Path | None:
    for relative in candidates:
        candidate = root / relative
        if candidate.exists():
            return candidate
    return None


def run(command: list[str], cwd: Path) -> None:
    print("$ " + " ".join(command))
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def iter_text_files(root: Path, excluded: set[Path]):
    for path in root.rglob("*"):
        if not path.is_file() or path.resolve() in excluded:
            continue
        try:
            data = path.read_bytes()
        except OSError:
            continue
        if b"\x00" in data:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        yield path, text


def scan_sensitive(root: Path, excluded: set[Path]) -> list[tuple[Path, int, str]]:
    findings: list[tuple[Path, int, str]] = []
    for path, text in iter_text_files(root, excluded):
        for label, pattern in SENSITIVE_PATTERNS:
            for match in pattern.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                findings.append((path.relative_to(root), line, label))
    return findings


def mask_sensitive(root: Path, excluded: set[Path]) -> int:
    replacements = 0
    for path, text in list(iter_text_files(root, excluded)):
        masked = text
        for label, pattern in SENSITIVE_PATTERNS:
            placeholder = f"[REDACTED_{label.upper().replace(' ', '_')}]"
            masked, count = pattern.subn(placeholder, masked)
            replacements += count
        if masked != text:
            path.write_text(masked, encoding="utf-8")
    return replacements


def build_zip(repository: Path, output: Path) -> None:
    output = output.resolve()
    root_name = repository.name
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in repository.rglob("*"):
            if not path.is_file() or path.resolve() == output:
                continue
            archive.write(path, Path(root_name) / path.relative_to(repository))


def report_findings(findings: list[tuple[Path, int, str]]) -> None:
    for path, line, label in findings:
        print(f"- {path}:{line}: {label}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, required=True, help="Handoff repository directory")
    parser.add_argument("--output", type=Path, help="ZIP output path; defaults to <repository>.zip")
    parser.add_argument("--skip-tests", action="store_true", help="Skip regression tests (not recommended)")
    parser.add_argument("--mask-sensitive", action="store_true", help="Mask detected text secrets in a temporary copy before packaging")
    args = parser.parse_args()

    repository = args.repository.resolve()
    if not repository.is_dir():
        print(f"ERROR: repository directory does not exist: {repository}", file=sys.stderr)
        return 2

    output = (args.output or repository.with_suffix(".zip")).resolve()
    excluded = {output}
    findings = scan_sensitive(repository, excluded)
    if findings and not args.mask_sensitive:
        print("SENSITIVE DATA DETECTED; no ZIP was generated:", file=sys.stderr)
        report_findings(findings)
        print("Review or redact the source. Use --mask-sensitive only when automatic replacement is appropriate.", file=sys.stderr)
        return 1

    validator = find_file(repository, ("scripts/validate_handoff_zip.py", "06-skills/universal-agent-handoff/scripts/validate_handoff_zip.py"))
    if validator is None:
        print("ERROR: could not locate validate_handoff_zip.py", file=sys.stderr)
        return 2
    tests_dir = find_file(repository, ("tests", "06-skills/universal-agent-handoff/tests"))

    staging_parent: Path | None = None
    working_repository = repository
    try:
        if findings and args.mask_sensitive:
            staging_parent = Path(tempfile.mkdtemp(prefix="handoff-mask-"))
            working_repository = staging_parent / repository.name
            shutil.copytree(repository, working_repository)
            masked = mask_sensitive(working_repository, {output})
            remaining = scan_sensitive(working_repository, {output})
            if remaining:
                print("SENSITIVE DATA REMAINS AFTER MASKING; no ZIP was generated:", file=sys.stderr)
                report_findings(remaining)
                return 1
            print(f"Masked {masked} sensitive value(s) in a temporary copy; source repository was not modified.")

        working_validator = find_file(working_repository, ("scripts/validate_handoff_zip.py", "06-skills/universal-agent-handoff/scripts/validate_handoff_zip.py"))
        working_tests = find_file(working_repository, ("tests", "06-skills/universal-agent-handoff/tests"))
        if not args.skip_tests and working_tests is not None:
            run([sys.executable, "-m", "unittest", "discover", "-s", str(working_tests), "-p", "test_*.py", "-v"], working_repository)
        elif not args.skip_tests:
            print("No test directory found; continuing with structural validation.")

        run([sys.executable, str(working_validator), str(working_repository)], working_repository)
        output.parent.mkdir(parents=True, exist_ok=True)
        if output.exists():
            output.unlink()
        build_zip(working_repository, output)
        run([sys.executable, str(working_validator), str(output)], working_repository)
        with zipfile.ZipFile(output) as archive:
            bad_member = archive.testzip()
        if bad_member:
            print(f"ERROR: ZIP integrity check failed at {bad_member}", file=sys.stderr)
            return 1
        print(f"HANDOFF VALIDATION COMPLETE: {output}")
        return 0
    except (OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if staging_parent is not None:
            shutil.rmtree(staging_parent, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
