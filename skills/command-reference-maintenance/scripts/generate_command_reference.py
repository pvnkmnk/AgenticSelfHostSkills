#!/usr/bin/env python3
"""Generate shareable command references from an explicitly supplied sanitized dump."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

SCHEMA_VERSION = "1.0.0"
VALID_TYPES = {
    "pwsh": {"Alias", "Cmdlet", "Function", "Filter"},
    "bash": {"Command", "Alias"},
}
VERSION_RE = re.compile(r"^[\d.]+(?:…|\.\.\.)?$")


def parse_pwsh(line: str) -> dict | None:
    line = line.strip()
    if not line:
        return None
    parts = line.split(None, 1)
    if len(parts) != 2:
        return None
    kind, rest = parts
    if kind not in VALID_TYPES["pwsh"]:
        return None
    if kind == "Alias":
        if " -> " in rest:
            name, target = (part.strip() for part in rest.split(" -> ", 1))
        else:
            name, target = rest.strip(), None
        return {"type": kind, "name": name, "module": "Unknown", "versions": [], "alias_target": target}
    tokens = rest.split()
    module = "Unknown"
    versions: list[str] = []
    if len(tokens) >= 2 and VERSION_RE.match(tokens[-2]):
        module, versions, tokens = tokens[-1], [tokens[-2]], tokens[:-2]
    elif tokens and VERSION_RE.match(tokens[-1]):
        versions, tokens = [tokens[-1]], tokens[:-1]
    name = " ".join(tokens).strip()
    if not name:
        return None
    return {"type": kind, "name": name, "module": module, "versions": versions, "alias_target": None}


def parse_aliases(alias_path: Path | None) -> dict[str, str]:
    if alias_path is None:
        return {}
    result: dict[str, str] = {}
    for raw in alias_path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if not raw.startswith("alias ") or "=" not in raw:
            continue
        name, target = raw[6:].split("=", 1)
        target = target.strip()
        if len(target) >= 2 and target[0] == target[-1] and target[0] in {"'", '"'}:
            target = target[1:-1]
        if name.strip():
            result[name.strip()] = target
    return result


def parse_bash(line: str, aliases: dict[str, str]) -> dict | None:
    name = line.strip()
    if not name:
        return None
    return {
        "type": "Alias" if name in aliases else "Command",
        "name": name,
        "module": "Bash",
        "versions": [],
        "alias_target": aliases.get(name),
    }


def dedupe(entries: list[dict]) -> list[dict]:
    merged: dict[tuple[str, str, str], dict] = {}
    for entry in entries:
        key = (entry["type"], entry["name"], entry["module"])
        prior = merged.get(key)
        if prior is None:
            merged[key] = {**entry, "versions": list(entry["versions"])}
            continue
        for version in entry["versions"]:
            if version not in prior["versions"]:
                prior["versions"].append(version)
        if not prior["alias_target"] and entry["alias_target"]:
            prior["alias_target"] = entry["alias_target"]
    return sorted(merged.values(), key=lambda item: (item["module"].lower(), item["name"].lower()))


def markdown(entries: list[dict], shell: str, source: str) -> str:
    by_module: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        by_module[entry["module"]].append(entry)
    lines = [
        "# Command Reference\n\n",
        f"_Generated from sanitized `{shell}` input: `{source}`._\n\n",
        f"**Unique commands:** {len(entries)}\n\n",
    ]
    for module, items in sorted(by_module.items(), key=lambda item: item[0].lower()):
        lines.extend([f"## {module}\n\n", "| Command | Type | Versions | Alias target |\n", "|---|---|---|---|\n"])
        for entry in items:
            versions = ", ".join(entry["versions"]) or "—"
            target = entry["alias_target"] or "—"
            lines.append(f"| {entry['name'].replace('|', '\\|')} | {entry['type']} | {versions} | {target.replace('|', '\\|')} |\n")
        lines.append("\n")
    return "".join(lines)


def yaml_text(entries: list[dict], shell: str, source: str) -> str:
    lines = [f"# shell: {shell}\n", f"# source: {source}\n", f"# schema_version: {SCHEMA_VERSION}\n\n"]
    for entry in entries:
        lines.extend([
            "- name: " + json.dumps(entry["name"]) + "\n",
            "  type: " + json.dumps(entry["type"]) + "\n",
            "  module: " + json.dumps(entry["module"]) + "\n",
            "  versions: " + json.dumps(entry["versions"]) + "\n",
            "  alias_target: " + ("null" if entry["alias_target"] is None else json.dumps(entry["alias_target"])) + "\n",
        ])
    return "".join(lines)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    meta = data.get("meta")
    if not isinstance(meta, dict) or meta.get("shell") not in VALID_TYPES:
        errors.append("meta.shell is missing or unsupported")
        return errors
    commands = data.get("commands")
    if not isinstance(commands, list):
        return ["commands must be a list"]
    for index, entry in enumerate(commands):
        if not isinstance(entry, dict):
            errors.append(f"commands[{index}] is not an object")
            continue
        if entry.get("type") not in VALID_TYPES[meta["shell"]]:
            errors.append(f"commands[{index}].type is invalid for {meta['shell']}")
        for key in ("name", "module", "versions", "alias_target"):
            if key not in entry:
                errors.append(f"commands[{index}].{key} is missing")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shell", required=True, choices=sorted(VALID_TYPES))
    parser.add_argument("--input", required=True, type=Path, help="Sanitized command dump; do not use a private inventory.")
    parser.add_argument("--aliases", type=Path, help="Optional sanitized Bash alias output.")
    parser.add_argument("--out-prefix", required=True, type=Path)
    args = parser.parse_args()

    if not args.input.is_file():
        parser.error(f"Input does not exist: {args.input}")
    aliases = parse_aliases(args.aliases) if args.shell == "bash" else {}
    parser_fn = (lambda line: parse_bash(line, aliases)) if args.shell == "bash" else parse_pwsh
    entries = dedupe([parsed for line in args.input.read_text(encoding="utf-8").splitlines() if (parsed := parser_fn(line))])
    payload = {
        "meta": {"shell": args.shell, "source": str(args.input), "schema_version": SCHEMA_VERSION, "total_unique_commands": len(entries)},
        "commands": entries,
    }
    errors = validate(payload)
    if errors:
        print("Validation failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1

    prefix = args.out_prefix
    prefix.parent.mkdir(parents=True, exist_ok=True)
    prefix.with_suffix(".md").write_text(markdown(entries, args.shell, str(args.input)), encoding="utf-8")
    prefix.with_suffix(".json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    prefix.with_suffix(".yaml").write_text(yaml_text(entries, args.shell, str(args.input)), encoding="utf-8")
    print(f"Generated {len(entries)} unique sanitized {args.shell} command references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
