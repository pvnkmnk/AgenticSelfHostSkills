# Incomplete Tasks and Open Decisions Checklist

Use this file to track work that is not finished and choices that still require resolution. Keep one copy at the handoff repository root or in `02-status/`, and update it before transferring work onward.

## How to use this checklist

Use one row per task or decision. Do not mark an item complete until the evidence path, test result, approval, or explicit resolution is recorded. Use `UNKNOWN` when information is unavailable and `NEEDS CONFIRMATION` when a person or authorized agent must decide.

## Incomplete tasks

| ID | Task or deliverable | Status | Priority | Owner | Dependencies or blocker | Next concrete action | Evidence or target path | Acceptance criterion | Review date |
|---|---|---|---|---|---|---|---|---|---|
| T-001 | <unfinished task> | `NOT STARTED` / `IN PROGRESS` / `BLOCKED` / `READY FOR REVIEW` | `<high/medium/low>` | `<person/agent>` | `<dependency or NONE>` | `<smallest next action>` | `<relative path or UNKNOWN>` | `<observable done condition>` | `<date or NONE>` |

### Task completion checks

- [ ] The owner and next concrete action are recorded.
- [ ] Dependencies and blockers are explicit rather than implied.
- [ ] The acceptance criterion is observable and testable.
- [ ] Evidence is linked by relative path, or the missing evidence is marked `UNKNOWN`.
- [ ] Completed work has been reflected in `02-status/current-status.md`.

## Open decisions

| ID | Decision required | Status | Decision owner | Options considered | Recommendation or default | Impact if delayed | Required evidence | Due or review date |
|---|---|---|---|---|---|---|---|---|
| D-001 | <decision to make> | `OPEN` / `NEEDS CONFIRMATION` / `DECIDED` / `DEFERRED` | `<person/agent>` | `<option A; option B>` | `<recommendation or NONE>` | `<impact>` | `<research, test, approval, or UNKNOWN>` | `<date or NONE>` |

### Decision completion checks

- [ ] The decision owner is identified.
- [ ] Material options and trade-offs are recorded.
- [ ] A default or recommendation is distinguished from an approved decision.
- [ ] The impact of delay is stated.
- [ ] A decided item has been copied into `03-decisions/decision-log.md` with rationale.

## Handoff readiness review

- [ ] No incomplete task is described as completed elsewhere in the repository.
- [ ] No open decision is hidden inside an assumption or prose-only note.
- [ ] Blocked tasks include a safe workaround or explicit escalation path.
- [ ] External side effects, authentication, publication, deletion, purchase, or deployment decisions require appropriate confirmation.
- [ ] This checklist is referenced by `MANIFEST.md` and the paste-ready handoff prompt when relevant.
