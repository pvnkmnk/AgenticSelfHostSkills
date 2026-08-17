# Agent Skills Reference

> Master index for all skills in the pvnkmnk agent-skills-library.
> Use this as the single reference for OpenCode, Freebuff, Antigravity CLI, and Codex.
>
> **Invoke a skill:** `Invoke <skill-id>` (OpenCode/Codex) | `/skill <skill-id>` (Freebuff)
>
> **Canonical skill path pattern:** `skills/<skill-id>/SKILL.md`

Last updated: July 14, 2026

---

## Meta / Reasoning Skills

> ⚠️ **Ghost specs** — The six skills below are listed in REFERENCE.md but their spec files live at
> `skills/meta/<skill-id>.SKILL.md` (composite format). Standalone `skills/<skill-id>/SKILL.md` trees
> have not yet been migrated. These skills are **not yet invocable** until migration is complete.

| Skill ID | Description | Path |
|---|---|---|
| `grill-me` | Interrogates a plan or idea with pointed questions to expose gaps before execution | `skills/meta/grill-me.SKILL.md` |
| `prompt-auditor` | Reviews and rewrites prompts for clarity, specificity, and safety | `skills/meta/prompt-auditor.SKILL.md` |
| `write-prd-from-conversation` | Turns a freeform conversation into a structured PRD | `skills/meta/write-prd-from-conversation.SKILL.md` |
| `prd-to-kanban-issues` | Decomposes a PRD into Kanban-ready issues with acceptance criteria | `skills/meta/prd-to-kanban-issues.SKILL.md` |
| `orchestrator` | Plans and delegates multi-step tasks across agents and tools | `skills/meta/orchestrator.SKILL.md` |
| `eval-loop` | Runs evaluation loops on agent outputs against defined criteria | `skills/meta/eval-loop.SKILL.md` |

---

## Coding Skills

> ⚠️ **Ghost specs** — The five skills below live at `skills/coding/<skill-id>.SKILL.md` (composite format).
> Standalone trees not yet migrated.

| Skill ID | Description | Path |
|---|---|---|
| `tdd-loop` | Drives a red-green-refactor TDD loop for any feature or fix | `skills/coding/tdd-loop.SKILL.md` |
| `refactor-with-tests` | Safely refactors existing code with test coverage as the safety net | `skills/coding/refactor-with-tests.SKILL.md` |
| `architecture-improvement` | Reviews and proposes improvements to system architecture and module boundaries | `skills/coding/architecture-improvement.SKILL.md` |
| `security-audit` | Audits code for common vulnerabilities (OWASP Top 10, injection, auth flaws) | `skills/coding/security-audit.SKILL.md` |
| `authz-and-audit-log` | Implements RBAC authorization and audit logging patterns (FastAPI/PostgreSQL focused) | `skills/coding/authz-and-audit-log.SKILL.md` |

---

## Obsidian Skills

### Official Obsidian Skills (upstream: github.com/kepano/obsidian-skills)

> ⚠️ **Ghost specs** — The five upstream skills below live at `skills/obsidian/<skill-id>.SKILL.md`
> (composite format). No standalone trees.

