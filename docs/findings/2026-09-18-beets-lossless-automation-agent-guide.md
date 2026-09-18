# Beets Lossless Automation Agent Guide

## Purpose

Operate a Beets-managed lossless music library with minimal human intervention. The agent imports files, identifies metadata, normalizes tags, analyzes loudness, fetches artwork, embeds artwork, detects duplicates, favors better-quality copies, validates results, and generates derivatives — while preventing a lossy file or a misleading bitrate comparison from silently replacing a better archive copy.

The agent is authorized to make changes inside the configured Beets library. It must not delete source or library audio as part of routine automation; quarantine is the default disposition for rejected, unreadable, ambiguous, or superseded files.

This guide does not replace backups. Before enabling automated moves, ensure the database, library, inbox, processed archive, and quarantine roots are covered by a separate backup policy.

## Managed roots

```text
/srv/music/00-inbox       New source material awaiting processing (a queue, not storage)
/srv/music/20-library     Canonical Beets-managed library
/srv/music/30-derivatives Disposable listening copies
/srv/music/90-quarantine  Non-destructive holding area
/srv/music/95-processed   Successfully handled source originals
/srv/music/metadata       Beets database, logs, manifests, state
```

The `00-inbox` is a queue, not permanent storage. With `import.copy: yes`, Beets copies a successful import into the canonical library; it does not drain the inbox. The automation runner must archive source candidates only after it has recorded a successful, verified outcome.

## Operating assumptions

- Beets is installed and available as `beet`; confirm the active configuration path with `beet version` and `beet config -p` before editing it.
- The main library is a Beets-managed directory.
- The inbox contains files ready for automated processing.
- Lossless formats are preferred for the canonical library.
- WAV files are accepted and rank above FLAC when the configured quality policy says so — but see the WAV caveats in Edge cases.
- Lossy files are only imported when the configuration explicitly allows them; the `filefilter` block enforces this at import time. Weakening the archive profile to permit lossy requires a separately reviewed configuration, not an inline edit.
- The agent may move, rename, retag, overwrite, quarantine, and archive files inside configured managed directories. It never deletes originals — imported files are archived, quarantined files are held for a retention policy.
- The agent must not touch paths outside configured inbox, library, derivative, quarantine, and archive roots.

## Configuration template

Adapt paths and plugin availability to the local system.

