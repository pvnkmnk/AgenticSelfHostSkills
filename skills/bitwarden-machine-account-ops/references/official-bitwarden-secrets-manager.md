# Official Bitwarden Secrets Manager Reference

Use this reference before changing machine-account scope, access tokens, `bws` configuration, runtime injection, CI, or incident response. The live Bitwarden web vault and the installed `bws --help` and `bws --version` are the final authority for the organization and CLI version being operated.

## Authority and current facts

| Topic | Verified behavior | Operating consequence |
|---|---|---|
| Machine accounts | A machine account is a non-human identity scoped to a discrete secret set. Project permissions are **Can read** or **Can read, write**. Adding a person or group permits that principal to generate tokens and interact with the whole machine-account scope. [1] | Default to one machine account per trust boundary, read-only access, and a restricted membership list. Review membership at every token change. |
| Access tokens | A token belongs to one machine account, is displayed once, is not stored by Bitwarden, and cannot be retrieved later. Expiry defaults to Never. Revocation stops current machines from retrieving and decrypting secrets. [2] | Store the value only in an owner-only host-local credential mechanism or independent recovery system. Use an expiry unless Never is explicitly justified. Treat revocation as an outage-causing cutover. |
| CLI authentication | `BWS_ACCESS_TOKEN` authenticates the `bws` CLI as its machine account. The CLI also supports an inline access-token flag. [3] | Use a process-local environment boundary for `BWS_ACCESS_TOKEN`. Do not pass a token on a command line even though the CLI permits it. |
| `bws run` | `bws run` injects secrets into a child process. Bitwarden warns that untrusted commands may access those secrets and that certain environment variable names can create severe security consequences. [3] | Inject into one reviewed entrypoint only. Never run an arbitrary interactive shell, coding agent, plugin, unknown binary, or command substitution under `bws run`. |
| Scope reduction | `bws run --project-id` injects one project’s secrets. `--no-inherit-env` reduces inherited environment variables but does not create a sandbox. `--uuids-as-keynames` makes valid shell variable names from UUIDs. [3] | Prefer project restriction when possible. Do not mistake a reduced inherited environment for isolation. Use POSIX-compatible secret keys or UUID mapping. |
| CLI output and state | Secret commands output objects containing values by default. The CLI can output `env` format. Configuration is stored under `~/.config/bws/config`; encrypted state can be stored under `~/.config/bws/state`. [3] | Avoid secret read/list commands in routine validation. Keep configuration and state owner-only, untracked, and reviewed in compromise response. |
| Containers | Bitwarden demonstrates runtime retrieval from a host or container entrypoint. [4] | Do not copy its functional examples into a high-assurance control plane without removing token-bearing command lines, logging, and image/build exposure. Retrieve only at runtime in one reviewed entrypoint. |
| GitHub Actions | The Bitwarden action injects selected secrets as masked environment variables; its machine account needs access to those secret IDs. [5] | Create a dedicated CI machine account/token, pin the action, request only necessary IDs, and prohibit untrusted code, artifacts, or debug output after injection. |
| Event evidence | Machine-account event logs include secret-access and identity-change events; logs are retained and exportable. [1] | Preserve relevant non-secret event references before deleting/revoking an identity during incident response. Do not export secret values into the incident record. |

## Version-sensitive and vendor-example cautions

Bitwarden documents capabilities that are technically available but unsuitable for this project’s hardened control plane. The `--access-token` flag, direct `bws secret get`, `--output env`, `echo` demonstrations, and `docker run -e` patterns can expose values through process metadata, shell history, logs, or diagnostics. This skill therefore intentionally prohibits them for operational workflows even when official documents show them as functional examples.

Machine-account write access is also version-sensitive. Bitwarden documents UI permissions for write behavior and notes that full write functionality depends on CLI release support. Record `bws --version`, confirm the installed command’s `--help`, and do not assume a write operation exists or behaves the same across versions. [1] [3]

## Inspection-only evidence collection

The following checks are allowed only after an access token has been delivered through an already approved host-local mechanism and the output has been confirmed non-secret. Do not run these checks from a generic agent shell or capture their full output in task logs.

| Goal | Safe pattern | Avoid |
|---|---|---|
| Record the client version | `bws --version` | Installing an unpinned binary or copying configuration from another host. |
| Confirm command syntax | `bws run --help` or `bws secret --help` | A command that retrieves or lists secret objects. |
| Validate application integration | A trusted service health endpoint that does not return credentials | `echo`, `printenv`, Docker inspect, or debug logging. |
| Investigate suspected exposure | Machine-account event-log reference and affected service logs with value redaction | Exporting secret content, rendered environments, or raw token values. |

## References

[1]: https://bitwarden.com/help/machine-accounts/ "Bitwarden Machine Accounts"
[2]: https://bitwarden.com/help/access-tokens/ "Bitwarden Access Tokens"
[3]: https://bitwarden.com/help/secrets-manager-cli/ "Bitwarden Secrets Manager CLI"
[4]: https://bitwarden.com/help/developer-quick-start/ "Bitwarden Developer Quick Start"
[5]: https://bitwarden.com/help/github-actions-integration/ "Bitwarden GitHub Actions Integration"
