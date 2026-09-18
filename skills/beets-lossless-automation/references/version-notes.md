# Version notes — silent traps in beets 1.6.0 (and what 2.x fixes)

Every claim below was verified against the beets 1.6.0 source at
`/usr/share/beets/beetsplug/` on CT 101 (Debian 12.15) or executed live, and
cross-checked against the 2.13.x changelog. The unifying theme: **most of
these traps fail silently — you get empty results, not errors.**

## Quick version triage

```bash
beet version
```

| Version | Verdict |
|---|---|
| 1.6.0 (Debian 12 package) | Usable with the traps below; verify every config form on a scratch library first |
| 2.x (2.13.1+, July 2026) | badfiles automation keys exist; docs current; prefer it for new deployments (see `upgrade-path.md`) |

## 1. `duplicates` plugin — the config forms that actually work

**`keys:` must be a BARE STRING.** A YAML list silently matches nothing:

```yaml
duplicates:
  keys: albumartist album title        # ✓ works (space-separated string)
  # keys: [albumartist, album, title]  # ✗ silent zero-output in 1.6.0
```

Mechanism: the plugin does `getattr(item, k)` per key over the parsed string;
a list-form key never resolves, every item is skipped, the command exits 0
with no output. Diagnosed by reading `_group_by`/`_dup` in the plugin source.

**`tiebreak:` must nest under `items:`/`albums:`.** A flat mapping is
silently ignored and the plugin falls back to its default ordering:

```yaml
duplicates:
  tiebreak:
    items: [tags_complete, quality_rank, bitdepth, samplerate, bitrate]  # ✓
  # tiebreak: [quality_rank, bitdepth]        # ✗ ignored (wrong type)
  # tiebreak: {quality_rank: desc}            # ✗ ignored (flat mapping)
```

Mechanism: `_duplicates()` calls `_order(objs, tiebreak)` where the mapping is
indexed as `tiebreak[kind]` (kind = `items`/`albums`). The sort is
`reverse=True` — **descending on every listed field** — so the field order
above reads: tag-complete first, then WAV-tier, then deeper/higher-rate/
higher-bitrate.

**Keys via CLI always work** and are the robust path for scripted runs:

```bash
beet duplicates -k acoustid_fingerprint -k acoustid_length -s -f '$path'
beet duplicates -k albumartist -k album -k title -s -f '$path'
```

Without any keys, the plugin defaults to `mb_trackid`/`mb_albumid` — useless
on asis-imported or loosely-tagged libraries.

**Flag semantics (1.6.0, verified from source):**
- `-F/--full` = show ALL group members including the winner. A dedup run that
  moves losers MUST omit `-F` (offset logic: `objs[offset:]` with offset 0
  under `-F`, 1 without). Dry-run counts under `-F` are ~2× the loser count.
- `-s/--strict` = only compare items where all key fields are set. An empty
  result under strict means "no complete-key matches", NOT "no duplicates".
- `-C sha256sum` = group by file content hash (bit-identical only; catches
  retagged copies, not different encodes).
- `--move DIR` moves losers (rename + DB store; collisions resolved by
  beets' `util.unique_path`, verified at library.py:817). Never `--delete`.
- Tiebreak reads flexible attributes — but declare non-string types under a
  top-level `types:` block or template/query behavior can surprise
  (`types: {quality_rank: int}`).

## 2. `badfiles` — 1.6.0 prompts interactively (stalls quiet imports)

In 1.6.0, `check_on_import: yes` routes failures to
`on_import_task_before_choice`, which calls `ui.input_options(['aBort',
'skip', 'continue'])`. Under `beet import -q` this either stalls forever or
aborts the batch. The config keys `import_action_on_error` /
`import_action_on_warning` **do not exist in 1.6.0** (grep for them in
`beetsplug/badfiles.py` — only `check_on_import` exists). They are 2.x keys.

1.6.0 guidance: leave `check_on_import` off for unattended imports; run
`beet bad` as a post-import validation pass instead, with a fallback loop:

```bash
find LIBRARY -type f -iname '*.flac' -print0 | xargs -0 -r -n1 flac -t
```

## 3. `incremental: yes` silently disables `resume`

In `beets/importer.py` (1.6.0), enabling `incremental` sets
`iconfig['resume'] = False` with no warning. If you rely on resume state to
survive interruptions, pick one deliberately. Also: after a fatal crash,
stale resume state can skip files recorded as processed — reprocess with
`resume: no` for that candidate.

## 4. Plugin availability differs by version (1.6.0 verified)

| Plugin | 1.6.0 | Note |
|---|---|---|
| `fingerprint` | **absent as a package** | The 2.x docs list it as core; on 1.6.0 it's not shipped in the Debian package. Chroma (which requires it on 2.x) works standalone here. Use external `fpcalc` regardless — see `fingerprints.md` |
| `web` | present (package dir) | import as `web` |
| `missing`, `unimported`, `mbsync`, `discogs`, `smartplaylist`, `mpdupdate`, `filefilter`, `permissions` | present | filefilter takes `path:` regex; in 1.6.0 a filtered file is skipped from the import task — the *runner* quarantines it afterwards |

Check any plugin before configuring it:

```bash
ls /usr/share/beets/beetsplug/ | grep -i NAME   # or wherever beet lives
```

## 5. Format naming: beets calls WAV files `WAVE`

`$format` for a `.wav` file is `WAVE`, not `WAV`. Any mapping keyed on the
string `WAV` silently misses the entire WAV tier (caught live: 1,270 files
ranked bottom-tier instead of top). Match both names in whatever injects or
renders quality:

```python
rank = 3 if fmt in ('WAV', 'WAVE') else 2 if fmt == 'FLAC' else 1
```

## 6. Verify attribute writes through beets' read path

After external writes (raw SQL, crashed writers, ORM from another process),
raw SQLite and beets can **disagree** — beets may serve a stale snapshot even
with `integrity_check` passing and no WAL files present. Observed live: SQLite
said all 13,318 items had the new field; `beet ls` rendered the pre-crash
state. A re-run of the write through the beets ORM reconciled both views.

Rule: after any bulk write, verify with `beet ls -f '$field' | sort | uniq -c`,
not just SQL.

## 7. The `import -A` flag means asis (no tagging)

`-A/--aset` = import **as-is**, skipping MusicBrainz autotag. Docs and blog
posts frequently mis-describe this. For quiet autotagging: `beet import -q`
with `autotag: yes` in config. Decide tag policy explicitly before any
import; never assume a flag from memory.

## 8. `pgrep -f` self-matches monitoring scripts

`pgrep -f "beet.*import"` matches any process whose command line *contains*
that pattern — including a Python script whose source embeds
`from beets.library import ...`. Use `pgrep -af` and eyeball, or match the
exact binary path (`pgrep -f "^/bin/beet"`).
