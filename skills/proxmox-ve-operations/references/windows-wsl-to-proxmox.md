# Secure Windows and WSL Connections to Proxmox VE

This reference defines the **Windows 11 and Ubuntu WSL control-plane pattern** for administering a Proxmox VE node securely. It is written for a private homelab whose current node is reachable at `192.168.2.9`, but its examples use placeholders so that the connection model can be reused. Read it before configuring a Windows SSH client, a WSL/Ansible control node, API access, browser TLS trust, or private remote access.

> **Scope boundary.** Treat creating Linux users, adding `authorized_keys`, changing SSH daemon settings, importing a trust anchor, creating API tokens, installing a VPN client, or changing tailnet policy as state-changing operations. Inspect first, preserve console recovery, write the exact change request, and obtain confirmation before carrying them out. Do not modify legacy guests merely to establish a host connection.

## 1. Connection model and decision rule

Use direct, private-LAN access while the Windows PC and Proxmox node share the trusted home network. Use the **native Ubuntu-26.04 WSL environment** for repository-driven operations and Ansible. Use Windows PowerShell or Windows Terminal for interactive Windows-native administration and the browser UI. Do not expose ports `22` or `8006` to the public Internet; a private VPN is the remote-access solution when direct LAN connectivity is unavailable.

| Route | Primary purpose | Identity and trust material | Default decision |
|---|---|---|---|
| Windows browser | Interactive Proxmox web UI and console | MFA-protected human Proxmox account; trusted CA/certificate | Use on the private LAN at the certificate’s DNS name and port `8006`. |
| Windows PowerShell / Windows Terminal | Human SSH inspection and an optional PowerShell API client | Windows-only Ed25519 key in `%USERPROFILE%\.ssh`; Windows `ssh-agent`; pinned host key | Use for short, interactive work. Do not make it the Ansible controller. |
| Ubuntu-26.04 WSL | `ssh`, `curl`, `pvesh` over SSH, Ansible, and mise tasks | WSL-only Ed25519 key in `~/.ssh`; WSL `known_hosts`; WSL-local CA file | This is the authoritative automation route. |
| Proxmox REST API | Narrow, non-interactive API operations | One privilege-separated API token per purpose, injected at runtime | Prefer to passwords for supported REST endpoints. API tokens cannot use system or guest console endpoints. [1] |
| Private VPN | Remote access when away from the LAN | VPN identity plus the normal SSH/API/browser controls | Use a dedicated VPN layer; do not replace a LAN-only deployment with public port forwarding. |

The current default endpoint is `https://192.168.2.9:8006`, but use a stable hostname such as `proxmox.<internal-domain>` once DNS and the certificate subject/SAN are aligned. A trusted CA alone does not fix a hostname mismatch: clients must use a name that the certificate covers. Do not normalize the practice of suppressing certificate or host-key validation.

## 2. Establish an immutable trust anchor before first use

Before adding an SSH host key or trusting a browser/API certificate, verify the Proxmox host’s fingerprint through an **independent path**. The safest paths are the physical console, an already-authenticated Proxmox console, or a previously verified local session. Do not treat a fingerprint obtained solely from the network as verification.

| Material | Obtain from the trusted path | Client-side action | Never do |
|---|---|---|---|
| SSH Ed25519 host-key fingerprint | On the node, inspect `/etc/ssh/ssh_host_ed25519_key.pub` with `ssh-keygen -lf` | Compare it with the result from `ssh-keyscan -t ed25519 <host> | ssh-keygen -lf -`, then pin the verified key in the relevant `known_hosts` file | Do not use `StrictHostKeyChecking=no` or accept a changed key without checking why. |
| Proxmox cluster CA | Copy `/etc/pve/pve-root-ca.pem` through the trusted path | Import it into the Windows/browser trust store and store a WSL copy in an owner-controlled configuration directory | Do not alter auto-generated node certificates or the cluster CA files manually. [2] |
| Proxmox web/API name | Inspect the installed certificate subject/SAN | Browse and call the API through the matching name | Do not bypass name validation with a browser warning or `-SkipCertificateCheck`. |

