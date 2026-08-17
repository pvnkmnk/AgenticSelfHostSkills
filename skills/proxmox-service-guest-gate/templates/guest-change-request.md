# Proxmox Guest Change Request

> **Approval required:** Creating the guest below allocates storage, creates a networked Proxmox resource, and may download a template. Do not execute until the user explicitly approves these exact values.

| Field | Proposed value | Confirmation required |
|---|---|---|
| Proxmox node | `<node>` | Yes |
| Guest ID | `<new unused ID>` | Yes |
| Hostname | `<hostname>` | Yes |
| Guest type | `<unprivileged LXC or VM>` | Yes |
| Template or image | `<template>` | Yes |
| vCPU | `<count>` | Yes |
| RAM and swap | `<values>` | Yes |
| Root disk | `<size and storage pool>` | Yes |
| Data disk | `<size and storage pool>` | Yes |
| Network bridge | `<bridge>` | Yes |
| Address strategy | `<DHCP reservation or static address>` | Yes |
| Runtime features | `<only required flags>` | Yes |
| Autostart | `<enabled after validation or disabled>` | Yes |
| First-service scope | `<services>` | Yes |
| Access scope | `<private LAN/private VPN>` | Yes |
| Backup destination | `<destination or NEEDS CONFIRMATION>` | Yes |
| Rollback boundary | `Destroy only this new guest after confirming no user data` | Yes |

## Evidence reviewed

- [ ] Current node, storage, bridge, templates, and next guest ID were confirmed read-only.
- [ ] Legacy or unrelated guests are explicitly out of scope.
- [ ] Resource headroom is acceptable.
- [ ] Data placement and backup gate are understood.

## Explicit user approval

Record the user’s exact approval message, timestamp, and any approved deviations from this request here. If a parameter changes, request approval again before execution.
