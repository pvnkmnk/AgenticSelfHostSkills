# Upgrade path: beets 1.6.0 → 2.x (planned, NOT yet executed)

**Status: deferred by idols' explicit order (2026-09-18): do not upgrade
until the current dedup/merge pipeline completes.** Never swap beets versions
mid-pipeline — the dedup runs against DB state that 1.6.0 wrote and 2.x may
migrate. This file is the plan for when the pipeline is done.

## Why upgrade at all

1.6.0 (Debian 12 package, Aug 2023 vintage) carries verified silent traps
(see `version-notes.md`): list-form duplicates keys that match nothing,
badfiles interactive prompts under quiet imports, incremental silently
disabling resume. Beets 2.13.1+ (July 2026) fixes these, adds the badfiles
automation keys, supports Python 3.14, and the current docs describe 2.x
behavior — fewer reality-checks needed against old source.

## Option A: in-place upgrade in CT 101 (pip)

Debian 12's apt beets is pinned at 1.6.0. The supported route is pip in a
venv (or pipx):

```bash
# inside CT 101
python3 -m venv /opt/beets2 --system-site-packages   # keep pyacoustid etc.
/opt/beets2/bin/pip install -U beets
# sanity: same DB, same config, new binary
/opt/beets2/bin/beet version
/opt/beets2/bin/beet config -p
```

Then repoint `beet` (wrapper script or shell alias) and keep the old binary
available at `/usr/bin/beet` as fallback.

## Option B: fresh Debian 13 CT with beets 2.x (cleaner, more work)

The host (PVE 9.2.11, Debian 13.6) already has
`debian-13-standard_13.1-2_amd64.tar.zst` in `local:vztmpl`. A new CT gets
current Python and a pip-installed current beets with zero 1.6.0 baggage:

1. `pct create <newid> local:vztmpl/debian-13-standard_13.1-2_amd64.tar.zst`
   — mount the SAME music volume (mp0 to
   `/opt/homelab/navidrome/music`), **do not let two CTs mount it rw at
   once during any beets run**.
2. pip-install beets 2.x + chromaprint; copy `/root/.config/beets/config.yaml`.
3. Validate read-only first (`beet ls | wc -l`, spot queries) against the
   existing DB; only then run writes.

Option B is also the natural moment to split responsibilities (beets CT vs
Navidrome CT) if desired. Cost: more setup, another container to maintain.

## Either way: DB backup + migration expectations

```bash
cp /root/.musiclibrary.db /root/.musiclibrary.db.bak-pre2x-$(date +%Y%m%d)
beet version && beet ls | wc -l     # record the pre-upgrade item count
```

2.x migrates the schema on first write. If `beet ls` count or spot queries
change afterward, STOP and restore the backup — do not debug in place.

## Post-upgrade revalidation checklist

Re-run the version-sensitive checks from `version-notes.md` against the new
install — behavior may have changed in BOTH directions:

- [ ] `duplicates` config block: does the bare-string `keys:` still parse
      (and does list-form now work?) — re-test on a scratch library before
      trusting either form
- [ ] `tiebreak.items` nesting: same test
- [ ] `badfiles`: `import_action_on_error`/`import_action_on_warning` keys
      now exist — wire `skip`/`continue` and RE-ENABLE `check_on_import`
- [ ] `incremental`/`resume` interaction: re-read importer behavior
- [ ] Plugin inventory: is `fingerprint` now shipped? (2.x docs say yes —
      enables chroma auto-fingerprinting if ever desired)
- [ ] `beet ls -f '$quality_rank'` still renders injected fields (flexible
      attributes survive schema migration — verify!)
- [ ] WAV still reports `format: WAVE`? Re-check the rank mapping either way
- [ ] Navidrome unaffected (it reads files, not the beets DB) — confirm by
      playing a few items post-rescan

## Rollback

- Option A: repoint `beet` back to `/usr/bin/beet` (1.6.0); restore DB backup
  if 2.x already migrated the schema.
- Option B: unmount/destroy the new CT; the music volume and original CT are
  untouched.
