#!/usr/bin/env bash
# Verify that a requested workspace is a native WSL filesystem path before use.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: verify_wsl_workspace.sh <absolute-workspace-path> [--probe-write]

Refuses /mnt paths and drvfs mounts. With --probe-write, performs a local
atomic write/read/hash/delete probe in the requested workspace.
EOF
}

workspace="${1:-}"
probe="false"

if [[ -z "$workspace" || "$workspace" == "-h" || "$workspace" == "--help" ]]; then
  usage
  exit 2
fi

if [[ "${2:-}" == "--probe-write" ]]; then
  probe="true"
elif [[ -n "${2:-}" ]]; then
  usage
  exit 2
fi

[[ "$workspace" = /* ]] || { printf 'FAIL: workspace must be an absolute Linux path.\n' >&2; exit 1; }
[[ -d "$workspace" ]] || { printf 'FAIL: workspace does not exist: %s\n' "$workspace" >&2; exit 1; }

canonical="$(realpath "$workspace")"
case "$canonical" in
  /mnt|/mnt/*)
    printf 'FAIL: workspace resolves to a mounted Windows path: %s\n' "$canonical" >&2
    exit 1
    ;;
  /home/*|/srv/*|/opt/*)
    ;;
  *)
    printf 'FAIL: workspace is not in an approved native WSL root: %s\n' "$canonical" >&2
    exit 1
    ;;
esac

filesystem="$(stat -f -c %T "$canonical")"
if [[ "$filesystem" == "drvfs" ]]; then
  printf 'FAIL: workspace filesystem is drvfs: %s\n' "$canonical" >&2
  exit 1
fi

if ! grep -qiE '(microsoft|wsl)' /proc/version 2>/dev/null; then
  printf 'WARN: WSL kernel marker not found; continuing because path/filesystem checks passed.\n' >&2
fi

printf 'PASS: canonical workspace: %s\n' "$canonical"
printf 'PASS: filesystem: %s\n' "$filesystem"
printf 'PASS: current user: %s\n' "$(id -un)"
printf 'PASS: kernel: %s\n' "$(uname -r)"

if [[ "$probe" == "true" ]]; then
  temp="$(mktemp "$canonical/.native-wsl-probe.XXXXXX")"
  payload="native-wsl-workspace-probe-$(date +%s)-$$"
  printf '%s\n' "$payload" > "$temp"
  expected="$(printf '%s\n' "$payload" | sha256sum | awk '{print $1}')"
  actual="$(sha256sum "$temp" | awk '{print $1}')"
  [[ "$expected" == "$actual" ]] || { rm -f "$temp"; printf 'FAIL: atomic write/read hash mismatch.\n' >&2; exit 1; }
  rm -f "$temp"
  [[ ! -e "$temp" ]] || { printf 'FAIL: probe cleanup failed.\n' >&2; exit 1; }
  printf 'PASS: native atomic write/read/delete probe completed.\n'
fi
