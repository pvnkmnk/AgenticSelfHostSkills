# Bulk attribute injection — the only pattern that scales

Injecting a flexible attribute into every item (quality_rank, tags_complete,
acoustid_fingerprint, ...) is a common need on asis-imported libraries. There
are three ways to do it; two are traps.

## ✓ The pattern: beets ORM, single transaction

```bash
PYTHONPATH=/usr/share/beets python3 <<'PYEOF'
from beets.library import Library

lib = Library('/root/.musiclibrary.db')     # EXACT path from `beet config -d`

# example: quality_rank by format tier (idols' policy: WAV > FLAC > lossy)
def rank(fmt):
    return 3 if fmt in ('WAV', 'WAVE') else 2 if fmt == 'FLAC' else 1

n = 0
with lib.transaction():                      # ONE transaction = one fsync
    for it in lib.items():
        it.quality_rank = rank(it.format)
        it.tags_complete = 1 if (it.albumartist and it.album and it.title) else 0
        it.store()
        n += 1
print("injected:", n)
PYEOF
```

**Measured: 13,318 items in 2.5 seconds.**

## ✗ Trap 1: stores without a wrapping transaction

`item.store()` commits (fsyncs) individually. 13,318 stores = 13,318 fsyncs
= **hours of D-state disk storming** on a 5400 RPM HDD, plus SQLite lock
contention that makes every concurrent `beet` command hang. Live-verified the
hard way: killed after an hour at ~10% progress, retried with the transaction
wrapper, finished in 2.5 s.

## ✗ Trap 2: raw SQL UPDATE works but can leave divergent views

A single `UPDATE items SET quality_rank = ...` is fast and SQLite-valid, but
beets can keep serving a **stale snapshot** afterward — even with
`integrity_check` clean and no WAL files present (root cause never fully
diagnosed; suspected lingering page cache from a crashed writer). SQLite
said all 13,318 rows updated; `beet ls` rendered the pre-write state for
4,255 of them. Re-running the write through the ORM reconciled both views.

Rule: **raw SQL is for emergencies; the ORM is the interface.** After any
bulk write — ORM or SQL — verify through beets' own read path:

```bash
beet ls -f '$quality_rank' | sort | uniq -c
```

not just through sqlite3.

## Gotchas

- **`Library()` path must be the real DB path from `beet config -d`.**
  Guessing `/root/.config/beets/library.db` yielded `matched=0` against a
  silently-created empty DB while the real library lived at
  `/root/.musiclibrary.db`. Zero matches on an injection run means wrong
  path until proven otherwise — check item count first
  (`sum(1 for _ in lib.items())`).
- **`PYTHONPATH`**: on non-standard installs (Debian package puts beets at
  `/usr/share/beets`) the system python3 can't import beets without it.
  Find the location from the `beet` wrapper: `head -5 $(which beet)`.
- **beets names WAV files `WAVE`** — any format mapping must match both
  `WAV` and `WAVE` or the WAV tier silently lands at the bottom rank.
- **Declare types** for injected fields used in tiebreak/queries:
  top-level `types: {quality_rank: int, tags_complete: int}` in config.yaml.
- **Query verification** of int flexible attributes can be surprising via
  string comparison — template rendering (`beet ls -f '$attr'`) is the
  reliable read-back.
- **`item.store()` with the ORM is what beets' own readers see.** If beets'
  view disagrees with SQLite after a crash-kill, re-run the write through
  the ORM to reconcile.
- `pgrep -f "beet.*import"` self-matches any script whose source contains
  `from beets.library import` — check `pgrep -af` output by eye.