The default Proxmox node certificate is signed by the cluster CA and is therefore not automatically trusted by Windows or browsers. Proxmox documents out-of-band distribution of `/etc/pve/pve-root-ca.pem` to administrator workstations as the LAN-safe way to eliminate those warnings. [2]

## 3. Bootstrap accounts and harden SSH without lockout

Separate **Proxmox application identities** from **Linux host identities**. A Proxmox user such as `tony@pve` governs GUI/API authorization, while a Linux account such as `pveadmin` is needed for SSH and `sudo`. Do not use a `root@pam` API token or root SSH login merely for convenience. Proxmox access control is role- and path-based; create only the permissions a human or automation role actually needs. [1]

First ensure a local-console recovery path exists. Then, in one approved change set, create a non-root Linux administration account, add its verified public key, verify that it can establish SSH and perform only the required `sudo` operations, and retain the console as fallback. Only after both Windows and WSL have completed successful key-based tests should an approved SSH hardening change disable password authentication and root SSH access. Test an `sshd` configuration before reloading it, keep the original connection open during the test, and do not use an `AllowUsers` restriction until every required human and automation account has been accounted for.

| Hardening step | Preconditions | Validation | Rollback boundary |
|---|---|---|---|
| Add `pveadmin` and a verified public key | Console access; approved account and sudo scope | `ssh pveadmin@<host> 'sudo -v'` from Windows and WSL | Remove only the newly added key/account after confirming no approved workflow depends on it. |
| Disable password SSH authentication | Both keys work; console recovery is known | Open a second key-authenticated session before closing the first | Re-enable only through the console if an approved user cannot connect. |
| Disable root SSH login | A non-root administrator can complete the required `sudo` commands; emergency console is tested | Read-only `sudo pvesh get /nodes --output-format json-pretty` succeeds | Restore the former SSH configuration through the console, then investigate the missing least-privilege path. |

Do not forward the Windows or WSL SSH agent to the Proxmox host by default. Agent forwarding lets software on the destination use the forwarded signing capability and is unnecessary for ordinary node administration. Similarly, do not copy a Windows private key to WSL or a WSL private key to Windows; use separate identities so that revocation, loss response, and audit trails remain host-specific.

## 4. Windows PowerShell and Windows Terminal setup

Windows OpenSSH includes `ssh-keygen`, `ssh-agent`, and `ssh-add`. Microsoft recommends a non-empty passphrase for the private key and documents using the user-scoped `ssh-agent` service so an interactive SSH client can use a protected key without embedding passphrases in scripts. [4]

Create a dedicated Windows key in an elevated PowerShell session only for the service-start operation. The key-generation command itself should run as the normal Windows user.

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.ssh" | Out-Null
ssh-keygen -t ed25519 -a 64 `
  -f "$env:USERPROFILE\.ssh\id_ed25519_proxmox_windows" `
  -C "windows-proxmox-$env:COMPUTERNAME"

# Elevated PowerShell: enable the user-scoped agent service and load the key.
Get-Service ssh-agent | Set-Service -StartupType Automatic
Start-Service ssh-agent
ssh-add "$env:USERPROFILE\.ssh\id_ed25519_proxmox_windows"
```

After out-of-band fingerprint comparison, use a dedicated host alias in `%USERPROFILE%\.ssh\config`. Keep `IdentitiesOnly yes` so unrelated keys are not offered to the node and retain explicit host-key validation.

```sshconfig
Host proxmox-windows
  HostName 192.168.2.9
  User pveadmin
  IdentityFile ~/.ssh/id_ed25519_proxmox_windows
  IdentitiesOnly yes
  StrictHostKeyChecking yes
  UserKnownHostsFile ~/.ssh/known_hosts
  ServerAliveInterval 30
  ServerAliveCountMax 3
  ForwardAgent no
