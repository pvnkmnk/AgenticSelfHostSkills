# Official and Community Source Map

## Authority order

1. **Installed Proxmox VE 9 host and UI/API.** Use the live system to confirm current version, configuration, storage, network, and task behavior.
2. **Official Proxmox VE Administration Guide.** Use for platform capabilities, backup/restore, networking, storage, cluster behavior, permissions, and node administration.
3. **Official Proxmox wiki reference pages.** Use the Linux Container, Storage, Backup and Restore, Package Repositories, and version-specific Upgrade pages for operational detail.
4. **Built-in command documentation.** Use `man pct`, `man qm`, `man pvesm`, `man vzdump`, `pvesh usage`, and `--help` against the installed version.
5. **Official Proxmox forum.** Use moderated staff/community discussion for troubleshooting and operational context; cross-check advice against the installed version and official documentation.
6. **Community Scripts project.** Use for service discovery, defaults, and implementation examples; inspect before execution and treat it as untrusted third-party automation.

## Current reference URLs

| Topic | Preferred source |
|---|---|
| Administration and API | `https://pve.proxmox.com/pve-docs/pve-admin-guide.html` |
| Linux containers | `https://pve.proxmox.com/wiki/Linux_Container` |
| Storage | `https://pve.proxmox.com/wiki/Storage` |
| Proxmox VE 8 to 9 upgrade | `https://pve.proxmox.com/wiki/Upgrade_from_8_to_9` |
| Official forum | `https://forum.proxmox.com/` |
| Community Scripts source | `https://github.com/community-scripts/ProxmoxVE` |
| Community Scripts documentation | `https://github.com/community-scripts/ProxmoxVE/wiki` |

## Community-script review gate

Before use, verify the repository owner, branch or pinned revision, stated Proxmox version support, host/root privileges, downloads, package repositories, network changes, guest ID/storage defaults, runtime features, post-install helper behavior, update method, backups, and rollback. Prefer creating a fresh disposable guest and advanced configuration mode. Record the reviewed source URL and commit/release identity where available.

Do not execute a pasted `curl | bash`, `wget | bash`, or equivalent remote pipeline without reviewing the retrieved script first. Do not use helper scripts to bypass the project’s approval gate, backup plan, or configuration management.
