#!/usr/bin/env bash
# Download one known artifact and atomically install it into a native WSL workspace.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install_verified_url.sh <url> <sha256> <absolute-native-target> [mode]

Download an artifact from a pre-verified URL, check its SHA-256, and atomically
move it to an absolute /home/... WSL target. Default mode is 0644.
EOF
}

url="${1:-}"
expected_sha256="${2:-}"
target="${3:-}"
mode="${4:-0644}"

[[ -n "$url" && -n "$expected_sha256" && -n "$target" ]] || { usage >&2; exit 2; }
[[ "$target" = /home/* ]] || { printf 'FAIL: target must be a native /home/... path.\n' >&2; exit 1; }
[[ "$expected_sha256" =~ ^[a-fA-F0-9]{64}$ ]] || { printf 'FAIL: SHA-256 must be 64 hexadecimal characters.\n' >&2; exit 2; }
[[ "$mode" =~ ^0?[0-7]{3,4}$ ]] || { printf 'FAIL: mode must be octal.\n' >&2; exit 2; }

parent="$(dirname "$target")"
mkdir -p "$parent"
filesystem="$(stat -f -c %T "$parent")"
[[ "$filesystem" != "drvfs" ]] || { printf 'FAIL: target parent is a Windows mount.\n' >&2; exit 1; }

temp="$(mktemp "$parent/.native-wsl-install.XXXXXX")"
cleanup() { rm -f "$temp"; }
trap cleanup EXIT

curl -fsSL --proto '=https' --tlsv1.2 "$url" -o "$temp"
actual_sha256="$(sha256sum "$temp" | awk '{print $1}')"
[[ "$actual_sha256" == "${expected_sha256,,}" ]] || {
  printf 'FAIL: checksum mismatch for %s\n' "$target" >&2
  printf 'Expected: %s\nActual:   %s\n' "$expected_sha256" "$actual_sha256" >&2
  exit 1
}

chmod "$mode" "$temp"
mv "$temp" "$target"
trap - EXIT
printf 'PASS: installed verified artifact: %s\n' "$target"
printf 'SHA-256: %s\n' "$actual_sha256"
