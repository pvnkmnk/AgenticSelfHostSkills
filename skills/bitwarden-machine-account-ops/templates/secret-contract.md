# Bitwarden Secrets Manager Contract

> **Non-secret document.** Do not enter an access-token value, secret value, rendered environment content, private key, or credential-bearing URL in this file. Complete every required field before requesting approval to create or change Bitwarden state.

| Field | Value |
|---|---|
| Trust boundary | `<for example: WSL deployment, Proxmox guest, Windows interactive, or CI>` |
| Environment | `<development, homelab-production, recovery, CI, other>` |
| Project name and ID | `<non-secret identifier>` |
| Machine account name and ID | `<non-secret identifier>` |
| Machine-account members/groups reviewed | `<names or group labels; date reviewed>` |
| Consumer host, guest, service, or workflow | `<non-secret name>` |
| Access level | `Can read` by default; write access requires the approved justification below |
| Write-access justification and approval | `<NONE or explicit capability need, approver, date>` |
| Project purpose | `<purpose>` |
| Required secret keys or IDs | `<at least one key name or opaque ID; never a value, N/A, or NONE>` |
| Human owner and recovery owner | `<person or team>` |
| Token expiry and next review | `<date/cadence; Never requires justification>` |
| Never-expiry justification | `<NONE or approved operational reason>` |
| Host-local token location | `<path or mechanism description only; never the token>` |
| `bws` config/state boundary | `<owner-only location/profile description>` |
| Integration mode | `<CLI runtime injection or SDK direct integration>` |
| `bws` version and selected release | `<output of bws --version / approved release; no token>` |
| CLI profile and state-file decision | `<profile and owner-only state directory/files, or N/A>` |
| SDK language, package, version, and API reference | `<official release-specific reference, or N/A for CLI mode>` |
| SDK state-file decision | `<owner-only absolute path / retention plan, or N/A for CLI mode>` |
| SDK allowed operations and redaction review | `<typed operation scope; logging/telemetry/error review, or N/A for CLI mode>` |
| Runtime project scope | `<project ID used with bws run, or documented reason not applicable>` |
| Trusted runtime entrypoint | `<absolute path, immutable image digest, or pinned action revision>` |
| Runtime command review | `<arguments, working directory, dependencies, logging review>` |
| Inherited-environment decision | `<use --no-inherit-env or documented exception>` |
| Key-name strategy | `<POSIX keys or --uuids-as-keynames mapping>` |
| Non-secret validation | `<health check or metadata-only validation>` |
| Service restart/control path | `<stable command or control-plane action; no credentials>` |
| Event-evidence location | `<machine-account event reference / value-redacted log location>` |
| Independent recovery location | `<description only>` |

## Safety review

- [ ] No token, secret value, rendered environment, private key, or credential-bearing URL appears in this document.
- [ ] The machine account has only the required project access, lists at least one required secret key/ID, and only approved people/groups can generate its tokens.
- [ ] Write access is `NONE` or has a documented, approved, version-checked capability need.
- [ ] The token has a finite expiry, or the Never-expiry justification and review date are approved.
- [ ] The runtime entrypoint, arguments, dependencies, working directory, selected shell, and logging behavior have been reviewed because it receives injected values.
- [ ] CLI mode records the selected release/profile/state-file decision; SDK mode records the official wrapper, exact version, state-file handling, typed operations, and redaction review.
- [ ] The injection boundary is not an arbitrary agent shell, installer, package manager, Compose command, or untrusted script.
- [ ] The design does not place credentials in Git, shell profiles, command lines, service definitions, Docker/Compose metadata, image layers, transcripts, artifacts, or logs.
- [ ] Validation does not retrieve/list/print secret objects or environments.
- [ ] Rotation, compromise, and recovery owners are explicit.
