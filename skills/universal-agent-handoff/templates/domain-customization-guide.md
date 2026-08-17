# Domain Customization Guide

Use this guide to adapt the universal handoff package without weakening its portability, truthfulness, or safety rules. Customize the vocabulary, evidence requirements, acceptance criteria, and repository sections for the project domain, while preserving the separation between the paste-ready prompt and durable repository context.

## Customization sequence

1. **Name the domain and recipient.** State whether the handoff is for software engineering, research, content, design, operations, finance, or another domain, and identify what the receiving agent is expected to do.
2. **Define domain-specific done criteria.** Replace generic completion language with observable checks such as passing tests, approved citations, rendered assets, signed-off copy, reconciled numbers, or a completed runbook.
3. **Extend the repository selectively.** Add domain folders only when they contain durable guidance. For example, software projects may add `09-engineering/`; research projects may add `09-sources/`; content projects may add `09-editorial/`.
4. **Preserve certainty markers.** Keep `FACT`, `DECISION`, `ASSUMPTION`, `UNKNOWN`, and `NEEDS CONFIRMATION`. Domain terminology may be added, but it must not replace these markers.
5. **Adapt the checklist.** Add columns for domain-specific ownership, evidence, review, or risk. Keep the incomplete-task and open-decision sections separate.
6. **Define side-effect gates.** State which actions require confirmation, such as deployment, publication, external communication, financial transfer, deletion, or submission.
7. **Update the manifest.** Record every added template, guide, custom skill, workflow, and artifact with purpose, status, provenance, sensitivity, and resume relevance.

## Domain adaptation examples

| Domain | Add to the prompt | Add to the repository | Typical verification |
|---|---|---|---|
| Software engineering | branch, runtime, test command, deployment gate, migration risk | architecture notes, API contracts, test output, migration plan | automated tests, lint, build, review |
| Research | research question, source standard, date boundary, citation style | source ledger, extraction notes, methodology, limitations | citation audit, reproducibility check |
| Content and SEO | audience, search intent, tone, claims policy, approval stage | brief, keyword map, fact sheet, editorial checklist | fact check, originality review, editorial approval |
| Design and media | target format, dimensions, brand constraints, source assets | design rationale, asset inventory, export specs, review notes | visual inspection, format validation, stakeholder approval |
| Operations | service scope, maintenance window, rollback condition, escalation path | runbook, environment notes, incident history, change record | dry run, health check, rollback rehearsal |
| Finance or analysis | period, currency, source hierarchy, modeling convention, review authority | source files, assumptions, calculation notes, review log | tie-out, formula check, independent review |

## Customizing the prompt safely

Keep the opening ownership instruction, objective, definition of done, current state, repository map, constraints, decisions, open questions, first-session checklist, verification, and handoff-back instruction. Replace placeholders with domain facts and add only the minimum domain-specific detail needed to execute safely.

Use relative paths for all package references. Do not embed credentials, private links that the recipient cannot access, or unsupported claims. If a domain requires a specialized tool, describe the expected output and provide a fallback inspection method rather than assuming that the receiving agent has the same integration.

## Customizing the templates

The prompt template can gain domain headings, but its required order should remain stable. The repository structure can gain numbered sections, but existing sections should not be renamed unless every prompt and manifest reference is updated. The checklist can add fields such as `risk`, `reviewer`, `source`, `test case`, or `rollback`, but each row must still identify an owner, next action or resolution method, evidence, and acceptance condition.

## Customization review

Before distributing a domain-specific package, ask whether a receiving agent unfamiliar with the domain can identify the first safe action, the authoritative rules, the evidence required for completion, the decisions it may make independently, and the actions requiring confirmation. Run the ZIP validator after adding any required file to ensure the package contract still holds.
