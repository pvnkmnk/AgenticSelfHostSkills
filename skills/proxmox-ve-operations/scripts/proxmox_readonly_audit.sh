#!/usr/bin/env bash
set -euo pipefail

require_command() {
  command -v "$1" >/dev/null 2>&1 || {
    printf 'ERROR: required command not found: %s\n' "$1" >&2
    exit 127
  }
}

for command in pveversion pvesh pvesm pct qm ip findmnt; do
  require_command "$command"
done

printf '%s\n' '# Proxmox VE Read-Only Audit'
printf 'Timestamp (UTC): '; date -u +'%Y-%m-%dT%H:%M:%SZ'
printf '\n## Version\n'; pveversion -v || true
printf '\n## Nodes\n'; pvesh get /nodes || true
printf '\n## Cluster resources\n'; pvesh get /cluster/resources --type vm || true
printf '\n## Storage status\n'; pvesm status || true
printf '\n## Containers\n'; pct list || true
printf '\n## Virtual machines\n'; qm list || true
printf '\n## Network addresses\n'; ip -brief address || true
printf '\n## Routes\n'; ip route || true
printf '\n## Mounts\n'; findmnt || true

printf '\nNOTE: This script is read-only. Review output before recording inventory or proposing changes.\n'
