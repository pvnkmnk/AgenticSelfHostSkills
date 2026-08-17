# Agent Skills Library — Practitioner Guide

> How to use, extend, and operate the pvnkmnk agent-skills-library.
> Covers all four agents: OpenCode, Freebuff, Antigravity CLI, Codex.

---

## Overview

This library provides structured behavioral skills for AI coding and automation agents. Skills are organized into a flat canonical tree (`skills/<name>/`) and wired to MCP action layers for live tool access.

### Four-Layer Architecture

```
[Agent]
  └─ [Skills Layer]         ← skills/<name>/SKILL.md
       └─ [MCP Layer]        ← mcp/*.json configs
            └─ [Tools]        ← Proxmox API, slskd REST, Subsonic API, Obsidian vault
                 └─ [Memory]  ← Obsidian vault notes + Cipher/Mem0
```

### Skill Folder Layout

Every canonical skill lives in its own directory:

```
skills/<skill-name>/
  SKILL.md        ← canonical behavioral spec (inputs, outputs, workflow, safety, failure modes)
  README.md       ← quick-start, usage notes, dependencies, companion skills
  references/     ← external docs, patterns, design notes, example prompts
  scripts/        ← helper CLIs, test harnesses, setup utilities
```

---

## Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/pvnkmnk/agent-skills-library
cd agent-skills-library
```

### 2. Wire an MCP config

Copy a stub from `mcp/` and fill in your credentials:

```bash
cp mcp/proxmox-mcp.json ~/.config/my-agent/mcp/proxmox-mcp.json
# Edit: set PROXMOX_HOST, PROXMOX_USER, PROXMOX_TOKEN_NAME, PROXMOX_TOKEN_VALUE
```

### 3. Load skills in your agent config

Point to the canonical skill path:

```yaml
skills:
  - path: skills/homelab-safe-ops/SKILL.md
  - path: skills/subsonic-api-client/SKILL.md
```

### 4. Invoke a skill

- **OpenCode / Codex:** `Invoke homelab-safe-ops`
- **Freebuff:** `/skill homelab-safe-ops`

---

## Domain Guide

### Homelab

**Skills:** `native-wsl-workspaces` · `proxmox-ve-operations` · `proxmox-service-guest-gate` · `bitwarden-machine-account-ops` · `homelab-safe-ops` · `homelab-change-planner` · `homelab-monitoring-analyst` · `homelab-logbook` · `homelab-research-librarian` · `homelab-sre-agent` · `homelab-topology-mapper` · `homelab-network-auditor` · `docker-app-deployer` · `reverse-proxy-and-tunnel` · `media-stack-builder`

**MCP:** `mcp/proxmox-mcp.json`

**Standard workflow:**
1. Run `native-wsl-workspaces` when the control plane or repository lives in WSL; establish the native authoritative path before any write.
2. Run `proxmox-ve-operations` for official-first read-only platform inventory, access, storage, backup, or networking guidance.
3. Use `proxmox-service-guest-gate` before proposing or creating a new service LXC/VM; it requires an exact confirmation and protects legacy guests.
4. Use `bitwarden-machine-account-ops` before a host, service, CI workflow, or SDK client receives machine-readable secrets.
5. Run `homelab-topology-mapper` to understand current state and use `homelab-change-planner` to draft a change with rollback steps.
6. Gate all execution through `homelab-safe-ops` and log the outcome with `homelab-logbook` + `obsidian-homelab-logbook`.

**Network audit workflow:**
1. `homelab-safe-ops` — confirm scope and get user approval.
2. `homelab-network-auditor` — run host discovery + port scan against owned infra.
3. `homelab-change-planner` — create remediation tasks for findings.
4. `homelab-logbook` — log audit and remediation plan.

**Safety:** All destructive operations require `homelab-safe-ops` confirmation. Never bypass.

---

### Media / Music / DJ

**Skills:** `soulseek-network-orienter` · `slskd-media-acquisition` · `slsk-mcp-client` · `subsonic-media-server` · `subsonic-api-client` · `netrunner-media-orchestrator` · `music-library-organizer` · `dj-library-curator` · `dj-set-architect` · `music-listening-journal` · `dj-mix-documentarian` · `music-project-planner` · `lyrics-and-theory-bridge`

**MCP:** `mcp/slsk-mcp.json`, `mcp/slskd-mcp.json`, `mcp/subsonic-mcp.json`

**Acquisition → Playback pipeline:**
1. `soulseek-network-orienter` → orient to network culture and search strategy.
2. `slskd-media-acquisition` or `slsk-mcp-client` → search and download.
3. `music-library-organizer` → tag, structure, deduplicate files.
4. `subsonic-media-server` → trigger rescan; verify ingestion.
5. `dj-library-curator` → build playlists and crates for mixing.
6. `dj-set-architect` → plan and sequence the set.
7. `dj-mix-documentarian` + `obsidian-music-journal` → archive the mix.

For full end-to-end automation, invoke `netrunner-media-orchestrator` to coordinate all steps.

---

### Obsidian

**Skills:** `obsidian-vault-architect` · `obsidian-vault-manager` · `obsidian-homelab-logbook` · `obsidian-music-journal` · `obsidian-markdown` · `obsidian-bases` · `obsidian-cli` · `json-canvas` · `defuddle`

**Role:** Obsidian skills are the memory and journaling layer. All other domain skills write their outputs here. The vault is the persistent knowledge base for homelab ops, music curation, and project planning.

**Setup:**
1. Run `obsidian-vault-architect` once to establish the vault folder structure.
2. All domain skills will then write to the correct vault locations automatically.
3. Use `obsidian-vault-manager` for day-to-day note creation, organization, and link management via the Local REST API.

---

### Coding

**Skills:** `tdd-loop` · `refactor-with-tests` · `architecture-improvement` · `security-audit` · `authz-and-audit-log`

**Always pair with:** `git-safe-ops` (never force-push main, always branch) and `grill-me` (interrogate the plan before writing code).

---

### Meta / Reasoning

**Skills:** `grill-me` · `prompt-auditor` · `write-prd-from-conversation` · `prd-to-kanban-issues` · `orchestrator` · `eval-loop`

**Planning workflow:**
1. `grill-me` — expose gaps in the plan before committing.
2. `write-prd-from-conversation` — crystallize requirements.
3. `prd-to-kanban-issues` — decompose into issues with acceptance criteria.
4. `orchestrator` — delegate tasks across agents.
5. `eval-loop` — validate outputs against criteria.

---

## Adding a New Skill

1. Create `skills/<skill-name>/` directory.
2. Add `SKILL.md` using the template below.
3. Add `README.md` with quick-start, dependencies, and companion skills.
4. Create `references/` and `scripts/` directories (add `.gitkeep` if empty).
5. Update `REFERENCE.md` with the new skill row.
6. If a new MCP config is needed, add a stub to `mcp/<mcp-name>.json`.
7. Update the relevant domain meta-aggregator `README.md` in `skills/<domain>/`.
8. Update this `GUIDE.md` if a new domain is introduced.

### SKILL.md Template

```markdown
---
name: skill-name
description: One-line description.
category: <domain>
tags: [tag1, tag2]
agents: [opencode, freebuff, antigravity, codex]
---

