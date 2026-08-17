# Guest Validation Gates

## Read-only inventory gate

Collect node version, online state, CPU/RAM capacity and current usage, storage names and free capacity, bridge/gateway/subnet, templates, backup configuration, existing guest IDs, and guest classifications. Do not create, start, stop, resize, migrate, delete, or reconfigure a guest at this stage.

## Creation gate

Require explicit approval for the exact values in the change request. Reconfirm the next guest ID immediately before creation. A new data volume, an address assignment, a downloaded template, and runtime feature flags are each state changes and must be included in the approval.

## Post-creation validation gate

Verify the new guest identity, boot state, address, private-LAN reachability, update status, storage mounts, free disk, runtime requirements, health-check endpoint, logs, and backup enrollment. Record the results without writing credentials or secret values to the inventory.

## Data and service gate

Do not place irreplaceable media, production databases, or non-recoverable configuration in the guest until secret retrieval has been tested and a backup destination plus disposable restore procedure exists.

## Rollback gate

When validation fails, preserve logs and the approved change record. Confirm that the new guest has no user data, then ask for explicit approval before destroying the new guest. Do not delete or modify unrelated guests as part of rollback.
