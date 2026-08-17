# Handoff Repository Structure

Use this layout as a contract. Include only sections that contain relevant material.

```text
handoff-repository/
├── HANDOFF_PROMPT.md
├── MANIFEST.md
├── 01-context/
│   ├── project-brief.md
│   └── glossary.md
├── 02-status/
│   ├── current-status.md
│   └── next-actions.md
├── 03-decisions/
│   └── decision-log.md
├── 04-rules/
│   ├── project-rules.md
│   └── acceptance-criteria.md
├── 05-workflows/
│   ├── bespoke-workflows.md
│   └── recovery-runbook.md
├── 06-skills/
│   └── <skill-name>/SKILL.md
├── 07-artifacts/
│   └── <artifact files>
└── 08-operations/
    └── operational-notes.md
```

## Manifest contract

`MANIFEST.md` must identify the handoff ID, creation date, source context, and intended recipient. Include a table with these columns: `Path`, `Type`, `Purpose`, `Status`, `Sensitivity`, `Source or provenance`, and `Required to resume?`. Use relative paths only.

## Packaging contract

The ZIP should contain one top-level repository directory. Exclude caches, build outputs that are not needed to resume, credentials, private keys, browser profiles, and unrelated personal data. Preserve custom skill directories instead of flattening them. The prompt must refer to paths exactly as they appear in the ZIP.
