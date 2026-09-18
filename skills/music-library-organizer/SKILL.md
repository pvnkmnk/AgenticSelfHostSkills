---
name: music-library-organizer
description: Import, tag, and organize music files using beets; enforce consistent folder structure, metadata, and MusicBrainz tagging across the local music library.
---

# music-library-organizer

## Purpose
Automate music file tagging and library organization using beets. Ingests raw downloads, applies MusicBrainz-backed metadata, enforces directory structure, deduplicates, and prepares files for streaming via Subsonic/Navidrome.

## Invocation
- "Organize new music downloads with beets"
- "Tag and import [artist/album] into library"
- "Fix missing tags in music library"
- "Deduplicate music library"
- "Run beets import on download folder"

## Workflow Steps
1. **Scan:** Identify new files in the slskd download directory (or configured inbox).
2. **Import:** Decide tag policy explicitly first. `beet import -A` means **asis — beets imports WITHOUT MusicBrainz lookup** (opposite of auto-tag). For MusicBrainz-backed tagging run plain `beet import` (interactive) or `beet import -q` after confirming config; never assume `-A` tags anything.
3. **Review:** Flag low-confidence matches for manual review; log ambiguous items.
4. **Organize:** Move/copy files into the canonical library structure: `Library/Artist/Year - Album/Track - Title.ext`.
5. **Tag:** Apply standardized tags: artist, album, year, genre, MusicBrainz IDs, ReplayGain.
6. **Deduplicate:** Run `beet duplicates` and resolve conflicts (keep highest quality).
7. **Notify:** Signal `subsonic-media-server` to rescan library after import completes.
8. **Log:** Record import summary in `homelab-logbook`.

## Safety
- Never delete original files without explicit confirmation.
- Preserve original files in an inbox backup before moving.
- Do not overwrite manual tag edits without user approval.
- Validate file integrity (checksum) before and after move.

## MCP
- No dedicated MCP; invoked via shell commands or agent subprocess calls to `beet` CLI.
- Pairs with `slskd-mcp` for end-to-end acquisition-to-library pipeline.

## Dedup Strategy (verified on the homelab-core library)

1. **Fingerprints via local `fpcalc`, not the chroma plugin during import.** Chroma during import does a per-file AcoustID API round-trip (measured: 46s for 2 files → ~10 days for a 19k-track library). Local `fpcalc` runs ~2.5/sec offline; bulk-inject the results into the beets DB afterwards.
2. **`beet duplicates` is the native dedup engine.** Set keys `[acoustid_fingerprint, albumartist album title]` and tiebreak `[format, bitdepth, samplerate, bitrate]` (lossless > lossy → deeper → higher rate → higher bitrate). Use `--move` into a quarantine dir + `--log` for the report.
3. **Non-destructive policy (standing order):** quarantine duplicates with a report, never delete. Keep sources + a pre-change snapshot until the user approves.
4. **Disk-space check gates the merge:** if free space < staged size, merge must be a **move**, not a copy.
5. **AcoustID API lookups are for duplicate groups only** (~100s of calls), never the whole library. MusicBrainz needs no key; AcoustID needs a free key.

## Instance Addendum: CT 101 "homelab-core" (192.168.2.242)

- Access: `ssh root@192.168.2.242`; beets 1.6.0 / Python 3.11.2; DB `/root/.musiclibrary.db`
- Library volume: `/opt/homelab/navidrome/music` (590 GiB, watch free space)
- Config: `/root/.config/beets/config.yaml` — `autotag: no, write: no, copy: no, move: no` (asis import, zero file mutation); chroma configured with idols' AcoustID key
- Staging dir convention: `.staging-YYYYMMDD/` (hidden); rollback snapshot `pre-dedup-YYYYMMDD` on PVE
- Container facts: no `lsof`/`fuser` (use `/proc/*/fd` scanning); no ffprobe (beets DB already stores bitrate/depth/rate)
- Host is a 2-core/5400-RPM-HDD laptop — heavy beets/fpcalc work must run `nice -n 19 ionice -c3`, single-worker, with an `flock` lockfile so relaunches can't stack
- Navidrome runs in Docker on this CT — production; rescan via Subsonic API, never restart without asking
- Full verified state: `homelab music server library cleanup findings.md` (project root of DevWorks/homelab workspace)

## References
- beets documentation: https://beets.readthedocs.io/
- MusicBrainz: https://musicbrainz.org/
- beets GitHub: https://github.com/beetbox/beets

## Companion Skills
- `slskd-media-acquisition` — source of new music files
- `subsonic-media-server` — streaming target after organization
- `dj-library-curator` — curation layer on top of organized library
- `homelab-logbook` — import event logging
