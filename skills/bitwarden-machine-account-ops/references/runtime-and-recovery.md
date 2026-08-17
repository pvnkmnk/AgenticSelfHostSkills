# Runtime, Rotation, Incident, and Recovery Gates

Use this reference after scope has been approved and before a machine-account token reaches a host, process, guest, container, service, or CI system. Read `official-bitwarden-secrets-manager.md` first for the product facts that support these stricter project controls.

## 1. Host-local credential boundary

An access token authenticates `bws`; it is not an application secret and it must not become broadly available to an application runtime. Store it in a host-local, owner-only credential mechanism outside the repository and outside any shared filesystem. Record only a descriptive location and recovery method in the contract.

| Consumer | Approved boundary | Explicitly prohibited |
|---|---|---|
| Windows interactive administration | A user-scoped, owner-only secret mechanism that provides a process-local variable only to the reviewed command | Windows environment variables persisted at user or machine scope, PowerShell history/transcripts, profiles, scheduled-task arguments, or repository files |
| Ubuntu WSL | An owner-only native-WSL location or process manager that exports `BWS_ACCESS_TOKEN` only for the reviewed invocation | `/mnt/c` synchronization, `~/.bashrc`, `~/.profile`, source-controlled `.env`, shell command lines, or agent-mounted paths |
| Proxmox guest | A guest-local, owner-only mechanism distinct from WSL and Windows | Host bind mounts, Proxmox notes, guest templates, image snapshots containing the token, or a shared token reused by another host |
| Container/service | An external runtime secret mechanism that exposes the token to one reviewed wrapper/entrypoint only | Dockerfile, image layer, build argument, `docker run -e`, Compose `environment:`, systemd `Environment=`, `ExecStart=`, logs, or inspectable metadata |
| CI | The CI platform’s encrypted secret store, limited to the protected workflow/environment | A developer/host token, workflow plaintext, reusable untrusted workflow, pull-request execution, artifacts, cache, or debug logs |

Keep the `bws` configuration and its state directory/encrypted state files owner-only. The documented defaults are `~/.config/bws/config` and `~/.config/bws/state`; a custom state directory must be an absolute path. Do not add configuration, profiles, encrypted state files, or server endpoints to a repository or cross-host synchronization workflow. Record the `bws` version, selected release, server profile, and state-file decision in non-secret inventory. During an exposure investigation, preserve only incident-relevant metadata and replace/remove runtime state after the replacement path is verified.

## 2. Runtime injection gate

Use `bws run` only around a reviewed, non-interactive entrypoint. The machine account should already be scope-limited; additionally use `--project-id` when one project supplies all required values. Use `--no-inherit-env` unless the consumer has a documented need for inherited variables, while recognizing that it does not sandbox a process, does not prevent file/network access, and can still leave `PATH` plus shell-created variables. The documented default shell is `sh` on Linux/macOS and PowerShell on Windows; any `--shell` override requires an explicit, version-tested review.

```bash
# Shape only. BWS_ACCESS_TOKEN must already be present in this process
# through an approved owner-only mechanism, and this entrypoint must be reviewed.
bws run --project-id <approved-project-id> --no-inherit-env -- \
  /usr/local/libexec/<approved-service-entrypoint>
```

For ordinary shell consumers, use POSIX-compatible secret keys: uppercase letters, digits, and underscores, beginning with a letter or underscore. If key names cannot be changed safely, use `--uuids-as-keynames` and map only the required UUID-style variables inside the reviewed entrypoint. Do not allow a secret name to control a shell command, option, file path, interpreter selection, `PATH`, loader variable, or executable lookup.

Do not use `bws run` to launch a generic interactive shell, an AI coding agent, a package manager, Docker Compose, an installer, or a script with unresolved dependencies. A child process can deliberately print or transmit every injected value. `--no-inherit-env` reduces collisions but is not a security boundary.

## 3. Non-disclosing validation