```

Use the alias for a harmless first test, then execute only approved host work:

```powershell
ssh proxmox-windows 'hostnamectl --static; pveversion --verbose'
```

Windows Credential Manager is not the required store for this pattern. Use `ssh-agent` for the passphrase-protected Windows key and Bitwarden Secrets Manager for automation secrets. Do not put Proxmox passwords, API token values, or Bitwarden machine-account tokens in a Terminal profile, a PowerShell history file, a Git repository, or a persistent system-wide environment variable.

## 5. Native WSL SSH and `pvesh` setup

The Ubuntu-26.04 WSL distribution is the authoritative automation control plane. Run all repository, mise, Ansible, and WSL SSH work from the native Linux workspace, not from a Windows UNC current directory or an agent-mounted transport path. From Windows, begin in `C:\` and invoke the exact distribution with `wsl.exe -d Ubuntu-26.04 -- bash -lc ...` when a Windows shell must launch a WSL command.

Create a separate WSL key. A process-local `ssh-agent` is sufficient for an interactive WSL session; do not arrange a Windows-to-WSL agent bridge unless an explicitly approved operational need outweighs the added trust path and maintenance burden.

```bash
umask 077
install -d -m 700 "$HOME/.ssh"
ssh-keygen -t ed25519 -a 64 \
  -f "$HOME/.ssh/id_ed25519_proxmox_wsl" \
  -C "wsl-proxmox-$(hostname -s)"
eval "$(ssh-agent -s)"
ssh-add "$HOME/.ssh/id_ed25519_proxmox_wsl"
```

After independently verifying the host fingerprint, place an equivalent alias in `~/.ssh/config` and keep `~/.ssh/known_hosts` owned by the WSL user.

```sshconfig
Host proxmox-wsl
  HostName 192.168.2.9
  User pveadmin
  IdentityFile ~/.ssh/id_ed25519_proxmox_wsl
  IdentitiesOnly yes
  StrictHostKeyChecking yes
  UserKnownHostsFile ~/.ssh/known_hosts
  ServerAliveInterval 30
  ServerAliveCountMax 3
  ForwardAgent no
```

`pvesh` is a **local** Proxmox API shell that is available only to `root`; it does not become a client-side command merely because SSH is installed. Invoke it through a deliberately authorized non-root SSH account with `sudo` and use `get` or `ls` for remote inspection. [3]

```bash
ssh proxmox-wsl 'sudo pvesh get /nodes --output-format json-pretty'
ssh proxmox-wsl 'sudo pvesh get /cluster/resources --type vm --output-format json-pretty'
```

## 6. REST API tokens and safe PowerShell/WSL calls

Use the REST API for scoped, non-interactive workflows that do not need a console. Proxmox API tokens are stateless, cannot access VM or system console endpoints, and should use **privilege separation**, which is the default. A separated token must have explicit ACLs and its effective permissions are the intersection of its own ACLs and its owner’s permissions. Set an expiration when practical; the secret value is displayed only once and must be treated as a secret. [1]

Create a dedicated non-root Proxmox user and one token per purpose only after the user approves the exact role, path, expiration, owner, and Bitwarden project. A read-only inventory token should normally have `PVEAuditor` only at the smallest path that covers its intended reads. A deployment token must not silently inherit a broader human administrator’s permissions. The following is an **illustrative, state-changing** pattern rather than a command to run without confirmation:

```bash
# On the Proxmox node, after an approved change request.
pveum user token add automation@pve inventory -privsep 1 --expire <unix-epoch>
pveum acl modify / -token 'automation@pve!inventory' -role PVEAuditor
pveum user token permissions automation@pve inventory
```

Store the complete Authorization header value in a Bitwarden Secrets Manager secret named, for example, `PVE_API_TOKEN_AUTH`. Its value should have the documented form `PVEAPIToken=USER@REALM!TOKENID=UUID`. Keep only the secret contract, ID, owner, scope, and rotation metadata in version control; inject the value into a reviewed process at runtime with the scoped `bws run` pattern. Never render it to a committed `.env` file or print it. [1]

A PowerShell client should require the injected value and rely on the Windows certificate store. It must fail rather than skip TLS validation.

```powershell
if ([string]::IsNullOrWhiteSpace($env:PVE_API_TOKEN_AUTH)) {
  throw 'PVE_API_TOKEN_AUTH was not injected into this process.'
}

