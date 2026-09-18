# Homelab Music Server Library Cleanup — Findings

> Consolidated 2026-09-18 from the live session (Buffy/Freebuff) continuing the codex
> session (`# Server work from codex.md`). Everything here was verified empirically
> unless marked otherwise.

---

## 1. Infrastructure inventory (verified)

### Proxmox host ("proxmox" / the box)
| Property | Value |
|---|---|
| Hardware | HP laptop ~15-bs0xx (2018): i5-7200U 2c/4t, 8 GB DDR4, **1 TB 5400 RPM HDD (the bottleneck)**, gigabit NIC |
| PVE version | 9.2.11 (kernel 7.0.14-12-pve) |
| LAN IP | 192.168.2.9 |
| Tailnet IP | 100.65.21.28 (`proxmox.tail0ea6ba.ts.net`) |
| Web UI | https://proxmox.tail0ea6ba.ts.net:8006 (login: root@pam, password NOT stored anywhere in chat — entered manually by idols) |
| SSH | `ssh root@192.168.2.9` — works now (see §3 firewall saga); key `idols@MVNK` already in `/root/.ssh/authorized_keys` |
| Load reality | Load 8–12 = thrashing. Anything >4 needs throttling. One meaningful workload at a time (idols' AGENTS.md rule) |

### CT 101 "homelab-core" (where all the music work happens)
| Property | Value |
|---|---|
| LAN IP | 192.168.2.242 |
| Tailnet IP | 100.80.82.44 (SSH to it times out — never needed, LAN works) |
| SSH | `ssh root@192.168.2.242` — key auth, worked from day one |
| Services | Docker: **Navidrome 0.63.2** (up 12+ days, port 4533, healthy = HTTP 302), **slskd**; beets **1.6.0** / Python 3.11.2 installed natively |
| Music volume | `/opt/homelab/navidrome/music` — 590 GiB, ~405 used, **157 GiB free** (merged from 400→600G during codex session) |
| Rollback snapshot | `pre-dedup-20260917` (covers rootfs + music volume, confirmed via PVE API) |
| Tools in CT | `beet`, `fpcalc` (chromaprint), python3.11. No `lsof`/`fuser`. No ffprobe (not needed — beets DB carries bitrate/depth/rate) |

### Tailnet (tail0ea6ba.ts.net)
- `mvnk` — Windows PC (100.69.36.47, LAN .121)
- `proxmox` — host (above)
- `homelab-core` — CT 101 (above)
- `ai` — tagged device, linux
- `pixel-10` — android, usually offline
- MagicDNS handles `*.ts.net` only; everything else resolves via router DNS
- Windows resolves tailnet names via NRPT (Chrome/curl work even though `nslookup` against the router says NXDOMAIN — it bypasses NRPT by querying 192.168.2.1 directly)

### Router
- **Bell Home Hub 3000** at 192.168.2.1 (`mynetwork.home`), Amino/KitBase GUI v8.0.1, Plume mesh integration
- DNS filter (Bell-side "Web Safe"-equivalent, account-level, NOT in hub UI) NXDOMAINs `example.com/net/org` etc. Ad domains pass. If a test site mysteriously NXDOMAINs, this is why. Fix is account-level or set client DNS to 1.1.1.1
- Hub fingerprints as Unbound-ish (version.bind="UNKNOWN", hostname.bind=NOTIMP)

---

## 2. Music library state (the migration)

### Numbers (verified 2026-09-18)
| Location | Files | Size | Audio files |
|---|---|---|---|
| **Live library** (in Navidrome, registered in beets DB asis) | 6,645 (6,209 audio) | 190.51 GiB | 6,209 |
| **Stage** `.staging-20260917/` (Music/ + downloads/) | 12,437 | 213.95 GiB | 7,111 |
| **Union after merge** | — | ~405 GiB | ~13,320 |

Format mix (stage): 5,754 flac / 633 mp3 / 637 wav / 68 m4a / 16 ogg / 2 opus / 1 aiff.
Stage also has 4,886 slskd .html, 218 .lrc, 78 .nfo, 68 .jpg, 65 .txt (junk to ignore in dedup).

### Layout realities (affects any dedup/merge logic)
- Live library top level is a **mix**: artist dirs (`$NOT`), album-with-year dirs (`(1974) Natty Dread` **and** variants `[1971] Soul Revolution… {mbid…}`, `1974 Natty Dread`, …), and **loose flat files** (`05 I Am Nietzsche.flac`, `01 The Gospel.flac`)
- Same albums exist under multiple naming schemes → strong duplicate signal
- Stage `downloads/` is flat with messy filenames (`BCee_Come & Join Us_14_Breath In.flac`)
- `lost+found/` exists (permission-denied on find — prune it explicitly)

### Safety state
- Windows originals (`D:\nikFiles\Music\jdSoundVault\01musicLibrary\{Music,downloads}`) **untouched** — transfer was a copy
- PVE snapshot `pre-dedup-20260917` = rollback of last resort
- **157 GiB free < 213.95 GiB staged → the merge MUST be a move, never a copy**

---

## 3. Access paths — what works, what doesn't, and the saga

### The firewall mystery (hours spent — don't repeat it)
1. Symptom: host:22 timed out from everywhere, ping + :8006 fine
2. Cluster firewall had a `DROP tcp/22` at rule 6 **above** the ACCEPTs → deleted it via API → still blocked
3. **The real culprit was a second DROP at the NODE level**: `/nodes/proxmox/firewall/rules/15 = DROP:22`. Node rules compile into `PVEFW-HOST-IN` independently of cluster rules. Deleted via `pvesh delete /nodes/proxmox/firewall/rules/15` → instantly fixed. No reboot needed (kernel applies rule changes live)
4. **Lesson: check BOTH `/cluster/firewall/rules` AND `/nodes/proxmox/firewall/rules`**
5. Rule list is now all-ACCEPT; `ts-input` accepts everything on tailscale0

### Working access paths (in order of preference now)
1. **`ssh root@192.168.2.9`** (host) — full control incl. `pct exec 101`
2. **`ssh root@192.168.2.242`** (CT) — direct for all music work
3. PVE web UI in agent-browser (`--headed`), logged in manually once — cookies persisted in the agent-browser profile, so later sessions may skip login
4. **In-page PVE API**: `agent-browser eval "fetch('/api2/json/...').then(r=>r.json())"` — GETs work great (cluster/resources, snapshots, firewall read). **Writes return 401** — the CSRFPreventionToken lives only in UI memory, not localStorage/cookies, so raw fetch can't write. Use `pvesh` on the host over SSH instead

### The blind-typing bridge (pre-SSH workaround, keep in back pocket)
xterm.js canvas terminals can be **typed into but not read** (eval returns CSS, AX tree has no output). Pattern that worked:
```
agent-browser click @e270
agent-browser keyboard type "{ cmds... } > /tmp/d.txt 2>&1; pct exec 101 -- sh -c 'cat > /root/diag.txt' < /tmp/d.txt"
agent-browser press Enter
ssh root@192.168.2.242 'cat /root/diag.txt'   # readable window into the host
```
No longer needed for routine work but invaluable if SSH ever breaks again.

### Misc access notes
- WSL2 `ssh pve` alias is configured in `~/.ssh/config` but MagicDNS doesn't resolve inside WSL → use IPs
- `agent-browser open --headed <url>` shows the visible automation Chrome; first launch to a new site can take >45s (don't kill it — poll with `agent-browser get url` instead)
- Ctrl-C'n an SSH command kills remote children **non-recursively** — orphan cascades were a whole saga (see §5)

---

## 4. Tooling decisions (the "why")

### Beets config (CT 101: `/root/.config/beets/config.yaml`)
- `autotag: no`, `write: no`, `copy: no`, `move: no` — **asis import, zero file mutation**, files stay wherever they are
- library: `/root/.musiclibrary.db` (6,209 items = the live library)
- chroma plugin configured with idols' AcoustID key `REDACTED — lives in CT 101 /root/.config/beets/config.yaml (chroma) and idols' secret store`
- AcoustID key facts: key = `REDACTED — lives in CT 101 /root/.config/beets/config.yaml (chroma) and idols' secret store`; MusicBrainz needs **no key** (anonymous OK); Last.fm optional (genre only, skipped)

### Bulk attribute injection — the only pattern that works (verified 2026-09-18)
- **Use the beets ORM inside ONE transaction**: `with lib.transaction(): for item in lib.items(): item.attr = x; item.store()` — 13,318 items in **2.5s**. Row-by-row stores WITHOUT a transaction = one fsync each = hours of D-state disk storm on this HDD (killed it, wasted an hour — don't repeat).
- **beets names WAV files `WAVE`** (not WAV!) — format ranks must match `('WAV','WAVE')` or the whole WAV tier silently sinks to rank 1. Caught in pre-flight verification.
- `PYTHONPATH=/usr/share/beets` required for `from beets.library import Library` in this CT (non-standard install location).
- Raw SQLite UPDATE works for writes, but beets kept serving a STALE snapshot afterward (fresh processes, no WAL files, integrity ok — root cause unresolved, anomaly logged). After an ORM pass both views agree. **Rule: verify attribute changes through `beet ls -f '$attr'`, not just SQLite.**
- `pgrep -f "beet.*import"` self-matches any script containing `from beets.library import` — use `pgrep -af` and eyeball, or match `/bin/beet` exactly.

### Why fingerprints are computed OUTSIDE beets (measured, not guessed)
- Chroma during import calls the AcoustID API **per file**: 46s for 2 files → **~10 days** for 19k. Rejected.
- Local `fpcalc` (no network): ~2.5/sec at P4, ~1/sec nice'd at P1 → 90 min to 12h depending on politeness. Chosen.
- Plan: bulk-inject TSV fingerprints into the beets DB (path-matched), then `beet duplicates` does the dedup **natively** (idols' design instinct, confirmed correct)

### The pipeline (agreed design)
1. ✅ Register live library in beets (done, 6,209 asis)
2. 🟢 External fpcalc pass → `/root/fingerprints.tsv` (path⇥duration⇥fingerprint) — running, resumable (~6,300/13,320 at 09:00)
3. Bulk-inject fingerprints into beets DB (ORM + single transaction — see injection pattern above)
4. ✅ `beet import -A -q` of `.staging-20260917` — **DONE 2026-09-18** (13,318 items total; 2 files skipped incl. truncated `SeeYouSpaceCowboy...WEB.flac`)
5. `beet duplicates` — **config syntax that actually works on beets 1.6.0 (validated on a scratch library, end-to-end):**
   ```yaml
   duplicates:
     keys: albumartist album title          # BARE STRING — a YAML list [albumartist album title] silently matches nothing
     tiebreak:
       items: [quality_rank, bitdepth, samplerate, bitrate]   # must nest under items:/albums: — flat mapping is silently ignored
   types:
     quality_rank: int
   ```
   Tiebreak sorts descending on every listed field, so `[quality_rank, bitdepth, samplerate, bitrate]` gives WAV>FLAC>MP3 then deeper→higher-rate→higher-bitrate. `quality_rank` injected: WAVE=3, FLAC=2, everything else=1 (idols' explicit order). Scratch test confirmed: WAV kept, FLAC+MP3 quarantined. `--move` to `.quarantine-dedup-20260918/` + `--log` report
6. **Non-destructive policy (idols' standing order): quarantine + report, never delete; sources + snapshot preserved**
7. Optional: batch AcoustID lookups (the key) only for the few hundred dup groups — not all files
8. Merge stage via `beet import -m`, then Navidrome rescan via its API (**never restart the container**, it's production)
9. Then: SysKnife install on host, network map, final report (original codex tasks 1/3/4)

---

## 5. Operational gotchas (paid for in time — read before touching)

1. **Orphan cascades**: killing a `nohup find | xargs | fpcalc` script leaves children spawning new work. Kill in pipeline order (`find` → `xargs` → `fpcalc`), verify `pgrep -c fpcalc = 0`, and use `flock -n` lockfiles so relaunches refuse to stack
2. **Lock holder detection without lsof/fuser**: `for p in /proc/[0-9]*; do readlink $p/fd/9 | grep -q fp.lock && echo $p; done`
3. **Two writers + one truncator = data loss**: a `>` redirect in a second script clobbered the TSV being appended by the first. The current setup dedupes into `/root/fp-uniq.tsv` on start and rebuilds `/root/fp-done.txt` from it
4. **The grep bug**: `find -print0 | xargs -0 grep -vxFf done.txt --` makes grep read the **audio files as content** (binary → empty). v2 script avoids xargs entirely: NUL-delimited find → bash `read -d ''` loop with a `declare -A DONE` skip set
5. **`pct push` beats quoting hell**: writing scripts locally and `base64`-pushing them into the CT is far saner than nested ssh→pct→bash -c escaping
6. **Load discipline**: 4-way parallel fpcalc put the 2-core box at load 12.67; SSH handshakes started dying ("banner exchange timeout" = starvation symptom, looks like a network bug but isn't). Now: 1 worker, `nice -n 19 ionice -c3`. ETA for full fingerprint pass: **~12h at idle priority** (2,348/13,300+ done at time of writing)
7. **Don't reboot the host for firewall changes** — PVE applies them live. Reboot only kills running jobs
8. **Navidrome health check**: `curl -fsS -o /dev/null -w "%{http_code}" http://127.0.0.1:4533/` → 302 = healthy (login redirect). Rescan via Subsonic API, never restart the container without asking
9. **idols' standing rules that bind this work** (from AGENTS.md): ask before VM/CT create/destroy/reboot/storage ops; one meaningful workload at a time on the box; never kill processes you didn't start (the orphan kills were all of my own launches); prefer scoped PVE API tokens over root SSH for future automation; production media app internals off-limits

---

## 6. Reversibility ledger
| Change | Undo |
|---|---|
| Node firewall rule 15 (DROP:22) deleted | `pvesh create /nodes/proxmox/firewall/rules --type in --action DROP --proto tcp --dport 22` (re-add only if idols wants SSH closed again) |
| Cluster firewall rule 6 (DROP:22) deleted | same pattern on `/cluster/firewall/rules` |
| SSH key `idols@MVNK` in host + CT authorized_keys | delete the line containing `idols@MVNK` |
| beets DB `/root/.musiclibrary.db` | `rm` (pure metadata, files untouched by design) |
| Fingerprint artifacts (`fingerprints.tsv`, `fp-done.txt`, scripts) | `rm` (pure derived data) |
| Library content | PVE snapshot `pre-dedup-20260917`; Windows originals intact |
| Quarantine dir (when created) | move files back (nothing is ever deleted) |

---

## 7. Open items / next session checklist
- [x] Poll fingerprint pass (2026-09-18: ~6,300/13,320, healthy)
- [x] Bulk-inject `quality_rank` (WAVE=3/FLAC=2/rest=1, ORM single-txn, verified via beet ls)
- [x] `beet import` the staged tree (13,318 total in DB)
- [ ] Wait for fingerprint pass to COMPLETE (idols: dedup runs once, all at once — no incremental passes)
- [ ] Bulk-inject fingerprints into beets DB (same ORM pattern)
- [ ] Dry-run `beet duplicates` (keys + tiebreak config already validated on scratch lib) → review counts → `--move` quarantine + `--log` report → review with idols before merge. Quality order (idols): **WAV > FLAC > MP3** via quality_rank field (WAVE naming gotcha!) — dedup ONCE, no incremental passes
- [ ] Merge, Navidrome rescan, verify playability
- [ ] SysKnife on host (codex deferred it; Node.js/npm may already be installed on host — check `node --version` first)
- [ ] Network map (task 3) + final report (task 4)
- [ ] Optional: batch AcoustID lookups for dup groups only
- [ ] Cleanup scratch: `/root/beets-test/`, `/tmp/beets-test-music/` in CT
