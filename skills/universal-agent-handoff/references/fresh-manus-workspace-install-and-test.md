# Fresh Manus Workspace: Install and Test Guide

This guide shows how to install the universal handoff skill in a new Manus workspace and verify it locally before using it for a real transfer.

## 1. Install the skill

Obtain the distributable Manus skill package or the complete skill directory. In the Manus interface, add the skill using the provided skill installation card generated from `SKILL.md`. If installing from a filesystem copy, place the complete directory at the workspace skill location and preserve its `scripts/`, `tests/`, `references/`, and `templates/` subdirectories.

The installed directory should contain at least:

```text
universal-agent-handoff/
├── SKILL.md
├── scripts/
├── tests/
├── references/
└── templates/
```

Do not install only `SKILL.md` if you intend to run the local tests; the bundled resources are part of the skill.

## 2. Run the focused tests

From the installed skill directory, run:

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

A healthy installation should report all tests passing, including malformed ZIP checks, masking-block behavior, temporary-copy masking, mock API-key coverage, token coverage, credential-assignment coverage, and private-key coverage.

## 3. Run the standard skill validation

From the parent directory containing the installed skill:

```bash
python /home/ubuntu/skills/skill-creator/scripts/quick_validate.py universal-agent-handoff
```

If the workspace does not provide that validator path, validate the YAML frontmatter manually and confirm that `SKILL.md` contains the required `name` and `description` fields. Record the limitation rather than claiming the standard validator ran.

## 4. Test a clean handoff repository

Use an existing handoff repository or create a temporary one from the repository structure template. Run the local wrapper:

```bash
python scripts/run_handoff_validation.py \
  --repository /path/to/universal-agent-handoff-repository \
  --output /path/to/universal-agent-handoff-repository.zip
```

The wrapper should run tests, scan for sensitive text, validate the repository, build a single-root ZIP, validate the ZIP, and check archive integrity. No remote CI run is required for this local installation test.

## 5. Test the receiving startup path

Use the receiver script with a new output directory:

```bash
python scripts/receive_handoff.py \
  /path/to/universal-agent-handoff-repository.zip \
  --output /path/to/received-handoff
```

Confirm that it reports `RECEIVING HANDOFF ACCEPTED`, then read `MANIFEST.md`, status, rules, decisions, checklist, and `HANDOFF_PROMPT.md` in that order. To test failure handling, run it against a deliberately corrupt copy and an existing output directory; both should return nonzero without overwriting or deleting the original handoff ZIP.

## 6. Test masking without exposing source data

Create a temporary text fixture containing mock credentials, not real credentials, and run:

```bash
python scripts/run_handoff_validation.py \
  --repository /path/to/test-repository \
  --output /path/to/masked-handoff.zip \
  --mask-sensitive
```

Verify that the ZIP contains redaction placeholders, that the original repository is unchanged, and that a second scan reports no remaining matches. Do not use live credentials as test fixtures.

## 7. Record the installation result

Record the workspace, Python version, commands run, test count, validation status, masking status, and any unavailable checks. The skill is ready for real handoff work only when the local tests and repository or ZIP validation pass, or when limitations are explicitly documented.
