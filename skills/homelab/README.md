# Homelab Skills — Meta Aggregator

This directory (`skills/homelab/`) is a **meta-aggregator** for the homelab skill family. It holds composite `.SKILL.md` files that were the original source-of-truth before all homelab skills were migrated into individual `skills/<name>/` trees.

## Status

All specs in this directory have been **migrated** into their canonical standalone trees:

| Composite file | Canonical location |
|---|---|
| `docker-app-deployer.SKILL.md` | [`skills/docker-app-deployer/`](../docker-app-deployer/) |
| `homelab-change-planner.SKILL.md` | [`skills/homelab-change-planner/`](../homelab-change-planner/) |
| `homelab-logbook.SKILL.md` | [`skills/homelab-logbook/`](../homelab-logbook/) |
| `homelab-monitoring-analyst.SKILL.md` | [`skills/homelab-monitoring-analyst/`](../homelab-monitoring-analyst/) |
| `homelab-research-librarian.SKILL.md` | [`skills/homelab-research-librarian/`](../homelab-research-librarian/) |
| `homelab-safe-ops.SKILL.md` | [`skills/homelab-safe-ops/`](../homelab-safe-ops/) |
| `homelab-sre-agent.SKILL.md` | [`skills/homelab-sre-agent/`](../homelab-sre-agent/) |
| `homelab-topology-mapper.SKILL.md` | [`skills/homelab-topology-mapper/`](../homelab-topology-mapper/) |
| `media-stack-builder.SKILL.md` | [`skills/media-stack-builder/`](../media-stack-builder/) |
| `reverse-proxy-and-tunnel.SKILL.md` | [`skills/reverse-proxy-and-tunnel/`](../reverse-proxy-and-tunnel/) |

## Project control-plane and security skills

The following canonical standalone trees were exported from the Windows/WSL/Proxmox dotfiles and homelab project. They are not legacy composite specs and should be loaded directly when their trigger applies.

| Skill | Canonical location | Primary use |
|---|---|---|
| `native-wsl-workspaces` | [`skills/native-wsl-workspaces/`](../native-wsl-workspaces/) | Establish the authoritative native WSL workspace and avoid UNC/mount write confusion. |
| `proxmox-ve-operations` | [`skills/proxmox-ve-operations/`](../proxmox-ve-operations/) | Inspect and safely operate Proxmox VE 9 using official-first guidance. |
| `proxmox-service-guest-gate` | [`skills/proxmox-service-guest-gate/`](../proxmox-service-guest-gate/) | Gate new service guest changes and protect legacy guests. |
| `bitwarden-machine-account-ops` | [`skills/bitwarden-machine-account-ops/`](../bitwarden-machine-account-ops/) | Scope Bitwarden Secrets Manager machine identities, bws/SDK runtime use, rotation, and recovery. |

## Purpose going forward

This directory serves as a **discovery index** for the homelab skill family. Agents browsing for infrastructure-related skills can start here and follow the links above to individual canonical skill trees.