```yaml
directory: /srv/music/20-library
library: /srv/music/metadata/beets.db

# Long classical/compilation titles can exceed media-server and share limits.
max_filename_length: 180

plugins:
  - musicbrainz
  - fetchart
  - embedart
  - scrub
  - zero
  - duplicates
  - info
  - convert
  - badfiles
  - replaygain
  - filefilter
  - permissions

# NOTE on quoting: these are YAML single-quoted strings, in which the
# backslash is NOT an escape character. Use single backslashes so the
# regex engine receives \. \s \x00 etc. Doubling them silently changes
# what the expressions match.
replace:
  '[\\/]': _
  '^\.': _
  '[\x00-\x1f]': _
  '[<>:"\?\*\|]': _
  '\.$': _
  '\s+$': ''
  '^\s+': ''
  '^-': _

art_filename: cover

import:
  copy: yes
  move: no
  link: no
  hardlink: no
  write: yes
  timid: no
  resume: yes
  incremental: yes
  quiet: yes
  detail: no
  log: /srv/music/metadata/import.log
  # What quiet mode does with no confident match: `skip` leaves the
  # candidate untouched in the inbox so the runner can move it to the
  # deferred queue. The alternative is `asis`, which imports with
  # existing tags — only use that if you accept unresolved material
  # entering the canonical library.
  quiet_fallback: skip
  # Duplicate resolution is deferred entirely to the daily quality-ranked
  # dedup pass. `upgrade` decides by raw bitrate alone (no lossless/lossy
  # distinction), which can replace a lossless original with a lossy
  # derivative. With quiet: yes, duplicates are skipped during import
  # regardless, so `skip` just makes the intent explicit.
  duplicate_action: skip
  duplicate_verbose_prompt: no
  from_scratch: no
  autotag: yes
  # Never enable this. Originals are archived by the agent loop, not
  # deleted by the importer.
  delete: no

match:
  preferred:
    countries: ['CA', 'US', 'GB']
    media:
      - 'Digital Media|File'
      - 'CD'
      - 'Vinyl'
    original_year: yes
  max_rec:
    missing_tracks: medium
    unmatched_tracks: medium

paths:
  default: $albumartist/$album%aunique{}/$disc-$track $title
  comp: Compilations/$album%aunique{}/$disc-$track $title
  singleton: Non-Album/$artist/$title
  albumtype:soundtrack: Soundtracks/$album%aunique{}/$disc-$track $title

# Enforce "lossless only unless explicitly allowed" at import time.
# (?i) matters: real-world files arrive as .FLAC and .Wav as often as
# lowercase. This is a policy guard, not codec verification — Step 2
# ffprobe inspection remains authoritative for misnamed files.
# ALAC-in-m4a is excluded by default because the extension cannot
# distinguish ALAC from AAC; allow `.m4a` only in a separately reviewed
# profile that trusts the codec inspection to quarantine lossy m4a.
filefilter:
  path: '(?i).*\.(flac|wav|bwf|aif|aiff|ape|wv)$'

fetchart:
  auto: yes
  cautious: yes
  minwidth: 1000
  maxwidth: 2000
  max_filesize: 12000000
  # Also available: enforce_ratio (reject non-square art) and quality
  # (JPEG compression when maxwidth resizes). Enable per the artwork
  # policy if square-only art is required.

embedart:
  auto: yes
  ifempty: yes
  # compare_threshold skips re-embedding a visually identical image —
  # useful for idempotent re-runs. Tune before enabling.
  # compare_threshold: 20

scrub:
  auto: yes

zero:
  auto: yes
  fields: comments
  comments:
    - '.*ripped by.*'
    - '.*encoded by.*'
    - '.*downloaded from.*'
    - '.*Exact Audio Copy.*'
    - '.*LAME.*'

duplicates:
  count: yes
  strict: yes
  # Pinned off. Duplicate losers are quarantined by the agent loop with a
  # recorded winner/loser manifest, never deleted by the plugin.
  delete: no

# The ffmpeg backend computes EBU R128 values and covers FLAC/WAV/Opus.
# The default `command` backend only handles mp3gain/aacgain — it cannot
# analyze a lossless library at all. `peak: sample` trades a little
# accuracy for much faster analysis on large batches (true-peak mode is
# roughly an order of magnitude slower).
replaygain:
  auto: yes
  backend: ffmpeg
  peak: sample
  overwrite: no
  parallel_on_import: yes

# Corruption checks at import time. The import_action_* keys matter for
# unattended runs: both default to `ask`, which stalls a quiet import.
badfiles:
  check_on_import: yes
  import_action_on_error: skip
  import_action_on_warning: continue

# Fix ownership/permissions after import so media-server processes can
# read everything beets writes on shared storage. If group write access
# is required, use a reviewed mode such as 664/775 here rather than
# applying chmod ad hoc after the fact.
permissions:
  file: 644
  dir: 755

convert:
  dest: /srv/music/30-derivatives
  embed: yes
  write_metadata: yes
  never_convert_lossy_files: yes
  force: no
  format: opus
  # Pin encoder settings so derivative regeneration is deterministic
  # and the fingerprint-based idempotence check is meaningful:
  # formats:
  #   opus: ffmpeg -i $source -y -vn -codec:a libopus -b:a 192k $dest
```

ReplayGain analysis writes loudness metadata only — it does not transcode canonical audio.

## Authority and precedence

Use the following precedence when deciding which metadata to keep:

1. Explicit user or deployment configuration.
2. MusicBrainz release and track identifiers.
3. Existing metadata when it does not conflict with a confident canonical match.
4. Filename, directory, and cue-sheet evidence.
5. Agent inference.

Never invent MusicBrainz IDs, release dates, artist credits, or provenance. If no reliable match exists, retain the existing metadata, mark the item as unresolved, and continue with safe normalization.

A confident album match normally has compatible artist and title evidence, a plausible release type, consistent track count and disc layout, and no similarly plausible competing release. Treat deluxe editions, remasters, live records, compilations, bootlegs, mixtapes, and local or underground releases as higher-risk matching cases.

## Quality policy

Use this quality preference for duplicate decisions — and only after establishing that the files represent the same recording:

```text
WAV/BWF: 500
FLAC:    400
ALAC:    390
APE:     380
WavPack: 370
Opus:    300
AAC:     250
MP3:     200
Ogg:     150
Unknown: 0
```

Quality comparison order:

1. Verified matching MusicBrainz track ID.
2. Lossless over lossy.
3. Evidence of source provenance and absence of a lossy transcode.
4. `quality_rank`.
5. Bit depth.
6. Sample rate.
7. Bitrate.
8. File size.
9. Tag completeness, and only as a final tie-breaker, recency.

Never treat size, bitrate, sample rate, or a WAV container alone as proof of quality. A WAV made from an MP3 is not an archive upgrade; a FLAC compressed at a different level is not necessarily a better copy. If provenance cannot be established and the selection remains ambiguous, retain both candidates and defer the group for review rather than guessing.

The importer never decides upgrades. `duplicate_action: skip` means every duplicate decision — including WAV-over-FLAC and other format-specific preferences — is made by the daily dedup pass using the ranking above. Beets' native `upgrade` action compares raw bitrate only, with no lossless/lossy distinction, so it is deliberately not used.

