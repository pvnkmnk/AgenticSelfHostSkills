# Two-Manus-Instance Walkthrough

This scenario demonstrates a safe transfer from **Manus A**, which has prepared a small web project, to **Manus B**, which must continue implementation without access to Manus A’s conversation.

## Scenario

Manus A has completed the project brief, selected the data model, created the initial application scaffold, and identified two unfinished tasks: adding input validation and writing the deployment notes. One open decision remains: whether the first release should use a hosted database or a local file-backed store. Manus A packages the current status, decision log, project rules, custom skills, the incomplete-task/open-decision checklist, and the relevant source artifacts.

## Manus A: prepare the handoff

Manus A copies the checklist template into `02-status/incomplete-tasks-open-decisions.md`, records the two unfinished tasks and the storage decision, updates `MANIFEST.md`, and writes a prompt whose immediate next action is to inspect the validation boundary before editing code. Manus A then runs:

```bash
python 06-skills/universal-agent-handoff/scripts/validate_handoff_zip.py universal-agent-handoff-repository.zip
```

The expected result is a passing validation message. Manus A sends Manus B the ZIP and the contents of `HANDOFF_PROMPT.md`, without including credentials or private browser state.

## Manus B: resume safely

Manus B extracts the ZIP, reads `MANIFEST.md`, `02-status/current-status.md`, `04-rules/project-rules.md`, the checklist, and the custom skill. Manus B verifies that the prompt’s immediate next action still matches the source artifacts. It then implements input validation, runs the project tests, and updates the task row with the evidence path and acceptance result.

Manus B does not choose a database architecture silently. It compares the recorded options, adds any new evidence to the open-decision row, and marks the decision `NEEDS CONFIRMATION` if authorization is required. It may continue with work that is independent of the storage choice, but it pauses before an irreversible migration or deployment.

## Manus B: hand back the work

Before returning the package, Manus B updates `02-status/current-status.md`, copies the resolved validation decision into `03-decisions/decision-log.md` if one was made, refreshes the checklist, updates the manifest, and revises `HANDOFF_PROMPT.md` with the new exact next action. Manus B rebuilds the ZIP and runs the validator again.

## Expected transfer record

| Stage | Owner | Evidence |
|---|---|---|
| Initial scaffold and project brief | Manus A | `07-artifacts/` and `01-context/project-brief.md` |
| Unfinished tasks and storage decision logged | Manus A | `02-status/incomplete-tasks-open-decisions.md` |
| Input validation implemented | Manus B | test output and updated status row |
| Storage choice resolved or escalated | Manus B and authorized owner | decision log or `NEEDS CONFIRMATION` row |
| Package returned for the next agent | Manus B | updated prompt, manifest, checklist, and passing ZIP validation |

## Lessons demonstrated

The prompt activates the receiving agent, but the repository preserves the details needed for trustworthy continuation. The checklist prevents unfinished work and unresolved decisions from disappearing into prose. The validator catches missing required documents before the package is handed over. Explicit confirmation gates prevent a receiving agent from turning an incomplete decision into an unintended external side effect.
