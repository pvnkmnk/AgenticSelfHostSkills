# Bitwarden Secret or Access-Token Rotation Record

> **Non-secret document.** Record metadata, timestamps, approvals, and value-redacted evidence only. Do not include a token value, secret value, rendered environment, private key, or credential-bearing URL.

| Field | Value |
|---|---|
| Record ID | `<non-secret identifier>` |
| Date and time (UTC) | `<timestamp>` |
| Change type | `<scheduled rotation, expiry replacement, compromise, retirement, clone, other>` |
| Project name and ID | `<non-secret identifier>` |
| Machine account name and ID | `<non-secret identifier>` |
| Affected consumer | `<host, guest, service, or workflow>` |
| Integration mode | `<CLI runtime injection or SDK direct integration>` |
| CLI release/profile or SDK package/version | `<non-secret selected version and profile/wrapper>` |
| CLI/SDK state-file handling | `<owner-only location/retention/removal decision>` |
| Affected credential class | `<access token or secret key name/ID; no value>` |
| Current token expiry / secret review date | `<date or NONE>` |
| Replacement scope reviewed | `<project IDs, access level, membership review, owner>` |
| Replacement expiry / next review | `<date or approved Never justification reference>` |
| Change approval | `<approver, exact approved scope, timestamp>` |
| Trusted delivery boundary | `<owner-only mechanism / protected CI secret / wrapper>` |
| Trusted entrypoint and version/digest | `<path, action revision, or image digest>` |
| Replacement validation | `<pass/fail; health or metadata check only; no values>` |
| Affected service/workflow health | `<pass/fail and value-redacted evidence link>` |
| Machine-account event evidence | `<event-log reference/date range; no exported secret values>` |
| Old credential revoked/retired | `<yes/no/pending and timestamp>` |
| Obsolete runtime state removed | `<yes/no/not applicable>` |
| Incident containment completed | `<yes/no/not applicable>` |
| Operator | `<person/agent>` |
| Independent recovery test | `<pass/fail/date or scheduled date>` |
| Next review date | `<date>` |

## Cutover attestation

- [ ] A replacement was created with the approved least-privilege scope before the old credential was revoked.
- [ ] The replacement was delivered without a command-line argument, rendered environment file, transcript, or log disclosure.
- [ ] The trusted consumer and its health check passed without retrieving, listing, or printing secret values.
- [ ] The CLI release/profile or SDK wrapper/version/state-file transition was reviewed and captured non-secretly.
- [ ] The old credential was revoked only after the replacement path was known good.
- [ ] Relevant non-secret event evidence and value-redacted service evidence were recorded before destructive identity cleanup.
- [ ] Any credential-bearing local state, temporary material, or obsolete client identity was removed or explicitly retained with justification.
- [ ] If this was a suspected exposure, containment and the disposable recovery test were completed or a scheduled exception is recorded.