## Inbox processing loop

Run the following loop whenever files appear in the inbox.

Shell safety rules, which apply to every command in this guide:

- Always quote path variables: `mv -- "$file" "$dest/"`.
- Use `find -print0` with `xargs -0` or `while IFS= read -r -d '' f` — never word-split paths. Music filenames routinely contain apostrophes, ampersands, and Unicode.
- Pass `--` before file operands (where the tool supports it) so filenames beginning with `-` are not parsed as flags.

### Step 1: Discover

```bash
find /srv/music/00-inbox -type f -print0
```

Ignore:

- Hidden files.
- Temporary editor and transfer files.
- Images not associated with an album.
- Playlist files unless playlist handling is configured.
- Files outside the allowed audio extensions.

Allowed extensions for classification:

```text
.wav .bwf .flac .alac .ape .wv .opus .m4a .aac .mp3 .ogg
```

Extensions are only a first-pass classification; codec inspection is authoritative. Import eligibility is narrower than classification: the `filefilter` block in the configuration controls which of these actually reach the library.

### Step 2: Inspect codecs

Use `ffprobe` or Beets fields to determine the actual codec and technical properties.

```bash
ffprobe -v error -select_streams a:0 \
  -show_entries stream=codec_name,sample_rate,bits_per_raw_sample,bit_rate,channels,duration \
  -of default=noprint_wrappers=1:nokey=0 "$FILE"
```

Classify each file as:

- Lossless PCM/container.
- Lossless compressed.
- Lossy.
- Unknown or unreadable.

Files whose codec contradicts their extension (an MP3 stream in a `.flac` file, or a re-encoded "FLAC" with a 16 kHz cutoff characteristic of a lossy source) are treated as their actual codec, not their extension, and follow the lossy quarantine path.

Quarantine unreadable files automatically, and record the original path, error output, destination, timestamp, and run ID in the quarantine manifest:

```bash
mkdir -p /srv/music/90-quarantine/unreadable
mv -- "$FILE" /srv/music/90-quarantine/unreadable/
```

Quarantine lossy files that arrive while the `filefilter` policy excludes them, rather than importing them:

```bash
mkdir -p /srv/music/90-quarantine/lossy
mv -- "$FILE" /srv/music/90-quarantine/lossy/
```

### Step 3: Group imports

Group files into album candidates using:

- Parent directory.
- Existing album and albumartist tags.
- Disc and track numbers.
- Playlist or cue-sheet information.
- Filename patterns.

Process a source directory as one candidate unless tags, disc/track numbering, or a cue sheet clearly establishes a different release boundary. Do not combine unrelated source directories based only on similar names, and do not combine files from separate source directories unless their metadata clearly indicates one release.

Cue-sheet + single-file rips. A common lossless-library case is one FLAC/WAV file plus a `.cue` sheet representing an entire disc. The grouping and import steps above assume per-track files, so handle this explicitly:

1. Detect a `.cue` file in the candidate directory before ordinary grouping. Do not import the image as a one-track album when the cue sheet represents multiple tracks.
2. Validate that the cue references the image file and that the image decodes.
3. Split to a staging directory using a reviewed cue-aware tool. The standard toolchain is `shntool` (shnsplit) plus `cuetools` (cuetag):

```bash
shnsplit -f ALBUM.cue -o flac ALBUM.flac
```

4. Pre-tag the split files from the cue sheet so grouping and autotagging have real metadata to work with:

```bash
cuetag ALBUM.cue split-track*.flac
```

5. Verify track count, boundaries, tags, and output decoding before importing the staged tracks.
6. Keep the original single file, the cue sheet, and any rip log in the archive (Step 6), and import the split tracks as the album.
7. If splitting fails, is ambiguous, or would overwrite an existing staged set, defer the entire group. Do not discard the source image or cue, and do not invent track boundaries by time.

Beets also ships a built-in `cue` plugin that automates cue-sheet import, but it currently only handles WAV images and still requires `shnsplit` under the hood — the staged manual flow above remains the primary path for FLAC images.

### Step 4: Preview metadata

Run:

```bash
beet import --pretend /srv/music/00-inbox/CANDIDATE
```

If the installed Beets version does not support a useful preview for the selected operation, inspect with:

```bash
beet info /srv/music/00-inbox/CANDIDATE
```

Use the preview to detect unexpected grouping, duplicate handling, and poor metadata matches. A no-prompt deployment should still preserve the preview output in the batch log.

### Step 5: Autotag

Run the import automatically:

```bash
beet import -q /srv/music/00-inbox/CANDIDATE
```

Use the MusicBrainz match when:

