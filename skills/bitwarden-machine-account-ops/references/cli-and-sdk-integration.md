# `bws` CLI and SDK Integration Reference

Use this reference before adding a `bws` command, setting a CLI profile/state path, selecting a shell, or adding a Bitwarden Secrets Manager SDK dependency. It is **CLI-first**: use `bws run` for one reviewed service entrypoint. Use an SDK only when an application must make programmatic Secrets Manager operations that cannot be safely expressed as an injected runtime.

## 1. Current CLI command rules

The official CLI reference identifies `bws secret list` as the current post-0.3.0 command family and explicitly advises checking `bws --version` because older syntax remains temporarily supported. The package’s current release listing included `bws CLI v2.1.0` when reviewed on 2026-08-17; pin a selected release for each deployment and verify it locally rather than assuming every host matches that release. [1] [2]

| Objective | Current documented form | Hardened operating rule |
|---|---|---|
| Identify installed CLI | `bws --version` | Safe preflight; record the result in the non-secret contract. |
| Inspect command grammar | `bws --help`, `bws run --help`, `bws secret --help` | Safe preflight; do not use a tokened secret command merely to test availability. |
| Limit injected scope | `bws run --project-id <project-id> -- <command>` | Use only when the reviewed entrypoint needs exactly one project. |
| Reduce inherited variables | `bws run --no-inherit-env -- <command>` | Prefer it unless an exception is documented. It does not sandbox the process; `PATH` and shell-created variables may remain. [1] |
| Select shell | `bws run --shell <shell> -- <command>` | Do not change shells casually. The documented defaults are `sh` on Linux/macOS and PowerShell on Windows. Never select an interactive shell as the injection target. [1] |
| Map non-POSIX names | `bws run --uuids-as-keynames -- <command>` | Prefer POSIX-compliant secret names. Use UUID mapping only when a reviewed entrypoint maps the required values safely. [1] |
| Set CLI server profile | `bws config server-base <https-url> --profile <name>` | Use only for the approved Bitwarden region/self-hosted endpoint; keep profiles host-local and owner-only. [1] |
| Set custom state location | `bws config state-dir <absolute-path>` | Use an absolute, owner-only path. The state directory contains encrypted state files that store authentication tokens and other relevant data. [1] |

The following is the approved runtime **shape**. It is not a credential-delivery command: `BWS_ACCESS_TOKEN` must already be supplied only to the `bws` process through the approved host-local mechanism. Review the final executable and all of its dependencies before execution.

```bash
bws run --project-id <approved-project-id> --no-inherit-env -- \
  /usr/local/libexec/<approved-service-entrypoint>
```

Bitwarden documents `BWS_ACCESS_TOKEN` as the CLI authentication environment variable and also supports a per-command `--access-token` flag. The latter is intentionally prohibited by this skill because command lines, shell history, CI job definitions, and process inspection can expose its value. [1]

## 2. Output, state, profile, and rate-limit safety

`bws secret get` and `bws secret list` return secret objects by default; the CLI also offers formats including `env`, which emits `KEY=VALUE`. These are functional commands, not safe routine validation actions. Do not print, redirect, capture, diff, serialize, attach, or upload their output in an agent, shell, CI, or service context. [1]

The default configuration path is `~/.config/bws/config`; the default state directory is `~/.config/bws/state`. State files are fully encrypted, but remain sensitive host-local authentication state. Keep the configuration, profiles, and state directory owner-only and out of Git, synchronization folders, images, snapshots, and recovery artifacts. `state_opt_out` can disable state-file use, but it may increase authentication frequency and make rate limiting more likely. [1]

> **Do not infer a secret-safe dry run.** The official reference documents no non-disclosing secret-access validation mode. Use `bws --version`, command help, completed static contract validation, and a reviewed consumer health check; never treat secret retrieval output as a safe connectivity probe.

High-frequency separate sessions from one IP can be rate-limited. Reuse one controlled runtime boundary where appropriate, avoid a retry storm, and define explicit backoff in the consumer if it makes many authenticated calls. [1]

## 3. SDK exception gate

The official Secrets Manager SDK uses a Rust core with published wrappers for C++, C#, Go, Java, JavaScript, PHP, Python, and Ruby. The SDK repository describes generated JSON schemas from Rust structs via `schemars`; QuickType uses them to generate bindings, and language wrappers use a JSON `run_command` boundary. **Do not hand-write, copy, or freeze generated SDK schema definitions in this skill.** Select the official wrapper version and its release-specific API reference instead. [3] [4]

| SDK decision | Required control | Reject when |
|---|---|---|
| Need direct programmatic Secrets Manager operations | Pin the language package and version; name the exact official release/API reference in the contract; use the narrowest typed method and retain no secret object beyond its need | The goal is merely to inject variables into one service process; use `bws run` instead. |
| Authenticate SDK client | Deliver the access token through a process-local owner-only boundary; keep SDK token handling in the reviewed application edge | The token would live in source code, config, an image, a command line, an application-wide environment, or a telemetry context. |
| Configure SDK state | Record the required absolute state-file path, ownership, backup/retention decision, and removal plan | The SDK/state file is shared across environments, users, or ephemeral build artifacts. |
| Handle SDK return values and errors | Redact logs, traces, exceptions, metrics, and support bundles; return only narrowly needed values inside the process | The application prints, serializes, caches, or forwards secret objects/values. |
| Generate bindings/schemas | Consume an official version-pinned binding or generate from the official SDK process | A project proposes an ad-hoc JSON schema, a copied main-branch type, or a schema guess. |

The released Python v2.1.0 repository example is a **development example**, not an operations template. It enables debug logging, prints generated values, uses local HTTP defaults, performs project/secret create-update-delete operations, and uses interactive cleanup. It demonstrates public SDK shape only; do not copy it into a host, service, agent, or CI runtime. [5]

## 4. SDK and CLI non-disclosure review

Before approving a CLI or SDK integration, verify the contract records these non-secret facts: machine account and project identifiers; access level; token expiry/review; integration mode; selected CLI or language-wrapper version; owner-only config/state boundary; trusted entrypoint; logging/telemetry redaction review; typed operation or project-scope boundary; health check; and independent recovery path.

The offline `validate_secret_contract.py` validator checks only contract metadata. It does not inspect source code, prove redaction, authenticate to Bitwarden, or validate a token. Use application code review and a non-disclosing health test to supply those separate assurances.

## References

[1]: https://bitwarden.com/help/secrets-manager-cli/ "Bitwarden Secrets Manager CLI"
[2]: https://github.com/bitwarden/sdk-sm/releases "Bitwarden Secrets Manager SDK releases"
[3]: https://bitwarden.com/help/secrets-manager-sdk/ "Bitwarden Secrets Manager SDK"
[4]: https://github.com/bitwarden/sdk-sm "Bitwarden Secrets Manager SDK repository"
[5]: https://github.com/bitwarden/sdk-sm/blob/python-v2.1.0/languages/python/example.py "Bitwarden Python SDK v2.1.0 example"