# skill-name

## Purpose

[What this skill enables. 2-3 sentences.]

## Invocation

**OpenCode / Codex:** `Invoke skill-name`
**Freebuff:** `/skill skill-name`

## Workflow Steps

1. **Step:** Description.
2. **Step:** Description.

## Inputs

- [Input 1 description]
- [Input 2 description]

## Outputs

- [Output 1 description]
- [Output 2 description]

## Safety

- [Constraint 1]
- [Constraint 2]

## Failure Modes

- [Failure mode 1 — how to handle]
- [Failure mode 2 — how to handle]

## References

- [Link text](URL)

## Companion Skills

- `companion-skill-a`, `companion-skill-b`
```

---

## MCP Config Setup

Each MCP stub in `mcp/` provides:
- `name` and `description`
- `upstream` (source repo/docs URL)
- `transport` (always `stdio` for local MCP servers)
- `env` (required environment variables with placeholder values)
- `skills` (skills that use this MCP)
- `safety` (constraints to enforce)

Never commit real credentials. Use environment variables or a secrets manager.

---

## Repeatable Iteration Pattern

For each new skill or skill cluster:

1. Create `skills/<name>/SKILL.md` from the template above.
2. Add `README.md`, `references/`, `scripts/` to the skill directory.
3. Create or update MCP JSON stub in `mcp/` if new tooling is needed.
4. Add rows to `REFERENCE.md`.
5. Update the relevant domain meta-aggregator (`skills/<domain>/README.md`).
6. Update this `GUIDE.md` domain section.
7. Commit: `feat: add <skill-name> skill` or `feat: add <domain> skill cluster`.

---

## Repository Structure

```
agent-skills-library/
  README.md              ← overview, quickstart, philosophy
  GUIDE.md               ← this file: practitioner guide
  REFERENCE.md           ← master skill + MCP index
  agents.md              ← per-agent session skill groups and MCP config
  skills/
    <skill-name>/        ← canonical skill tree (one per skill)
      SKILL.md
      README.md
      references/
      scripts/
    homelab/README.md    ← homelab family meta-aggregator index
    media/README.md      ← media family meta-aggregator index
    obsidian/README.md   ← obsidian family meta-aggregator index
    meta/                ← composite specs: meta/reasoning skills
    coding/              ← composite specs: coding skills
    social/              ← composite specs: social skills
    mcp/                 ← composite specs: MCP/tool bridge skills
  mcp/
    proxmox-mcp.json
    slsk-mcp.json
    slskd-mcp.json
    subsonic-mcp.json
```