| Skill ID | Description | Path |
|---|---|---|
| `obsidian-markdown` | Teaches Obsidian-flavored Markdown: wikilinks, YAML properties, callouts, embeds, tags | `skills/obsidian/obsidian-markdown.SKILL.md` |
| `obsidian-bases` | Teaches agents to work with Bases (Obsidian's structured data tables) | `skills/obsidian/obsidian-bases.SKILL.md` |
| `json-canvas` | Teaches the JSON Canvas format for visual canvases and whiteboards | `skills/obsidian/json-canvas.SKILL.md` |
| `obsidian-cli` | Teaches agents to use the Obsidian CLI for vault-level terminal workflows | `skills/obsidian/obsidian-cli.SKILL.md` |
| `defuddle` | Extracts clean Markdown from web pages for vault import | `skills/obsidian/defuddle.SKILL.md` |

### Bespoke Obsidian Skills

| Skill ID | Description | Path |
|---|---|---|
| `obsidian-vault-architect` | Designs and enforces folder structure, naming conventions, MOCs, and template standards for Obsidian vaults | `skills/obsidian-vault-architect/SKILL.md` |
| `obsidian-homelab-logbook` | Logs homelab change events, incidents, and maintenance notes as structured Obsidian notes | `skills/obsidian-homelab-logbook/SKILL.md` |
| `obsidian-music-journal` | Standardizes listening, DJ set, and production journal entries in the vault | `skills/obsidian-music-journal/SKILL.md` |
| `obsidian-vault-manager` | Primary interface for Obsidian vault ops: create notes, manage folders, apply templates, maintain links via Local REST API | `skills/obsidian-vault-manager/SKILL.md` |

> **Deprecated composite files** — the following files in `skills/obsidian/` have been superseded by the
> standalone skill trees above and should be treated as read-only archives:
> - `skills/obsidian/obsidian-music-journal.SKILL.md` → superseded by `skills/obsidian-music-journal/SKILL.md`
> - `skills/obsidian/obsidian-homelab-logbook.SKILL.md` → superseded by `skills/obsidian-homelab-logbook/SKILL.md`
> - `skills/obsidian/obsidian-vault-architect.SKILL.md` → superseded by `skills/obsidian-vault-architect/SKILL.md`

---

## Homelab Skills

### Behavior Skills

| Skill ID | Description | Path |
|---|---|---|
| `homelab-topology-mapper` | Builds and maintains a structured map of hosts, VMs, containers, networks, and services | `skills/homelab-topology-mapper/SKILL.md` |
| `homelab-change-planner` | Plans infrastructure changes with explicit risk assessment and rollback steps before execution | `skills/homelab-change-planner/SKILL.md` |
| `homelab-safe-ops` | Encodes read-first, no-destroy-by-default safety constraints for all homelab automation | `skills/homelab-safe-ops/SKILL.md` |
| `homelab-monitoring-analyst` | Interprets metrics and logs, summarizes incidents, suggests next investigation steps | `skills/homelab-monitoring-analyst/SKILL.md` |
| `homelab-logbook` | Systematizes change and incident logging, linked to topology and issues | `skills/homelab-logbook/SKILL.md` |
| `homelab-research-librarian` | Teaches agents where and how to find reliable homelab and self-hosting information | `skills/homelab-research-librarian/SKILL.md` |
| `homelab-sre-agent` | SRE-style agent behavior over monitoring tools and MCP endpoints | `skills/homelab-sre-agent/SKILL.md` |
| `homelab-network-auditor` | Scans homelab for open ports, audits firewall rules, and generates network security reports | `skills/homelab-network-auditor/SKILL.md` |
| `native-wsl-workspaces` | Establishes an authoritative native WSL workspace and prevents unsafe UNC, mount, and remote-write confusion | `skills/native-wsl-workspaces/SKILL.md` |
| `proxmox-ve-operations` | Guides official-first, read-before-write Proxmox VE 9 operations across guests, storage, networking, backup, and access | `skills/proxmox-ve-operations/SKILL.md` |
| `proxmox-service-guest-gate` | Gates fresh Proxmox service-guest creation and protects legacy guests from implicit changes | `skills/proxmox-service-guest-gate/SKILL.md` |
| `bitwarden-machine-account-ops` | Designs and operates scoped Bitwarden Secrets Manager machine accounts, bws injection, SDK exceptions, rotation, and recovery | `skills/bitwarden-machine-account-ops/SKILL.md` |

### Infrastructure Action Skills

| Skill ID | Description | Path |
|---|---|---|
| `media-stack-builder` | Scaffolds Docker Compose media stacks: slskd, Subsonic, Jellyfin, reverse proxy, Watchtower | `skills/media-stack-builder/SKILL.md` |
| `reverse-proxy-and-tunnel` | Secure service exposure via Traefik/NPM/Caddy + Cloudflare Tunnel/WireGuard/Tailscale | `skills/reverse-proxy-and-tunnel/SKILL.md` |
| `docker-app-deployer` | Safe Docker Compose deployment, env var management, and update patterns | `skills/docker-app-deployer/SKILL.md` |

---

## Media / Music Skills

### Soulseek / slskd / Subsonic Pipeline

| Skill ID | Description | Path |
|---|---|---|
| `soulseek-network-orienter` | Teaches Soulseek culture, etiquette, and search strategies; logs discoveries to Obsidian | `skills/soulseek-network-orienter/SKILL.md` |
| `slskd-media-acquisition` | Uses slskd web/API in homelab: token auth, HTTPS, reverse proxy, queue management | `skills/slskd-media-acquisition/SKILL.md` |
| `slsk-mcp-client` | Wraps the Slsk MCP server with safety rules, rate limits, and session logging | `skills/slsk-mcp-client/SKILL.md` |
| `subsonic-media-server` | Subsonic/OpenSubsonic auth, browsing, rescans, playlist management, library hygiene | `skills/subsonic-media-server/SKILL.md` |
| `subsonic-api-client` | Integration guidance for Subsonic/OpenSubsonic client libraries in netrunner and related projects | `skills/subsonic-api-client/SKILL.md` |
| `netrunner-media-orchestrator` | Orchestrates the full acquisition-to-playback media pipeline for the netrunner project | `skills/netrunner-media-orchestrator/SKILL.md` |

### Music Library, Listening & DJ

| Skill ID | Description | Path |
|---|---|---|
| `music-library-organizer` | Structures listening collection: folders, canonical filenames, tags, Obsidian alignment | `skills/music-library-organizer/SKILL.md` |
| `music-listening-journal` | Logs active listening sessions, albums, and tracks to Obsidian with ratings, notes, and context | `skills/music-listening-journal/SKILL.md` |
| `dj-library-curator` | Curates DJ-friendly library with BPM/key/energy tags and context-specific crates | `skills/dj-library-curator/SKILL.md` |
| `dj-set-architect` | Plans sets as emotional arcs (opening → build → peak → comedown → close) with transition tracking | `skills/dj-set-architect/SKILL.md` |
| `dj-mix-documentarian` | Documents completed DJ mixes: tracklists, timestamps, transitions, gear notes, Obsidian archive | `skills/dj-mix-documentarian/SKILL.md` |
| `music-project-planner` | Plans music production and release projects with phased milestones, task breakdowns, and Obsidian integration | `skills/music-project-planner/SKILL.md` |
| `lyrics-and-theory-bridge` | Bridges lyric writing with music theory: prosody, harmonic function, flow mapping, targeted edit suggestions | `skills/lyrics-and-theory-bridge/SKILL.md` |

---

## Social Domain Skills

> ⚠️ **Ghost specs** — The two skills below live at `skills/social/<skill-id>.SKILL.md` (composite format).
> Standalone trees not yet migrated.

| Skill ID | Description | Path |
|---|---|---|
| `social-impact-lens` | Applies sociological and social-work ethics lens to any feature or system design | `skills/social/social-impact-lens.SKILL.md` |
| `case-note-structurer` | Structures case notes in social work and community support contexts | `skills/social/case-note-structurer.SKILL.md` |

---

## MCP / Tool Bridge Skills

| Skill ID | Description | Path |
|---|---|---|
| `memory-layer-bridge` | Teaches agents when to query Cipher/Mem0, when to consult Obsidian, when to log decisions | `skills/memory-layer-bridge/SKILL.md` |
| `filesystem-refactor-planner` | Plans filesystem refactors safely using MCP filesystem tools | `skills/mcp/filesystem-refactor-planner.SKILL.md` |
| `git-safe-ops` | Encodes safe git operations: no force-push to main, always branch, always review | `skills/git-safe-ops/SKILL.md` |

---

## MCP Config Files

| Config | Purpose | Upstream |
|---|---|---|
| `mcp/proxmox-mcp.json` | Proxmox VM/LXC/monitoring MCP server | MCPMarket: Homelab Proxmox MCP |
| `mcp/slsk-mcp.json` | Soulseek P2P access MCP server | MCPMarket: Slsk MCP |
| `mcp/slskd-mcp.json` | slskd OpenAPI → MCP auto-generated server | github.com/abl030/slskd-mcp |
| `mcp/subsonic-mcp.json` | Subsonic/OpenSubsonic library ops MCP | subsonic.org / opensubsonic.netlify.app |
| `mcp/obsidian-mcp.json` | Obsidian Local REST API MCP bridge | github.com/coddingtonbear/obsidian-local-rest-api |

---

## Skill Count

| Category | Committed Standalone Trees | Ghost Specs (composite only) | Total Unique IDs |
|---|---|---|---|
| Meta / Reasoning | 0 | 6 | 6 |
| Coding | 0 | 5 | 5 |
| Obsidian (official + bespoke) | 4 | 5 | 9 |
| Homelab (behavior + action) | 15 | 0 | 15 |
| Media / Music / DJ | 13 | 0 | 13 |
| Social | 0 | 2 | 2 |
| MCP / Tool Bridge | 3 | 1 | 4 |
| **Total** | **35** | **19** | **54** |

> **35 skills have committed standalone `skills/<id>/SKILL.md` trees and are fully invocable.**
> The four project-exported control-plane and security skills were added on August 17, 2026.
> **19 skills have composite `.SKILL.md` specs only and must be migrated before they are invocable.**
> Skills are counted by unique skill IDs. MCP config files are not counted as skills.
> `filesystem-refactor-planner` remains composite (1 ghost in MCP / Tool Bridge category).

---

## Upstream Links

- Official Obsidian Skills: https://github.com/kepano/obsidian-skills
- claude-homelab (SKILL.md structure): https://github.com/jmagar/claude-homelab
- Slsk MCP: https://mcpmarket.com
- slskd-mcp: https://github.com/abl030/slskd-mcp
- slskd: https://github.com/slskd/slskd
- Subsonic API: https://subsonic.org/pages/api.jsp
- OpenSubsonic API: https://opensubsonic.netlify.app
- Proxmox VE: https://www.proxmox.com/en/proxmox-virtual-environment
- Obsidian Local REST API: https://github.com/coddingtonbear/obsidian-local-rest-api