- Artist and album match strongly.
- Track count is consistent.
- Track titles have high agreement.
- The release type is plausible.
- The media format and country preference are reasonable.

Reject or defer the match when:

- More than one release has similarly high confidence.
- Track count differs substantially.
- The candidate is a remix, deluxe edition, live release, or compilation when the source appears to be a standard album.
- The source is a bootleg, obscure underground release, mixtape, or local release without a reliable MusicBrainz match.

After the import command finishes, verify the exit status, inspect the import log, and confirm the expected items exist in the library. With `quiet: yes` and `duplicate_action: skip`, imports that match existing items may be skipped rather than upgraded — record that disposition explicitly in the batch report.

Unresolved candidates follow `quiet_fallback: skip`: they are left untouched in the inbox. The runner moves them to the dated deferred location rather than importing them with guessed metadata. (If you switch to `quiet_fallback: asis`, they import with existing tags into the normal paths — only do this deliberately.) Never treat "left in the inbox" as a terminal state; every candidate must end the run with a recorded disposition: imported, skipped-duplicate, deferred, quarantined, or archived.

### Step 6: Archive processed originals

`copy: yes` with `move: no` means originals remain in the inbox after a successful import. Without an explicit archive step, the discovery/grouping/preview cycle re-touches every leftover file every run and the inbox grows without bound. Only after the import outcome has been recorded and library-side verification succeeds, move the whole candidate directory to a dated, collision-resistant archive destination — never delete it:

```bash
processed="/srv/music/95-processed/$(date -I)/run-$RUN_ID"
mkdir -p -- "$processed"
mv -- "$CANDIDATE" "$processed/"
```

Record a manifest entry for each move containing:

- Original path.
- Archive path.
- Beets item or album IDs.
- Timestamp.
- Agent run ID.

Do not archive a candidate whose import partially failed, whose source-to-library mapping is unclear, or whose metadata remains unresolved. Move those candidates to a dated deferred or quarantine location and report why.

## Automated normalization

After a verified import batch, run only idempotent maintenance scoped to the imported items — use the import query or the recorded item IDs rather than sweeping the whole library:

```bash
beet update -q QUERY
beet write -q QUERY
beet scrub -q QUERY
```

ReplayGain analysis runs automatically on import (`replaygain.auto: yes`, parallel with `parallel_on_import: yes`). For items that arrive without gain tags, or after `beet write` regenerates tags, run:

```bash
beet replaygain
beet write -q
```

Use `zero` rules only for known unwanted fields. Do not apply a broad whitelist unless the configured player compatibility profile explicitly requires it. Query before removing tags when a field may carry useful provenance:

```bash
beet ls -a 'comments::*'
```

## Artwork workflow

Use `fetchart` with cautious selection and `embedart` with `ifempty: yes`.

The agent should:

1. Prefer artwork matching the selected release.
2. Prefer square artwork.
3. Prefer at least 1000 pixels on the long edge.
4. Reject tiny thumbnails and watermarked images when alternatives exist.
5. Save the external cover as `cover.jpg` or the configured filename.
6. Embed artwork only when no better existing embedded image is present.

Run:

```bash
beet fetchart -q QUERY
beet embedart -q QUERY
```

If artwork is missing, continue the import, add the album to the deferred report, and run a later artwork pass. An artwork failure must never block audio import.

## Deduplication workflow

### Detection

First use MusicBrainz track IDs:

```bash
beet duplicates -k mb_trackid -F -p \
  -f '$mb_trackid | $format | $bitrate | $samplerate | $bitdepth | $path'
```

For items without MusicBrainz IDs, use normalized metadata with explicit `-k` keys. Without `-k`, the plugin falls back to its default keys (`mb_trackid`/`mb_albumid`), which defeats the purpose of this pass:

```bash
beet duplicates -k albumartist -k album -k title -F -p \
  -f '$albumartist | $album | $disc | $track | $title | $format | $bitrate | $path'
```

For content-identical copies that differ only in tags (retagged or re-ripped releases), a checksum pass groups by file content regardless of metadata:

```bash
beet duplicates -C sha256sum -F -p \
  -f '$albumartist | $album | $title | $format | $path'
```

With `duplicates.strict: yes`, incomplete key fields prevent a comparison. Treat an empty result from this pass as "no strict match found," not proof that two untagged tracks are distinct.

### Selection

For every duplicate group, generate the decision report before moving anything:

```bash
beet ls -a -f \
  '$id|$mb_trackid|$albumartist|$album|$disc|$track|$title|$format|$bitrate|$samplerate|$bitdepth|$filesize|$path'
```

Then, for every group:

1. Exclude unreadable files.
2. Prefer complete files over partial files.
3. Prefer matching MusicBrainz IDs.
4. Apply `quality_rank`.
5. Compare bit depth, sample rate, bitrate, and file size.
6. Prefer the copy with the most complete metadata.
7. Keep one winner.
8. Move all losers to quarantine.
9. Remove or update Beets database entries only after the filesystem move has completed and been verified.

### Quarantine

Use a quarantine directory rather than direct deletion:

```bash
mkdir -p /srv/music/90-quarantine/duplicates
```

Move losers to a structured location:

```text
90-quarantine/duplicates/YYYY-MM-DD/<reason>/...
```

Record a manifest containing:

- Original path.
- New path.
- Kept path.
- Match key.
- Quality comparison.
- Timestamp.
- Agent run ID.

Delete quarantined files only when the retention policy allows it. Do not invoke the duplicates plugin's own deletion automation.

## Quality ranking implementation

If Beets exposes a custom field, create `quality_rank` during import. If not, the agent must calculate ranking externally from `beet ls -f` and use the resulting report to choose files.

Do not assume that lexical sorting of `$format` implements the quality policy. `WAV`, `FLAC`, and `MP3` must be mapped to explicit numeric ranks.

## Validation

After every import batch, use the `badfiles` plugin, which runs format-specific corruption checkers (`flac -t`, `mp3val`, and similar) over the library. With `check_on_import: yes`, corrupt files are already rejected at import time; this pass catches later corruption:

```bash
beet bad
beet stats
```

If a checker for a given format is unavailable locally (WAV/BWF in particular), fall back to the equivalent manual checks:

```bash
find /srv/music/20-library -type f -iname '*.flac' -print0 |
  xargs -0 -r -n1 flac -t
```

```bash
find /srv/music/20-library -type f \
  \( -iname '*.wav' -o -iname '*.bwf' \) -print0 |
  xargs -0 -r -n1 ffmpeg -v error -i
```

If validation fails:

1. Move the failing file to quarantine.
2. Preserve the failure output in the operation manifest.
3. Mark the corresponding Beets item as invalid.
4. Search for another copy in the inbox or duplicate set.
5. Do not silently replace the file with a lossy derivative.

## Derivative generation

Generate derivatives only from verified canonical lossless items:

```bash
beet convert --pretend -q -a \
  -d /srv/music/30-derivatives \
  --format opus 'format:FLAC OR format:WAV'
```

Then run:

```bash
beet convert -q -a \
  -d /srv/music/30-derivatives \
  --format opus 'format:FLAC OR format:WAV'
```

Never convert a lossy file into a format that is presented as an archive master. Regenerate derivatives only when the source fingerprint or conversion settings changed, and write derivatives via temporary output followed by an atomic rename where the conversion tooling permits it.

## Optional plugins and add-ons

These are not part of the baseline policy, but each solves a problem this guide handles manually or defers entirely. Evaluate each against the minimal-intervention principle before enabling.

### Library hygiene (core plugins)

- `missing` — lists albums whose track count is lower than the release expects. Automates the "incomplete album" deferral check: `beet missing -a`. Wire into the daily pass instead of hand-rolling track-count logic.
- `unimported` — lists files under the library directory that are not in the database. Run after archive/sync operations to catch stray files that landed in `20-library` outside of beets. Configure `ignore_extensions` (e.g. `jpg png log`) and `ignore_subdirectories` for cover art and metadata sidecars.
- `mbsync` — re-fetches MusicBrainz metadata for items already in the library. Useful for the hourly deferred-retry pass: deferred matches can be retried with fresher MusicBrainz data via `beet mbsync QUERY` before re-attempting import decisions.

### Acoustic identification (core plugins)

- `chroma` — AcoustID fingerprinting (requires `pyacoustid` and an API key). With `chroma.auto: yes`, tracks get fingerprinted during import, which can rescue mistagged or unnamed files before they hit the deferred queue. `beet chromasearch` can identify duplicates by acoustic identity regardless of tags — a stronger signal than metadata matching for the dedup pass, at the cost of the AcoustID lookup.
- `fingerprint` — the lower-level companion that submits/computes fingerprints, useful with `mbsubmit` to contribute matches for underground releases back to MusicBrainz.

### Metadata enrichment (core and community)

- `discogs` — Discogs as an autotagger fallback. Frequently better than MusicBrainz for vinyl rips, bootlegs, and small-label electronic releases. Runs automatically as a fallback source during import when enabled.
- `bandcamp` — parses Bandcamp release pages into structured metadata. Strong fit for underground and independent intake where Bandcamp is the canonical release page and MusicBrainz coverage is thin.
- `deezer`, `spotify` — additional metadata fallback sources; useful mainly for genre/popularity fields.
- `lastgenre` — Last.fm genre tags written into a configurable field; nice for filtering smart playlists, noise for archive purists.
- `lyrics` — fetches and embeds lyrics; optional, file-format dependent.