$headers = @{ Authorization = $env:PVE_API_TOKEN_AUTH }
$uri = 'https://proxmox.example.internal:8006/api2/json/nodes'
Invoke-RestMethod -Method Get -Uri $uri -Headers $headers
```

A WSL client should use the verified cluster CA file when the default Proxmox CA is retained. The hostname in the URL must match the trusted certificate.

```bash
: "${PVE_API_TOKEN_AUTH:?Inject this via a reviewed Bitwarden runtime command}"
curl --fail --silent --show-error \
  --cacert "$HOME/.config/proxmox/pve-root-ca.pem" \
  -H "Authorization: $PVE_API_TOKEN_AUTH" \
  'https://proxmox.example.internal:8006/api2/json/nodes'
```

## 7. WSL Ansible control node

Use Ansible from native WSL, where the repository, SSH config, and private key have Linux ownership and permission semantics. Ansible encourages SSH keys and `ssh-agent`; it enables host-key checking by default because host-key verification protects against spoofing and man-in-the-middle attacks. Preserve that default. [5]

```yaml
# ansible/inventory/proxmox.yml
all:
  children:
    proxmox_nodes:
      hosts:
        proxmox:
          ansible_host: 192.168.2.9
          ansible_user: pveadmin
          ansible_become: true
          ansible_become_method: sudo
          ansible_ssh_private_key_file: ~/.ssh/id_ed25519_proxmox_wsl
          ansible_ssh_common_args: >-
            -o StrictHostKeyChecking=yes
            -o UserKnownHostsFile=~/.ssh/known_hosts
```

```ini
# ansible/ansible.cfg
[defaults]
host_key_checking = True
inventory = inventory/proxmox.yml

[ssh_connection]
ssh_args = -C -o ControlMaster=auto -o ControlPersist=60s
```

Validate the connection without changing Proxmox state before applying any playbook. A successful ping validates SSH and Python availability; it does not authorize later guest, storage, firewall, or package changes.

```bash
ansible-inventory --graph
ansible proxmox_nodes -m ansible.builtin.ping
ansible proxmox_nodes -m ansible.builtin.command -a 'pveversion --verbose' --become
```

Do not set `ANSIBLE_HOST_KEY_CHECKING=False` to make first contact non-interactive. Instead, verify and pin the expected host key once before running a playbook. Keep platform-level playbooks idempotent, route guest creation through `proxmox-service-guest-gate`, and use application configuration inside the guest rather than modifying the Proxmox host unnecessarily.

## 8. Browser TLS and private remote access

The Proxmox REST API and web UI are both served by `pveproxy`. Proxmox supports its cluster-CA certificate, a custom certificate, or an integrated ACME certificate. It documents automatic ACME renewal after successful configuration. [2]

| TLS/access option | Appropriate when | Security decision |
|---|---|---|
| Import the Proxmox cluster CA | LAN-only node; no public DNS name; one or few administrator workstations | Best initial state. Import the CA through an approved out-of-band transfer and browse using a certificate-matching internal name. |
| Custom internal-CA certificate | Internal DNS and a private PKI already exist | Use the supported certificate upload/management workflow; do not overwrite auto-generated certificate files by hand. [2] |
| ACME DNS-01 certificate | A controlled domain and DNS API are available, but the node must remain private | Viable later option. Store the narrowly scoped DNS credential in Bitwarden and manage the change through the approved Proxmox workflow. |
| ACME HTTP-01 certificate | The node can be safely reached from the public Internet on port 80 | **Not appropriate now.** Proxmox documents that HTTP-01 requires port 80 and public DNS reachability, which conflicts with the LAN/private-VPN-only requirement. [2] |

For remote access, prefer a private VPN that authenticates the Windows computer and, if necessary, the WSL/Proxmox endpoints. **WireGuard** is the fully open-source baseline for a self-managed design; terminate any inbound VPN reachability on a dedicated gateway or router, not by exposing Proxmox HTTPS or SSH. Tailscale is a convenient overlay alternative, but its hosted coordination service is not a self-hosted FOSS control plane; choose it deliberately rather than by default.

If Tailscale is approved, ordinary SSH over the encrypted tailnet is the lowest-surprise initial mode. Tailscale SSH is a distinct feature that intercepts port 22 on the target’s Tailscale address, uses tailnet policy for authorization, and leaves ordinary LAN SSH configuration unchanged. Its `check` mode may require reauthentication, but `checkPeriod: "always"` can be unsuitable for connection-heavy automation such as Ansible. [6] Treat installation, `tailscale set --ssh`, and tailnet ACL changes as explicit host/network changes with a recovery route.

An SSH local forward is a break-glass alternative when a VPN is temporarily unavailable, not a routine publishing mechanism. Keep it private to the local machine and browse using a hostname covered by the certificate after explicitly mapping that hostname to `127.0.0.1` for the temporary session. Do not access the forward as `https://localhost` unless the certificate covers `localhost`.

