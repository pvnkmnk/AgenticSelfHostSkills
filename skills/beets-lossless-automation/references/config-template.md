# Config template — lossless library, automation-safe

Adapt paths and plugin availability locally. Blocks marked **[1.6.0-trap]**
are version-fragile — check `version-notes.md` before trusting them on a
different version. Verify plugin availability before enabling (`beet version`
first, always).

```yaml
directory: /srv/music/20-library
library: /srv/music/metadata/beets.db

# Long classical/compilation titles exceed media-server and share limits.
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
# backslash is NOT an escape character. Single backslashes reach the regex
# engine correctly; doubling them silently changes what matches.
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
  # [1.6.0-trap] incremental: yes silently disables resume (importer.py).
  # Pick one deliberately; incremental also changes re-import semantics.
  incremental: no
  quiet: yes
  detail: no
  log: /srv/music/metadata/import.log
  # What quiet mode does with no confident match. `skip` leaves the candidate
  # untouched in the inbox so the runner can move it to the deferred queue.
  # `asis` imports with existing tags — only if you accept unresolved material
  # entering the canonical library. Set it explicitly either way.
  quiet_fallback: skip
  # The importer must never decide upgrades. Native `upgrade` compares raw
  # bitrate only (no lossless/lossy distinction) and can replace a lossless
  # original with a lossy derivative. All duplicate decisions belong to the
  # quality-ranked dedup pass.
  duplicate_action: skip
  duplicate_verbose_prompt: no
  from_scratch: no
  autotag: yes
  # Never enable. Originals are archived by the agent loop, not deleted by
  # the importer.
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
# (?i) matters: files arrive as .FLAC and .Wav as often as lowercase.
# This is a policy guard, not codec verification — ffprobe inspection is
# authoritative for misnamed files. ALAC-in-m4a is excluded by default
# because the extension cannot distinguish ALAC from AAC.
filefilter:
  path: '(?i).*\.(flac|wav|bwf|aif|aiff|ape|wv)$'

fetchart:
  auto: yes
  cautious: yes
  minwidth: 1000
  maxwidth: 2000
  max_filesize: 12000000

embedart:
  auto: yes
  ifempty: yes

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

# [1.6.0-trap] keys: bare string, NOT a YAML list (silent zero-output).
# tiebreak: must nest under items: (flat mapping silently ignored).
# The tiebreak sorts descending on every field. tags_complete is an injected
# flexible attribute (see bulk-injection.md): tagged files beat blank-tagged
# twins so quality never loses to missing metadata.
duplicates:
  count: yes
  strict: yes
  keys: albumartist album title
  tiebreak:
    items: [tags_complete, quality_rank, bitdepth, samplerate, bitrate]
  delete: no          # pinned off; losers are quarantined by --move, never deleted

# The ffmpeg backend computes EBU R128 and covers FLAC/WAV/Opus. The default
# `command` backend (mp3gain/aacgain) cannot analyze a lossless library at
# all. [1.6.0: backend/peak/auto/threads keys verified present;
# parallel_on_import present; import_action keys are 2.x — see badfiles.]
replaygain:
  auto: yes
  backend: ffmpeg
  peak: sample          # true-peak is ~10x slower; use for clipping-critical material only
  overwrite: no
  threads: 2
  parallel_on_import: yes

# [1.6.0-trap] check_on_import: yes routes failures through an INTERACTIVE
# prompt (ui.input_options) — it stalls or aborts quiet imports, and the
# import_action_on_error/import_action_on_warning keys DO NOT EXIST in 1.6.0.
# Leave off for unattended imports; run `beet bad` post-import instead.
badfiles:
  check_on_import: no

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
  # Pin encoder settings so derivative regeneration is deterministic:
  # formats:
  #   opus: ffmpeg -i $source -y -vn -codec:a libopus -b:a 192k $dest
```

## Flexible-attribute declarations

Any injected numeric field used in tiebreak/templates/queries should be
declared so beets treats it as the right type:

```yaml
types:
  quality_rank: int
  tags_complete: int
```

## Instance variant: CT 101 homelab-core (asis archive profile)

The production CT runs a deliberately conservative profile: existing file
layout is preserved, nothing is rewritten:

```yaml
import:
  autotag: no      # asis
  write: no
  copy: no
  move: no
```

Rationale: the library predates beets (decade-plus of manual curation);
re-tagging or relocating files was out of scope. Dedup uses injected
flexible attributes (`quality_rank`, `tags_complete`, `acoustid_fingerprint`)
instead of MusicBrainz keys. Trade-off: no `mb_trackid` grouping — tag-key
and fingerprint-key passes carry all the weight.

## Verification checklist after any config change

```bash
beet config -p                     # right file?
python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]))" "$(beet config -p)"   # parses?
beet version                       # still boots?
beet duplicates -F -s -k <testkey> # plugin loads with new block (scratch lib for real runs)
```
