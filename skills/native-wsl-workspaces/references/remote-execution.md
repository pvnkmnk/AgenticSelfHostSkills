# Native WSL Workspace Routes

## Required path model

Treat these as distinct routes, even if they describe related files:

| Route | Use | Policy |
|---|---|---|
| Native WSL path, for example `/home/idols/LNXDevWorks/project` | Source of truth for a WSL-native repository | Required for all workspace reads, writes, validation, Git, and package actions |
| Windows path under `C:\…` or WSL `/mnt/c/…` | Windows-native files or a deliberate import/export source | Never use as the active source tree for WSL projects unless the user explicitly accepts the trade-off |
| UNC `\\wsl.localhost\<distro>\…` | Human-facing Windows Explorer access | Inspection/copy only; do not write through it while using WSL commands in the same session |
| Agent-mounted `/mnt/desktop/…` path | Tool-side transport surface | Never assume it is the authoritative or directly synchronized WSL filesystem |

## Safe operation sequence

1. Start the remote Windows shell from `C:\`, not a UNC working directory.
2. Invoke the exact distribution with `wsl.exe -d <distro> -- bash -lc …`.
3. Run `verify_wsl_workspace.sh <native-path> --probe-write` through that invocation.
4. For a small manual change, run a short noninteractive WSL command from `C:\` and verify it from the same native WSL shell.
5. For generated or large files, upload the artifact, record its SHA-256, and run `install_verified_url.sh` inside native WSL to download, verify, and atomically install it. Compare its reported WSL hash to the local source hash.
6. Run project commands only after the write/read/hash check passes.

## Prohibited patterns

Do not start a WSL command while the Windows shell current directory is `\\wsl.localhost\…`. Do not depend on Windows single-quote semantics to preserve a Bash script. Do not paste large heredocs into an interactive WSL session. Do not write project content through a mounted agent path and assume WSL sees it. Do not initialize Git, install packages, or deploy anything until the native workspace probe passes.

## Recovery after a route error

Stop the active command. Do not merge or overwrite files. Re-run the native workspace verifier. Compare the expected native path, the Windows path, and the agent-mounted path. If the workspace has split copies, declare one native WSL path authoritative, copy only after a verified hash comparison, and retain the other copy as a backup until the native repository passes its project tests.
