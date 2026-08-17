# Handoff Schema

Use this schema to gather and audit a handoff. The labels are deliberately explicit so that a receiving agent can distinguish established facts from provisional context.

| Field | Required | Guidance |
|---|---:|---|
| `handoff_id` | Yes | Stable human-readable identifier and date. |
| `objective` | Yes | One measurable statement of the intended outcome. |
| `definition_of_done` | Yes | Observable completion criteria, including tests or approvals. |
| `current_phase` | Yes | Where the work is now, not where it began. |
| `completed_work` | Yes | Verified accomplishments with paths or evidence. |
| `next_action` | Yes | The smallest concrete action the recipient should take first. |
| `repository_root` | Yes | Relative root of the packaged handoff repository. |
| `constraints` | Yes | Time, scope, platform, security, budget, policy, or format limits. |
| `decisions` | Yes | Durable choices, rationale, and decision status. |
| `assumptions` | Yes | Provisional statements that may affect execution. |
| `open_questions` | Yes | Unresolved questions, owner, deadline, and resolution method. |
| `blockers` | Yes | Anything preventing progress, with workaround if available. |
| `artifacts` | Yes | Important files, URLs, outputs, and their purpose. |
| `skills` | No | Custom skills included in `06-skills/`, with loading guidance. |
| `verification` | Yes | Checks that prove the next work is correct. |
| `side_effects` | Yes | Actions requiring confirmation, authorization, or credentials. |
| `security_notes` | Yes | Redactions, omitted files, and safe access instructions. |
| `handoff_back` | Yes | What the next agent must update before transferring onward. |

## Certainty markers

Use `FACT` only for information supported by the current work or an identified source. Use `DECISION` for an intentional choice that should persist. Use `ASSUMPTION` for a working belief. Use `UNKNOWN` where information is unavailable. Use `NEEDS CONFIRMATION` where the recipient must obtain approval before proceeding.

## Minimum evidence standard

Every claimed completed item should point to a file, command result, URL, test, or user-confirmed statement when practical. Every blocker should say how it was discovered. Every decision should record its rationale when a future agent might otherwise reverse it.