```bash
# Keep this foreground session open; no public listener is created.
ssh -N -L 8443:127.0.0.1:8006 proxmox-wsl
```

## 9. Secret, key, and recovery handling

| Item | Correct location | Version-control record | Rotation/revocation response |
|---|---|---|---|
| Windows private SSH key | `%USERPROFILE%\.ssh`, protected by passphrase and Windows `ssh-agent` | Key label and public fingerprint only | Remove its public key from Proxmox; generate a replacement key. |
| WSL private SSH key | `~/.ssh`, mode `0600`, optionally loaded in a local agent | Key label and public fingerprint only | Remove its public key from Proxmox; generate a replacement key. |
| Proxmox API token Authorization value | Bitwarden Secrets Manager, injected only into the trusted process | Token ID, owner, scope, expiry, and rotation date | Revoke the token, create a scoped replacement, validate non-destructively, then retire the old contract. |
| Bitwarden machine-account token | Host-local owner-only location, outside Git | Machine-account name, project scope, and recovery procedure | Create/validate a replacement before revoking the old token. |
| Cluster CA and host fingerprints | Approved administrator trust stores and WSL config directory | SHA-256/fingerprint and source node | Re-verify through the console if the host is reinstalled or a key/certificate changes unexpectedly. |

If the Proxmox host is reinstalled, an SSH host key changes unexpectedly, a client device is lost, or an API token may be exposed, stop automated access first. Re-establish trust through the console, remove the affected public key or token, rotate only the impacted identity, validate a read-only operation, and document the incident without recording secret values.

## 10. Approval checklist for first implementation

The first implementation request should name the exact Linux admin account, Proxmox human account, Windows public-key fingerprint, WSL public-key fingerprint, intended SSH hardening change, certificate choice, and the first API token’s role/path/expiry. It should also identify the console recovery route and confirm that CT 100 remains untouched. Only then should the connection configuration be applied.

| Check | Required evidence before approval |
|---|---|
| Network identity | Confirmed bridge, node address, gateway, and a stable local hostname plan. |
| Trust anchor | Console-verified SSH host fingerprint and cluster-CA/certificate fingerprint. |
| Human access | Non-root Proxmox browser account with MFA and recovery keys where supported. [1] |
| Windows and WSL separation | Two distinct public keys, two client configs, and no agent forwarding. |
| Automation scope | A privilege-separated token with least-privilege ACLs, expiry, owner, and Bitwarden project. [1] |
| Recovery | Console path, approved rollback plan, and a test plan for losing each client identity. |
| Exposure boundary | No public forwarding of `22` or `8006`; any VPN or Tailscale change is separately approved. |

## References

[1]: https://pve.proxmox.com/wiki/User_Management "Proxmox VE User Management"
[2]: https://pve.proxmox.com/wiki/Certificate_Management "Proxmox VE Certificate Management"
[3]: https://pve.proxmox.com/pve-docs/pvesh.1.html "pvesh(1) — Shell interface for the Proxmox VE API"
[4]: https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement "Microsoft Learn: Key-based authentication in OpenSSH for Windows"
[5]: https://docs.ansible.com/projects/ansible/latest/inventory_guide/connection_details.html "Ansible: Connection methods and details"
[6]: https://tailscale.com/docs/features/tailscale-ssh "Tailscale SSH documentation"
