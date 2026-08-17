# Receiving-Agent Quick-Start Checklist

Use this checklist immediately after receiving a handoff ZIP. Treat verification as a startup gate: do not begin project work until the package is accepted.

## Intake and preservation

- [ ] Confirm the ZIP path and preserve the original file unchanged.
- [ ] Choose a new output directory; do not overwrite an existing workspace automatically.
- [ ] Confirm that the handoff came from an expected sender or channel.

## Safe unpack and validation

- [ ] Run the packaged receiver script:

  ```bash
  python 06-skills/universal-agent-handoff/scripts/receive_handoff.py \
    /path/to/universal-agent-handoff-repository.zip \
    --output /path/to/received-handoff
  ```

- [ ] Confirm that the script reports `RECEIVING HANDOFF ACCEPTED`.
- [ ] If it fails, preserve the original ZIP, record the failure, and request a corrected package. Do not silently repair or overwrite files.
- [ ] Confirm that exactly one top-level repository directory was extracted.
- [ ] Confirm that the repository validator passed.

## Read-first orientation

- [ ] Read `MANIFEST.md` and confirm that referenced files exist.
- [ ] Read the current status file and identify the exact next action.
- [ ] Read project rules, the decision log, and the incomplete-task/open-decision checklist.
- [ ] Read `HANDOFF_PROMPT.md` and compare its current state with the repository.
- [ ] Inspect any included custom skills before applying them.

## Execution readiness

- [ ] Record any `UNKNOWN`, `NEEDS CONFIRMATION`, blocker, missing dependency, or contradiction.
- [ ] Confirm which actions are safe to perform without approval.
- [ ] Confirm which actions require approval, credentials, publication, deployment, deletion, or other external side effects.
- [ ] Perform the exact next action only after the repository and prompt agree.
- [ ] Update status, checklist, decisions, and evidence paths before handing work onward.
