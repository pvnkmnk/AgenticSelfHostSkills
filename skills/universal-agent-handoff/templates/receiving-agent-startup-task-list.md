# Receiving-Agent Startup Task List

Use this short task list immediately after the handoff ZIP has been safely unpacked and validated. It is intentionally limited to startup orientation; it is not a multi-agent coordination system.

## Required startup tasks

| Done | Task | Evidence or note |
|---|---|---|
| [ ] | Confirm the original ZIP is preserved and the output directory is new. | |
| [ ] | Run `scripts/receive_handoff.py` or confirm the sender-provided acceptance result. | |
| [ ] | Read `MANIFEST.md`. | |
| [ ] | Read `HANDOFF_PROMPT.md`. | |
| [ ] | Read the current status and project rules. | |
| [ ] | Read the decision log and incomplete-task/open-decision checklist when present. | |
| [ ] | Confirm the prompt, status, manifest, and next action agree. | |
| [ ] | Record missing files, contradictions, blockers, or `NEEDS CONFIRMATION` items. | |
| [ ] | Confirm no publishing, authentication, deletion, deployment, purchase, or other external side effect is authorized without approval. | |
| [ ] | Begin only the exact next action described by the handoff prompt. | |

## Startup result

- **Startup status:** `ACCEPTED` / `BLOCKED` / `NEEDS CONFIRMATION`
- **Exact next action:**
- **Missing or contradictory information:**
- **Required approval:**
- **Evidence written to:**

If startup is blocked, preserve the original ZIP and report the failure without silently repairing, overwriting, or deleting the received package.
