# Proxmox VE 9 Operations Cookbook

Use these as inspected patterns, not blind commands. Replace placeholders only after read-only inventory and required approval.

## Read-only node and guest inventory

```bash
pveversion -v
pvesh get /nodes
pvesh get /cluster/resources --type vm
pvesm status
pct list
qm list
ip -brief address
ip route
findmnt
```

Inspect a specific container or VM without modifying it:

```bash
pct config <CTID>
qm config <VMID>
pvesh get /nodes/<NODE>/lxc/<CTID>/config
pvesh get /nodes/<NODE>/qemu/<VMID>/config
```

## Storage inspection

```bash
pvesm status
pvesm list <STORAGE_ID>
pvesm list <STORAGE_ID> --vmid <GUEST_ID>
pvesm path <VOLUME_ID>
```

Do not use `pvesm free`, remove a storage configuration, or change a storage content type without explicit approval and a rollback/backup plan.

## Templates and container lifecycle

```bash
pveam update
pveam available --section system
pveam list <TEMPLATE_STORAGE>
pct status <CTID>
pct enter <CTID>
pct exec <CTID> -- <reviewed command>
```

Downloading a template, creating a container, changing mount points, setting start-on-boot, or altering features is state-changing. Route those through `proxmox-service-guest-gate`.

## Backups and restore

```bash
pvesh get /nodes/<NODE>/vzdump
pvesh get /storage/<BACKUP_STORAGE>/content
```

Before a backup, confirm managed-volume versus bind-mount behavior, destination capacity, retention, and guest/application quiescence requirements. Before a restore, identify the target guest ID, target storage, network isolation, and whether it is a disposable recovery test. Restores, pruning, deleting backups, and changing retention are state-changing and require approval.

## Network and firewall inspection

```bash
pvesh get /nodes/<NODE>/network
pvesh get /cluster/firewall/options
pvesh get /nodes/<NODE>/firewall/options
```

Confirm bridge, address strategy, route, VLAN tag, firewall scope, and a post-change test client before modifying host or guest networking.

## Package and upgrade inspection

```bash
apt update
apt list --upgradable
pveversion
journalctl -p warning..alert -b
```

For a major version upgrade, use the version-specific official guide and its checker. Do not treat these inspection commands as approval to run `dist-upgrade`, reboot, or alter repositories.
