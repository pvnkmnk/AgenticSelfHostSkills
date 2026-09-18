# music-library-organizer

Automates music file tagging and library organization using beets — ingests raw downloads, applies MusicBrainz-backed metadata, enforces directory structure, deduplicates, and prepares files for streaming via Subsonic/Navidrome.

## Quick Start

Invoke via your agent: `Invoke music-library-organizer` (OpenCode/Codex) or `/skill music-library-organizer` (Freebuff).

## What it does

- Scans the slskd download directory (or configured inbox) for new files.
- Uses explicit beets import tag policies (`-A` = asis/no tagging; never assume it auto-tags).
- Flags low-confidence matches for manual review; logs ambiguous items.
- Moves/copies files into the canonical library structure: `Library/Artist/Year - Album/Track - Title.ext`.
- Applies standardized tags: artist, album, year, genre, MusicBrainz IDs, ReplayGain.
- Runs `beet duplicates` to detect and resolve conflicts (keeps highest quality).
- Signals `subsonic-media-server` to rescan the library after import completes.
- Records the import summary in `homelab-logbook`.

## Safety

- Never deletes original files without explicit confirmation.
- Preserves originals in an inbox backup before moving.
- Never overwrites manual tag edits without user approval.

## Dependencies

- beets installed and configured with MusicBrainz plugin
- slskd download directory or configured inbox path
- Optional: `subsonic-media-server` for post-import rescan

## Companion Skills

`slskd-media-acquisition` · `subsonic-media-server` · `dj-library-curator` · `homelab-logbook`

See [SKILL.md](./SKILL.md) for the full canonical specification.