### Serving and integration (core and community)

- `smartplaylist` — writes m3u playlists from stored queries (`name` + `query` pairs) into a playlist directory. Pairs well with MPD or any media server that scans playlist files; regenerate after import batches.
- `mpdupdate` — signals an MPD instance to rescan after changes. Community equivalents exist for other media servers (e.g. `subsonicupdate` for Subsonic-based servers).
- `web` — embeds a REST/JSON API over the library. Handy for dashboards or the agent's own reporting if the SQLite queries become awkward.

### External tools

- `beets-check` (community) — computes and stores per-file checksums in the library, then verifies them on subsequent runs. Stronger than `badfiles` for slow bit-rot detection, since it detects silent corruption in files that still decode. Sits naturally in the weekly schedule.
- `beets-container` (community) — prebuilt container image bundling beets plus common plugins. Relevant if the `music-acquisition` stack should stay dockerized rather than installing beets into the host.
- `cue` (core, limited) — automatic cue-sheet import, currently WAV-image-only and dependent on `shnsplit`. The staged manual flow in Step 3 remains primary.

When adding any metadata source, MusicBrainz stays primary; other sources act as fallbacks, and their suggestions still pass through the same authority and precedence rules — a Discogs or Bandcamp match never overrides a confident MusicBrainz ID.

## Error handling

Classify errors as:

### Retryable

- Temporary MusicBrainz/network failure.
- Artwork provider timeout.
- Database lock.
- Temporary filesystem busy error.

Retry with exponential backoff up to three times.

### Deferrable

- No confident metadata match.
- Missing artwork.
- Unsupported but readable format.
- Incomplete album.
- Cue-splitting uncertainty.
- Ambiguous duplicate group.

Move the item to a deferred queue and continue processing other items.

### Fatal

- Path escapes configured roots.
- Database corruption.
- File cannot be decoded (affecting an in-progress candidate).
- Destination collision cannot be resolved.
- Command would delete or modify outside the allowed roots.

Stop the current batch and report the exact failure. Reporting means a concrete sink, not a silent log line:

1. Append to `/srv/music/metadata/fatal.log` a single-line, grep-able record:

```text
BEETS_AGENT_FATAL <ISO-8601 timestamp> run_id=<id> stage=<step> path=<quoted path> error=<exact message>
```

2. When `$MUSIC_AGENT_FATAL_WEBHOOK` is set, POST the same payload there.
3. A fatal error is not considered handled until it appears in the sink. Do not continue the batch, and do not archive its inputs.

The notifier must be tested at deployment time. A fatal event that only appears in an unmonitored log is not an operational alert.

## Idempotence rules

The agent must be safe to run repeatedly.

- Track candidates and operations by stable source identity, Beets item ID, or content hash.
- Do not re-import files already present in the Beets database, and do not re-import a source already recorded as imported, skipped as a duplicate, deferred, processed, or quarantined unless an operator explicitly requeues it.
- Archived originals are never re-imported: the incremental import log plus the archive move (Step 6) removes them from the inbox, so discovery no longer touches them after a successful run.
- Do not overwrite artwork when `embedart.ifempty` prevents replacement.
- Do not regenerate derivatives when the source fingerprint and settings are unchanged.
- Do not move a quarantined file twice.
- Use temporary filenames and atomic renames when creating reports.
- Treat the filesystem move and the manifest/database update as a recoverable transaction: on restart, reconcile incomplete operations before processing new input.

## Scheduled jobs

Recommended schedule:

```text
Every 5 minutes: scan inbox, process new candidates, archive imported originals.
Hourly: retry deferred metadata and artwork tasks; run beet replaygain on items missing gain tags.
Daily: run beet bad, beet stats, and the duplicate detection plus quality-ranked dedup pass.
Weekly: regenerate derivative files that are missing or stale; run beet missing
       (incomplete albums) and beet unimported (stray files in the library root).
Monthly: review quarantine retention; prune only under an approved retention policy.
```

Example daily commands:

```bash
beet bad
beet stats
beet duplicates -k mb_trackid -F -p
beet duplicates -k albumartist -k album -k title -F -p
```

## Agent decision output

For every batch, produce a concise report:

```text
Batch: 2026-09-18T04:00:00-04:00
Run ID: 6df8b2f4
Imported: 12 albums, 143 tracks
Skipped as existing duplicates: 3 tracks
Updated: 3 existing tracks
Quality upgrades: 2 WAV, 1 FLAC
Quarantined: 4 duplicates, 1 unreadable file
Processed-source archives: 12 candidates
Archived: 12 albums to 95-processed/2026-09-18/run-6df8b2f4
Artwork: 10 embedded, 2 deferred
Metadata: 11 MusicBrainz matches, 1 unresolved
Validation: passed
Errors: none
```

