# AGE-11 Homelab-Agent Change-Control Matrix

**Status:** Accepted governance contract on 2026-08-17.  
**Applies to:** `Homelab-Agents`, reusable behavior in `AgenticSelfHostSkills`, any future agent connected to homelab control planes, and any tool path that could reach guests, services, storage, networks, secrets, or media.  
**Purpose:** Keep the homelab laboratory useful for research and planning without granting it implicit authority over valuable personal infrastructure.

> A system’s ability to inspect a terminal, write a Compose file, install a service, generate a skill, or retain a maintenance recipe is not permission to act on the homelab. Current policy is **read first, propose second, execute only an exact approved subset, and never auto-expand scope**.

## 1. Authority and protected boundaries

| Concern | Canonical authority | Agent boundary |
|---|---|---|
| Declared supported topology and recovery documentation | `homelab-proxmox-ansible` | Agents may review and propose documentation changes; no deployment command is implied. |
| Reusable safety behavior | `AgenticSelfHostSkills` | Agents may load validated skills and use them to classify a request; skills do not grant credentials or write authority. |
| Homelab-agent laboratory code | `Homelab-Agents` | Treat as research/disposable until a separately approved integration scope exists. |
| Existing Navidrome service on CT 100 | Protected legacy workload | Never stop, modify, migrate, resize, delete, or adopt automatically. Every action requires a separate explicit approval. |
| CT 101 `homelab-core` | Empty approved service boundary | No service, media, secret, autostart, Tailscale, network, or storage change without a new exact approval. |
| Secrets and machine identities | Approved secret manager and host-local recovery process | Never print, copy, store, infer, or rotate values. Activation is a separate approved action. |
| Personal media and private knowledge | Their canonical music/vault owners | Do not mount, index, transfer, or expose them through an agent laboratory. |

## 2. Capability matrix

| Action class | Examples | Default policy | Minimum condition |
|---|---|---|---|
| Offline research and documentation | Read repository files, compare docs, draft diagrams, validate fictional fixtures | **Allowed** | No connection to a live service, secret, personal media path, or private vault |
| Local disposable validation | Lint documentation, test a synthetic manifest, run a fixture-only checker, build an isolated local image without deployment | **Allowed when isolated** | Temporary or disposable data only; no host mount, credential, network enrollment, or live endpoint |
| Live read-only discovery | View authorized service topology, inventory, logs, storage facts, or private-access posture | **Propose and execute only within the user-approved read-only scope** | Target and questions named; output redacted; no writes, downloads, secrets, or configuration export |
| Change-plan drafting | Compose/Terraform/Ansible diff, service-placement design, rollback plan, approval packet | **Allowed as a proposal** | Clearly label as unexecuted; name assumptions, protected resources, recovery requirement, and exclusions |
| State-changing infrastructure work | Create/alter guests, deploy/restart services, modify storage, mounts, network, DNS, firewall, Tailscale, or monitoring | **Never automatic** | Exact owner approval naming target, parameters, data placement, rollback, validation, and protected-resource exclusions |
| Secrets and identity work | Create/revoke credentials, bind machine identity, inject environment, rotate token | **Never automatic** | Separate exact approval and a non-secret validation plan; values stay outside Git, prompts, logs, and Linear |
| Media or knowledge data work | Import, sync, index, tag, move, delete, mount, export, or migrate personal content | **Never automatic** | The applicable music or private-knowledge contract plus exact owner approval |
| Public exposure | Router forwarding, public tunnel, Tailscale Serve/Funnel, public DNS, reverse-proxy exposure | **Prohibited** | No exception is implied by this contract; a future policy change would require a distinct owner decision |

## 3. Controls for `Homelab-Agents`

`Homelab-Agents` documents a ServiceOps system capable of writing Compose files, invoking terminal tools, installing services, polling endpoints, and persisting generated maintenance knowledge. Those capabilities are categorised as **laboratory-only** for this portfolio.

The laboratory may be used to reason about a proposed service or generate a non-executed plan. It must not register terminal tools against the live homelab, submit live shell commands, write a service configuration on a homelab target, register a persistent service skill from observed production data, or treat a chat request as approval to deploy.

If a future owner-approved disposable environment is established, the laboratory may execute only the named experiment after the approval records its target, isolation boundary, maximum resource/data scope, disposal method, expected outputs, and no-contact guarantee for CT 100, CT 101, personal media, and secrets. Results must be redacted into a non-secret record.

## 4. Required decision sequence for a live proposal

1. Classify the request as read-only discovery, reversible configuration, data/service change, credential/access change, or destructive operation.
2. Name the canonical authority, target resource, affected data, and protected resources before selecting an implementation path.
3. Collect the smallest safe read-only evidence set. Treat unknown state or recovery gaps as blockers.
4. Prepare a bounded proposal with a reviewed diff or manifest, prerequisites, rollback method, validation steps, and explicit exclusions.
5. Obtain a new owner approval that names the exact parameters and confirms that the protected resources are excluded.
6. Reconfirm volatile facts immediately before execution, then perform only the approved subset.
7. Record non-secret pass/fail evidence, scope, and follow-up gates in the canonical repository and Linear. Do not retain raw environment exports, addresses, credentials, media listings, or private content.

## 5. Hard stops

Stop and request guidance when the target is ambiguous; a command would reach more than the approved resource; recovery evidence is absent; output contains a secret or private data; a change could affect CT 100; a service would become externally reachable; an agent asks to create persistent credentials; or a generated plan attempts to broaden itself from one approved action into a general management capability.

## 6. Relationship to reusable skills

This matrix is the repository-specific policy layer. It uses `homelab-safe-ops` for standing read-first and no-destroy behavior, `homelab-change-control` to determine whether a request is ready for a plan, and `proxmox-service-guest-gate` only for a separately approved guest operation. If guidance conflicts, the narrower safety boundary and the owner’s exact approval prevail.
