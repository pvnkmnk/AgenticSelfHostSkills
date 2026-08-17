# AgenticSelfHostSkills

> A comprehensive, opinionated agent skills library for **OpenCode**, **Freebuff**, **Antigravity CLI**, and **Codex** — covering homelab, media, music, DJ, Obsidian, coding, and social domains.

**Owner:** pvnkmnk  
**Last updated:** August 17, 2026
**Former repository path:** `pvnkmnk/agent-skills-library` (redirects here)
**Stack:** Windows 11 + WSL2, MCP, Obsidian, Cipher/Mem0, slskd, Subsonic/OpenSubsonic, Proxmox  
**Structure:** 37 standalone canonical skill trees plus composite discovery specifications

---

## Overview

This repo is the single source of truth for all agent skills used across the pvnkmnk agent ecosystem. It follows a two-layer model:

- **Behavior layer** — `SKILL.md` files that encode opinionated workflows, decision trees, safety rules, and domain knowledge for each agent.
- **Action layer** — MCP server configs and API wrappers (Proxmox MCP, Slsk MCP, slskd-mcp, Subsonic/OpenSubsonic HTTP APIs) that do the actual work.

Agents (OpenCode, Freebuff, Antigravity CLI, Codex) load skills by referencing this repo in their config (`agents.md`, `opencode.json`, or equivalent).

---

## Repo Structure

All skills live in a **flat, canonical tree**: `skills/<skill-name>/SKILL.md`. Each skill folder also contains a `README.md`, a `references/` directory, and a `scripts/` directory.

Domain subdirectories (`skills/homelab/`, `skills/media/`, `skills/obsidian/`) are **meta-aggregator indexes** that link to canonical skill trees — they are not the primary skill locations.

```
AgenticSelfHostSkills/
  README.md                          ← this file
  GUIDE.md                           ← practitioner guide (how to use, extend, operate)
  REFERENCE.md                       ← master skill + MCP index table
  agents.md                          ← per-agent session skill groups and MCP config
  skills/
    ├── meta-aggregators (index-only)
    │   ├── homelab/README.md         ← homelab family discovery index
    │   ├── media/README.md           ← media family discovery index
    │   └── obsidian/README.md        ← obsidian family discovery index
    │
    ├── canonical skill trees (one folder per skill)
    │   ├── <skill-name>/
    │   │   ├── SKILL.md              ← canonical behavioral spec
    │   │   ├── README.md             ← quick-start and usage notes
    │   │   ├── references/           ← external docs, patterns, examples
    │   │   └── scripts/              ← helper CLIs, test harnesses, automation
    │   └── ...
    │
    ├── meta/                         ← composite specs: meta/reasoning skills
    ├── coding/                       ← composite specs: coding skills
    ├── social/                       ← composite specs: social skills
    └── mcp/                          ← composite specs: MCP/tool bridge skills
  mcp/
    proxmox-mcp.json
    slsk-mcp.json
    slskd-mcp.json
    subsonic-mcp.json
```

### Canonical skill trees (skills/<name>/)

| Domain | Skills |
|---|---|
| Homelab | `docker-app-deployer` · `homelab-change-planner` · `homelab-logbook` · `homelab-monitoring-analyst` · `homelab-network-auditor` · `homelab-research-librarian` · `homelab-safe-ops` · `homelab-sre-agent` · `homelab-topology-mapper` · `media-stack-builder` · `reverse-proxy-and-tunnel` |
| Media / Music / DJ | `dj-library-curator` · `dj-mix-documentarian` · `dj-set-architect` · `music-library-organizer` · `music-listening-journal` · `music-project-planner` · `netrunner-media-orchestrator` · `slsk-mcp-client` · `slskd-media-acquisition` · `soulseek-network-orienter` · `subsonic-api-client` · `subsonic-media-server` |
| Obsidian | `obsidian-homelab-logbook` · `obsidian-music-journal` · `obsidian-vault-architect` · `obsidian-vault-manager` |

---

## Skill Categories

| Category | Count | Description |
|---|---|---|
| **Meta / Reasoning** | 6 | Planning, auditing, PRD, orchestration, eval |
| **Coding** | 5 | TDD, refactoring, architecture, security, authZ |
| **Obsidian** | 9 | Official Obsidian Skills + bespoke vault skills |
| **Homelab** | 12 | Proxmox, Docker, networking, SRE, research, network audit |
| **Media / Music / DJ** | 13 | Soulseek, slskd, Subsonic, DJ, listening, netrunner |
| **Social** | 2 | Social impact lens, case notes |
| **MCP / Tool Bridge** | 3 | Memory bridge, filesystem, git safety |
| **Total** | **50** | |

---

## Quick Start

### OpenCode

1. Clone this repo to your project root or `~/.config/opencode/skills/`.
2. Add to your `agents.md`:

```markdown
## Skills
This agent has access to the skills in ./skills/. Use "Invoke <skill-name>" to activate a skill.
```

3. Reference in `opencode.json`:

```json
{
  "skills": "./skills"
}
```

### Freebuff

1. Clone or symlink `skills/` into Freebuff's skill directory.
2. Invoke skills via `/skill <skill-name>`.

### Antigravity CLI / Codex

1. Point your agent config at this repo's `skills/` directory.
2. Use your skill manager (aix/OpenPackage or equivalent) to index skills from this repo.

### Invoking a skill

- **OpenCode / Codex:** `Invoke <skill-name>`
- **Freebuff:** `/skill <skill-name>`

---

## Governance and Consolidation

Read [`SKILL_CATALOG.md`](SKILL_CATALOG.md) for the canonical-home rules, intake and deprecation process, and provenance of skills promoted from validated handoffs. Reusable behavior belongs here; private control-plane instructions, service desired state, and secret values do not.

## MCP Action Layers

The following MCP servers provide the action layer underneath behavioral skills:

| MCP Server | Purpose | Config |
|---|---|---|
| Proxmox MCP | Proxmox VM/LXC/monitoring | `mcp/proxmox-mcp.json` |
| Slsk MCP | Soulseek P2P search & download | `mcp/slsk-mcp.json` |
| slskd-mcp | slskd OpenAPI → MCP (70 paths) | `mcp/slskd-mcp.json` |
| Subsonic MCP | Subsonic/OpenSubsonic library ops | `mcp/subsonic-mcp.json` |

---

## Upstream Sources

- [Official Obsidian Skills](https://github.com/kepano/obsidian-skills) by kepano
- [claude-homelab](https://github.com/jmagar/claude-homelab) by jmagar — SKILL.md structure reference
- [Slsk MCP](https://mcpmarket.com) — Soulseek MCP server
- [slskd-mcp](https://github.com/abl030/slskd-mcp) by abl030
- [Subsonic API](https://subsonic.org/pages/api.jsp) / [OpenSubsonic API](https://opensubsonic.netlify.app)
- [slskd](https://github.com/slskd/slskd) — headless Soulseek client

---

## Philosophy

- **Behavior on top, action underneath.** Skills encode *how to think and decide*; MCP servers encode *how to act*.
- **Safety by default.** Every homelab and media skill has explicit safety rules and read-first constraints.
- **Domain-true.** Skills reflect actual workflows: Soulseek culture, Subsonic/OpenSubsonic auth, Proxmox VE, Obsidian vault semantics, DJ set architecture, social work ethics.
- **Composable.** Skills are designed to call each other — `netrunner-media-orchestrator` chains the full pipeline from `slskd-media-acquisition` through to `obsidian-music-journal`.
- **Self-documenting.** Every skill tree contains its own `README.md`, `references/`, and `scripts/` so an agent or developer can navigate and understand any skill in isolation.