For each unresolved item, include:

- Source path.
- Current metadata.
- Reason for deferral.
- Suggested next action.

## Hard prohibitions

- Never delete files outside configured roots.
- Never set `import: delete: yes` in the configuration. Deleting originals on import is a config key, not a CLI flag, and must stay off; archiving is the agent loop's job.
- Never set `duplicates: delete: yes` or invoke the duplicates plugin's `--delete`.
- Never pass `-L`/`--library` to `beet import`. It treats arguments as a query over the existing library and retags matching items instead of importing from the inbox — an incautious query could touch the entire library.
- Never use the native importer upgrade behavior as the archive-quality decision mechanism.
- Never treat upsampled or transcoded files as higher-quality originals.
- Never replace a lossless file with a lossy derivative.
- Never use a filename alone to decide that two files are duplicates.
- Never discard a duplicate without recording the winner and loser.
- Never invent release IDs, artist credits, or dates.
- Never let an artwork failure block audio import.
- Never let a fatal failure remain only in an unmonitored log.

## Edge cases and known pitfalls

- **`quiet_fallback` decides the unresolved path.** The default (`skip`) leaves unmatched candidates in the inbox — if you assumed "unresolved items are imported with existing metadata," that only happens with `asis`. Set it explicitly; the runner's deferred-queue workflow assumes `skip`.
- **Extension case.** Without `(?i)` in the `filefilter` regex, `Album.FLAC` is filtered out and `.flac` passes. Real-world intake has both.
- **Codec ≠ extension.** A `.flac` file containing an MP3 stream passes `filefilter`. Step 2 ffprobe inspection is the authoritative classification; treat spectral/transcode evidence as lossy regardless of container.
- **WAV as canonical storage is weak.** Beets' default `replaygain` `command` backend (mp3gain/aacgain) cannot analyze FLAC or WAV at all — use the `ffmpeg` backend. WAV tagging support and player compatibility are also poorer than FLAC's. The quality table still ranks WAV above FLAC for comparing like-for-like sources, but converting a WAV master to FLAC for canonical storage is a legitimate normalization, not a downgrade — it is lossless-to-lossless. FLAC is the recommended canonical container; retain WAV originals in the archive.
- **ReplayGain true-peak mode is slow.** The ffmpeg backend's default `peak: true` is roughly an order of magnitude slower than `peak: sample`. On large backfill batches, `sample` is the pragmatic choice; re-analyze with true peaks only for material where clipping accuracy matters.
- **Disc-number padding.** `$track` is zero-padded; `$disc` is not. A 10+ disc box set sorts disc `10` before disc `2` under `$disc-$track`. Rare, but known.
- **Stale resume state after a crash.** `resume: yes` stores per-directory progress. After a fatal or partial failure, re-running may skip files recorded as processed. Clear the resume state (or run once with `resume: no`) when reprocessing a candidate after a fatal error, and let the recoverable-transaction rule reconcile the manifest first.
- **Strict duplicates silence.** `strict: yes` drops comparisons with unset key fields. Two identical untagged files report as non-duplicates under metadata keys — that is why the MusicBrainz-key pass and checksum pass exist alongside the metadata pass.
- **Checksum duplicates are exact-content only.** `-C sha256sum` groups bit-identical files; different pressings, encodes, or even tag-only differences produce different hashes. Use it to catch retagged copies, not as the primary quality comparison.
- **Convert determinism.** If encoder settings drift (default bitrate changes between ffmpeg versions), the fingerprint-based regeneration check will see every derivative as stale. Pin `convert.formats` so regeneration is reproducible.
- **`beet import -L` retags, it does not import.** Any query passed with `-L` is evaluated against the existing library. The automation loop never uses it.

## Minimal automation commands

```bash
# Inspect installation
beet version
beet config -p

# Preview inbox
beet import --pretend /srv/music/00-inbox

# Run automated import
beet import -q /srv/music/00-inbox

# Normalize, analyze, and validate
beet update -q
beet write -q
beet replaygain
beet bad
beet stats

# Find duplicate groups
beet duplicates -k mb_trackid -F -p
beet duplicates -k albumartist -k album -k title -F -p

# Library hygiene (if the optional plugins are enabled)
beet missing -a
beet unimported

# Generate derivatives
beet convert --pretend -q -a -d /srv/music/30-derivatives --format opus 'format:FLAC OR format:WAV'
```

## Final operating principle

In full-automation mode, optimize for throughput while preserving the ability to identify what happened, and preserve reversibility and evidence. Automatically import, tag, clean, analyze loudness, artwork, upgrade, quarantine, validate, and convert. Defer only cases where the agent cannot determine a safe winner or a reliable metadata match. Make irreversible decisions only when a separately approved retention policy authorizes them.

