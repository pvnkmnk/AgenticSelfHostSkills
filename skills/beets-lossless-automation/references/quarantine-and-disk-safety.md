# Quarantine placement and disk safety

Hard-won on a real run (CT 101, 2026-09-18). Read this before any
`beets duplicates --move`, before relocating a large tree, and any time a
library lives on its own volume but services live on the root filesystem.

## The rule

**The quarantine/move destination must be on the same filesystem as the library.**

```bash
LIB_DEV=$(stat -c %d /path/to/library)
Q_DEV=$(stat -c %d /path/to/quarantine)
[ "$LIB_DEV" = "$Q_DEV" ] || { echo "FATAL: cross-device move would copy, not rename"; exit 1; }
```

Put this guard *inside* the run script, before the first pass. It costs two
milliseconds and prevents the failure mode below.

Note that `findmnt -T PATH` tells you the mount, but `stat -c %d` comparing two
paths is the cheapest correct check — two paths can *look* adjacent in the
directory tree and still be on different volumes.

## What goes wrong (the incident)

Layout:

```text
/           32 GiB   ← root volume; Docker, Navidrome's DB, the beets DB
/opt/homelab/navidrome/music   590 GiB   ← separate volume; the library
```

Chosen quarantine: `/opt/homelab/navidrome/quarantine-dedup-…` — a **sibling of
the library mount point**, which looks "next to the library" but is on the
32 GiB root volume.

`beets duplicates --move` calls `item.move(basedir=…)`, which uses an ordinary
file move. Across filesystems that is copy+delete, so:

- 1,075 files (~27 GiB) were **copied** onto root until
  `No space left on device` (147 MB free), and the run died mid-pass;
- Docker, Navidrome's database and the beets database all live on that
  filesystem, so this was a live hazard for production services, not just a
  failed batch job;
- throughput was ~3–8 MB/s (spinning disk), where the same-volume equivalent
  would have been microseconds per file.

Two compounding mistakes worth naming:

1. **Placement by appearance.** "Beside the library" is not "on the library's
   volume". Only a device-id comparison answers it.
2. **All-at-once relocation.** The first recovery attempt copied everything and
   only removed the source afterwards, holding root at 100% for the whole copy
   (~100 minutes projected). `cp`-then-`rm` is the wrong shape under disk
   pressure.

## Recovery pattern (if it happens)

```bash
# 1. Move with per-file source removal so space is reclaimed continuously.
rsync -a --remove-source-files "$SRC/" "$DST/"

# 2. Verify BEFORE trusting it: counts and total size must match.
#    (rsync's default size+mtime check is adequate when the source mtimes
#     were preserved; skip -c to avoid reading both sides of a slow disk.)
find "$DST" -type f | wc -l
du -sh "$DST"

# 3. Only then drop the now-empty source tree.
find "$SRC" -depth -type d -empty -delete
```

Then reconcile the database:

```python
# Rows only — the files are safe in quarantine. delete=False is the default.
from beets.library import Library
lib = Library('/path/to/library.db')
targets = [it for it in lib.items() if b'quarantine-dedup-' in it.path]
with lib.transaction():
    for it in targets:
        it.remove(with_album=False)
```

Write the loser manifest into the quarantine directory itself
(`MANIFEST-*.txt` = the original paths from the pass output) so the move is
reversible without consulting logs.

## Why purging between passes matters

`--move` relocates the file and updates the DB path, but **the item stays in the
library**. A second pass (different keys) will therefore re-group those losers
with the very winners they lost to and move them again — if they are still in
the DB. Purging quarantined rows after each pass keeps every pass operating on
the real library. The files remain on disk; restore = move them back and
re-import.

## Verification checklist after any dedup pass

```bash
# arithmetic must close: before − moved = after
beet ls | wc -l
# no DB rows should point into the quarantine (after the purge)
beet ls -f '$path' | grep -c quarantine-dedup-  # expect 0
# quarantine file count should equal the loser-manifest line count
find "$Q" -type f | wc -l
# free space on BOTH volumes, and containers still healthy
df -h "$LIB" / ; docker ps --format '{{.Names}}: {{.Status}}'
```

A decode spot-check of moved files is not evidence either way when the moves
were renames (no data moves); it only tells you about pre-existing corruption.
Prefer `ffmpeg -v error -i FILE -f null -` when `flac`/`mp3val` are unavailable
— and expect a small pre-existing failure rate in any real-world collection.
