---
name: homelab-topology-mapper
description: Builds and maintains a structured map of hosts, VMs, containers, networks, storage, and services.
category: homelab
tags: [homelab, topology, inventory, documentation]
agents: [opencode, freebuff, antigravity, codex]
---

# homelab-topology-mapper

## Purpose

Maintains a living, structured map of the entire homelab environment. This is the foundation for all other homelab skills — you must know what exists before you can change anything.

## Invocation

**OpenCode / Codex:** `Invoke homelab-topology-mapper`
**Freebuff:** `/skill homelab-topology-mapper`

## Workflow

1. **Inventory nodes** — List all physical hosts, VMs, and LXC containers with: hostname, IP, OS, resources (CPU/RAM/storage), and role.
2. **Map services** — For each node, list running services, Docker containers, and their ports.
3. **Map networking** — Document VLANs, subnets, DNS entries, reverse proxy routes, and VPN/tunnel endpoints.
4. **Map storage** — Document NAS mounts, ZFS pools, backup targets, and retention policies.
5. **Output format** — Produce a structured Markdown table or YAML block that can be saved to Obsidian via `obsidian-homelab-logbook`.

## Output Schema

```yaml
nodes:
  - name: pve-01
    type: proxmox-host
    ip: 192.168.1.10
    os: Proxmox VE 8.x
    vms:
      - name: media-server
        ip: 192.168.1.20
        services: [slskd, navidrome, jellyfin]
      - name: reverse-proxy
        ip: 192.168.1.30
        services: [nginx-proxy-manager, cloudflared]
network:
  subnets: [192.168.1.0/24]
  vlans: []
  dns: technitium @ 192.168.1.5
  vpn: tailscale mesh
storage:
  nas: truenas @ 192.168.1.40
  pools: [data, backup]
  backup-target: proxmox-backup-server
```

## This homelab

The schema above stays generic on purpose. The current verified map for this
homelab lives in `homelab-proxmox-ansible/docs/network-map.md`, with service
and storage detail in `homelab-proxmox-ansible/docs/observed-state.md`. Update
those rather than producing a parallel map, and treat the staged validation
directories as audit history, not as current state.

## Companion Skills

- `homelab-change-planner` — use topology as input to change plans
- `homelab-logbook` — log topology changes
- `obsidian-homelab-logbook` — persist topology to vault
- `homelab-safe-ops` — always active alongside this skill

## References

- Proxmox VE API: https://pve.proxmox.com/pve-docs/api-viewer/
- r/homelab wiki: https://www.reddit.com/r/homelab/wiki/index