| Validation objective | Acceptable evidence | Disallowed evidence |
|---|---|---|
| Runtime contract | Completed static contract validation and a reviewed entrypoint path/digest | A rendered `.env`, `printenv`, shell trace, or copied environment |
| `bws` capability | `bws --version` and `--help` output, with no token or secret command | `bws secret get`, `bws secret list`, `--output env`, or secret JSON captured in logs |
| Service integration | Health endpoint, authenticated operation result, exit status, and value-redacted logs | Echoing a variable, verbose debug mode, error object containing values, Docker inspect, or CI artifact |
| Scope review | Web-vault project/membership record and non-secret IDs | Listing secret values to infer scope |

Never use `set -x`, `bash -x`, `Write-Verbose` with values, PowerShell `Start-Transcript`, debug CI logs, `docker inspect`, or process listings around a token or an injected runtime. Confirm that the entrypoint’s own logging redacts credential fields before enabling it in a service.

## 4. Container, service, SDK, and CI pattern

Build application images without the Bitwarden access token or application secrets. At runtime, a trusted wrapper may authenticate `bws`, inject only the approved project, and start the final process. The wrapper must not log the environment, invoke a shell with user-controlled input, or retain a rendered value file after startup. If an application cannot consume environment variables safely, use a narrowly permissioned temporary file with a documented deletion/rotation behavior and do not print its contents.

Use an SDK only when the application needs direct programmatic Secrets Manager operations that a reviewed `bws run` boundary cannot provide. Pin the official language binding and release-specific API documentation, configure its state file as owner-only local state, limit the method call and token scope, and prevent values from reaching logs, traces, metrics, exceptions, caches, telemetry, or support bundles. Do not paste a vendor SDK sample into a runtime: current released examples can enable debug logging, print values, use local endpoints, or create/delete resources.

For CI, create a separate read-only machine account and token per CI trust boundary. Pin `bitwarden/sm-action` to a reviewed release or immutable revision, request explicit secret IDs, and place the job in a protected environment. Do not inject secrets into workflows triggered by untrusted forks or pull requests. Do not forward injected values to artifacts, caches, child workflows, container builds, chat notifications, test snapshots, or debug logs.

## 5. Rotation and revocation sequence

1. Confirm the consumer, machine-account membership, project IDs, required keys, current token expiry, current `bws` version, trusted entrypoint, health check, and independent recovery path.
2. Create the replacement token or secret only after the exact scope, owner, expiry, and Bitwarden project are approved.
3. Deliver the replacement through the approved host-local mechanism without output. Validate the trusted consumer and health check without retrieving or printing a value.
4. Cut the affected consumer over through its stable service control path. Avoid broad restarts and avoid command lines that disclose credentials.
5. Confirm the health check, value-redacted logs, and expected non-secret event evidence.
6. Revoke the old token or retire the old secret only after the replacement is known good. Record the cutover in `templates/rotation-record.md`.
7. Remove obsolete local configuration, state, or temporary files as applicable, then schedule the next expiry/review date.

Revocation deliberately prevents affected machines from retrieving and decrypting secrets. Plan an overlap and a rollback path; do not revoke first and diagnose later.

## 6. Compromise and recovery sequence

1. **Contain.** Stop or isolate the suspected consumer and prohibit further automated runs using the affected token.
2. **Preserve non-secret evidence.** Record the machine-account event-log reference, timestamps, affected host/service, project/machine-account identifiers, and value-redacted service logs. Do not export token values, secret objects, or rendered environments.
3. **Replace.** Create a replacement with the exact approved least-privilege scope and a finite expiry where practicable.
4. **Validate.** Deliver it through the approved boundary, test the trusted consumer, and verify health without disclosure.
5. **Revoke and remove.** Revoke the compromised token. Remove affected runtime state and local client identity only after the replacement path works. Delete a machine account only when its incident record, secret ownership, and replacement/retirement plan are complete.
6. **Recover-test.** In a disposable workspace, VM, or guest snapshot, restore the repository and independent credential-recovery mechanism; install the pinned CLI; run static contract validation; validate a trusted consumer non-destructively; record pass/fail and timestamps; and destroy the test state.