## Changelog

Revision 3 (edge-case and optional-plugin pass):

- Added `import.quiet_fallback: skip` with explicit semantics; reconciled Step 5 unresolved handling with it and added the every-candidate-gets-a-disposition rule.
- Added `(?i)` to the `filefilter` regex — uppercase extensions were silently excluded.
- Wired `fetchart.minwidth: 1000` (matching the stated artwork policy) and noted `enforce_ratio`/`quality`; noted `embedart.compare_threshold` for idempotent re-embedding.
- Documented the replaygain backend trap: the default `command` backend only supports mp3gain/aacgain and cannot analyze a lossless library; set `backend: ffmpeg`, `peak: sample`, `parallel_on_import: yes`.
- Added a checksum-based duplicates detection pass (`-C sha256sum`) and its limits.
- Added `convert.formats` pinning note for deterministic derivative regeneration.
- Expanded cue handling: `shnsplit`/`cuetools` toolchain, `cuetag` pre-tagging of split files, and the built-in `cue` plugin's WAV-only limitation.
- Added misnamed-file handling (codec vs extension) to Step 2.
- Added stale-resume-state guidance after fatal failures.
- Added the "Optional plugins and add-ons" section (`missing`, `unimported`, `mbsync`, `chroma`, `fingerprint`, `discogs`, `bandcamp`, `deezer`/`spotify`, `lastgenre`, `lyrics`, `smartplaylist`, `mpdupdate`, `web`, `beets-check`, `beets-container`, `cue`) with guidance that MusicBrainz remains the primary metadata source.
- Added the "Edge cases and known pitfalls" section, including WAV-as-canonical caveats, true-peak slowness, disc padding, strict-silence, and checksum-duplicate limits.

Revision 2 (merged from the reviewed alternative guide):

- Added the managed roots table and the backup-coverage caveat.
- Added `duplicates: delete: no` (pinned off) and `badfiles: check_on_import: yes` with automation-safe `import_action_on_error`/`import_action_on_warning` settings — both default `ask`, which stalls quiet imports.
- Added the `filefilter` "separately reviewed profile" framing for permitting lossy input.
- Added provenance/transcode evidence as an explicit step in the quality comparison order, plus the "same recording first" precondition and the retain-both-when-ambiguous rule.
- Added the `strict: yes` empty-result interpretation caveat to duplicate detection.
- Added quarantine-manifest fields (including error output) for unreadable files.
- Expanded cue-image handling: validate the cue references a decodable image, split to a staging directory, verify track count/boundaries/tags before import, defer on ambiguity, never discard the source image or cue.
- Added preview-output preservation in the batch log, and post-import verification of exit status, import log, and recorded skip dispositions.
- Archive destinations are now collision-resistant (`run-<run-id>` subdirectories); partial failures go to a dated deferred/quarantine location instead of the archive.
- Normalization now scoped to the imported query or recorded item IDs instead of sweeping the whole library.
- Validation fallback commands now use `xargs -0 -r`; failure output is preserved in the manifest.
- Derivatives: regenerate only on source/setting change, write via temp file plus atomic rename.
- Fatal notifier must be tested at deployment; fatal marker renamed to `BEETS_AGENT_FATAL` with stage and path fields.
- Idempotence: added operator-requeue semantics, no-reimport of recorded dispositions, and the recoverable-transaction/reconcile-on-restart rule.
- Batch report gains Run ID and skipped-as-duplicate lines; hard prohibitions gain the duplicates-deletion, importer-upgrade, and unmonitored-fatal clauses.

Revision 1 (fixes from the source-code review):

- Fixed the `replace:` regex block: single backslashes in YAML single-quoted strings, so `\.`, `\s`, and `\x00-\x1f` reach the regex engine correctly. The previous double-escaped control-character rule matched digits and all uppercase letters and would have mangled track numbers, years, and capitalized names.
- Moved `original_year` into `match.preferred`, its actual location; the previous sibling placement was silently ignored.
- Changed `duplicate_action` from `upgrade` to `skip` and documented why: the native upgrade comparison is bitrate-only with no lossless/lossy distinction.
- Made `import.delete: no` explicit and corrected the hard prohibitions around `-L`/`--library`.
- Fixed the metadata-based duplicates command to pass explicit `-k` keys.
- Added the post-import archive step so the inbox drains without deletion.
- Wired `filefilter` so the lossless-only policy is enforced at import time.
- Added `badfiles`, `replaygain`, `permissions`, and `max_filename_length`.
- Added cue-sheet + single-file album rip handling to the grouping step.
- Made shell quoting rules explicit and applied them to every command.
- Defined a concrete fatal-error reporting sink.
