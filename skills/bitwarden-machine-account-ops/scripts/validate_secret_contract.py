#!/usr/bin/env python3
"""Validate non-secret metadata in a completed Bitwarden contract Markdown file.

This validator is intentionally offline. It never invokes bws, reads environment
variables, calls Bitwarden, or prints a suspect line's contents.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REQUIRED_FIELDS = (
    "Trust boundary",
    "Environment",
    "Project name and ID",
    "Machine account name and ID",
    "Machine-account members/groups reviewed",
    "Consumer host, guest, service, or workflow",
    "Access level",
    "Write-access justification and approval",
    "Required secret keys or IDs",
    "Human owner and recovery owner",
    "Token expiry and next review",
    "Never-expiry justification",
    "Host-local token location",
    "bws config/state boundary",
    "Integration mode",
    "bws version and selected release",
    "CLI profile and state-file decision",
    "SDK language, package, version, and API reference",
    "SDK state-file decision",
    "SDK allowed operations and redaction review",
    "Runtime project scope",
    "Trusted runtime entrypoint",
    "Runtime command review",
    "Inherited-environment decision",
    "Key-name strategy",
    "Non-secret validation",
    "Event-evidence location",
    "Independent recovery location",
)

TABLE_ROW = re.compile(r"^\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$")
PLACEHOLDER = re.compile(r"<[^>]+>")
SUSPECT_PATTERNS = (
    ("an empty or malformed BWS access-token assignment", re.compile(r"(?im)\bBWS_ACCESS_TOKEN[ \t]*=[ \t]*(?:$|\||#)")),
    ("a BWS access-token assignment", re.compile(r"(?i)\bBWS_ACCESS_TOKEN\s*=\s*[^\s|]+")),
    ("a bearer authorization value", re.compile(r"(?i)\bauthorization\s*[:=]\s*bearer\s+[^\s|]+")),
    ("a private-key block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("a common provider token prefix", re.compile(r"\b(?:ghp_|github_pat_|AKIA|tvly-)[A-Za-z0-9_\-]+")),
)


def normalise(value: str) -> str:
    return " ".join(value.replace("`", "").lower().split())


def extract_rows(text: str) -> dict[str, tuple[str, int]]:
    rows: dict[str, tuple[str, int]] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = TABLE_ROW.match(line)
        if not match:
            continue
        field, value = match.groups()
        if normalise(field) in {"field", "---", ""} or set(field) <= {"-", ":"}:
            continue
        rows[normalise(field)] = (value.strip(), line_number)
    return rows


def incomplete(value: str) -> bool:
    return not value.strip() or bool(PLACEHOLDER.search(value))


def has_required_secret_identifier(value: str) -> bool:
    """Require at least one non-secret key name or opaque identifier in the contract."""
    if normalise(value) in {"", "none", "n/a", "not applicable", "unknown"}:
        return False
    return bool(re.search(r"[A-Za-z0-9]", value))


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_secret_contract.py <completed-contract.md>", file=sys.stderr)
        return 2

    contract_path = Path(sys.argv[1])
    if not contract_path.is_file():
        print("Contract file not found.", file=sys.stderr)
        return 2

    text = contract_path.read_text(encoding="utf-8")
    rows = extract_rows(text)
    errors: list[str] = []
    warnings: list[str] = []

    for description, pattern in SUSPECT_PATTERNS:
        for line_number, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                errors.append(f"Line {line_number}: contains {description}; remove the value from the contract.")

    for field in REQUIRED_FIELDS:
        key = normalise(field)
        if key not in rows:
            errors.append(f"Missing required field: {field}.")
            continue
        value, line_number = rows[key]
        if incomplete(value):
            errors.append(f"Line {line_number}: complete the non-secret value for {field}.")

    required_secret_identifiers, required_secret_identifiers_line = rows.get(
        normalise("Required secret keys or IDs"), ("", 0)
    )
    if not incomplete(required_secret_identifiers) and not has_required_secret_identifier(required_secret_identifiers):
        errors.append(
            f"Line {required_secret_identifiers_line}: record at least one non-secret required secret key or ID."
        )

    access_level = rows.get(normalise("Access level"), ("", 0))[0]
    write_justification = rows.get(normalise("Write-access justification and approval"), ("", 0))[0]
    if "write" in access_level.lower() and normalise(write_justification) in {"", "none", "n/a", "not applicable"}:
        errors.append("Write access requires a completed justification and approval reference.")

    token_expiry = rows.get(normalise("Token expiry and next review"), ("", 0))[0]
    never_justification = rows.get(normalise("Never-expiry justification"), ("", 0))[0]
    if "never" in token_expiry.lower() and normalise(never_justification) in {"", "none", "n/a", "not applicable"}:
        errors.append("A Never-expiry token requires a completed justification and review reference.")

    integration_mode = rows.get(normalise("Integration mode"), ("", 0))[0]
    mode = normalise(integration_mode)
    if mode not in {"cli runtime injection", "sdk direct integration"}:
        errors.append("Integration mode must be exactly 'CLI runtime injection' or 'SDK direct integration'.")

    sdk_fields = (
        "SDK language, package, version, and API reference",
        "SDK state-file decision",
        "SDK allowed operations and redaction review",
    )
    if mode == "sdk direct integration":
        for field in sdk_fields:
            value, line_number = rows.get(normalise(field), ("", 0))
            if normalise(value) in {"n/a", "not applicable", "none"}:
                errors.append(f"Line {line_number}: SDK mode requires a completed value for {field}.")
    elif mode == "cli runtime injection":
        for field in sdk_fields:
            value, line_number = rows.get(normalise(field), ("", 0))
            if normalise(value) not in {"n/a", "not applicable", "none"}:
                warnings.append(f"Line {line_number}: CLI mode normally records N/A for {field}; explain a hybrid design in the contract review.")

    inherited_environment = rows.get(normalise("Inherited-environment decision"), ("", 0))[0]
    if mode == "cli runtime injection" and "no-inherit-env" not in inherited_environment.lower():
        warnings.append("Document why --no-inherit-env is not used, or record its use explicitly.")

    entrypoint = rows.get(normalise("Trusted runtime entrypoint"), ("", 0))[0]
    if re.search(r"(?i)\b(?:interactive shell|arbitrary agent|docker compose|package manager)\b", entrypoint):
        warnings.append("The entrypoint description appears broad; verify it is a single reviewed executable or pinned action.")

    if errors:
        print("Contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Contract metadata validation passed. No credential-like literal was detected.")
    for warning in warnings:
        print(f"Warning: {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
