# Fingerprints — compute outside beets, capture everything

## Why external fpcalc (measured, not guessed)

The chroma plugin with `auto: yes` computes fingerprints during import, but
each file triggers an AcoustID API round-trip: **measured 46 s for 2 files**
on the CT 101 instance → ~10 days projected for a 19k-track library. Local
`fpcalc` (chromaprint package, no network) runs ~1–2.5 files/sec depending on
politeness level. A full 13k-file pass: 90 min (parallel, loaded) to ~12 h
(nice'd idle-priority on a 5400 RPM HDD).

AcoustID API lookups (key for this instance lives in CT 101's
`/root/.config/beets/config.yaml` under chroma, and in idols' secret store —
never hardcode it) are for **duplicate groups only** (~100s of calls) — e.g.
resolving "same recording, different tags" groups — never the whole library.

## The capture loop — and the bug that silently skips 14% of files

**The trap:** `fpcalc` on files with trailing junk (truncated frames, appended
garbage after the audio stream) decodes fine, prints a **valid fingerprint to
stdout**, then errors on the final frame read and **exits nonzero**. A capture
loop like:

```bash
r=$(fpcalc -length 120 "$f" 2>/dev/null) || return 0   # ✗ DISCARDS VALID FPS
```

throws away exactly those fingerprints. Live-verified: the first pass over
13,321 files "completed" with 1,847 files missing — every one re-fingerprinted
successfully once stdout was captured regardless of exit code. ffmpeg
reports zero decode errors on the same files (`ffmpeg -v error -i f -f null -`
empty output) — the audio is intact.

**Correct pattern:**

```bash
_fp() {
  local f="$1" r dur fp
  r=$(fpcalc -length 120 "$f" 2>/dev/null) || true      # capture stdout anyway
  dur=$(printf '%s\n' "$r" | sed -n 's/^DURATION=//p')
  fp=$(printf '%s\n' "$r" | sed -n 's/^FINGERPRINT=//p')
  if [ -n "$fp" ]; then
    printf '%s\t%s\t%s\n' "$f" "$dur" "$fp" >> "$out"
    printf '%s\n' "$f" >> "$done_list"
  else
    printf '%s\n' "$f" >> "$failed_list"
  fi
}
```

A file with NO fingerprint after this is genuinely corrupt (or <1 s of
audio). Expect ~0.02% failures on real libraries.

## Resumable design (hard-won)

- **Done-list as a plain file** (one path per line) + `declare -A DONE` skip
  set built at startup. On resume, a file is skipped if it appears in the
  done-list OR in the TSV's path column.
- **Walk with NUL-delimited find and read -d ''** — never xargs pipelines:

```bash
while IFS= read -r -d '' f; do
  [[ -n "${DONE[$f]:-}" ]] && continue
  _fp "$f"
done < <(find "$base" -path '*/lost+found' -prune -o -type f \
  \( -iname '*.mp3' -o -iname '*.flac' -o -iname '*.m4a' -o -iname '*.aac' \
     -o -iname '*.ogg' -o -iname '*.opus' -o -iname '*.wav' \
     -o -iname '*.aiff' -o -iname '*.aif' -o -iname '*.wma' \) -print0)
```

  Why no xargs: an earlier `find -print0 | xargs -0 grep -vxFf done.txt --`
  pattern made grep read the **audio files as grep content** (binary → empty
  output → nothing processed). Also, an `xargs grep -v` dedup can't append
  progress — you need per-file loop control for resume.
- **flock lockfile** so a second launch refuses to start instead of stacking:

```bash
exec 9> /root/fp.lock
flock -n 9 || { echo "LOCKED: another pass is running"; exit 1; }
```

- **One writer per output file.** Two appenders + one `>` truncator = silent
  data loss (observed: a second script's `>` redirect clobbered a TSV being
  appended by the first). If you need dedup, do it in-place at start:
  `sort -u file -o file`.
- **Politeness on shared boxes:** `nohup nice -n 19 ionice -c3` + single
  worker. On the 2-core/5400-RPM instance, 4-way parallel fpcalc hit load
  12.67 and started killing SSH handshakes ("banner exchange timeout" =
  starvation, looks like a network bug but isn't).
- **Launch detached, verify by outputs.** Foreground launches over SSH that
  time out orphan their children (kill in pipeline order: find → xargs →
  fpcalc). Verify progress with `wc -l < tsv` growth, not `pgrep -f` patterns
  that self-match the monitoring script.

## Coverage check before declaring done

```bash
find "$base" ... -print | sort > /tmp/all_audio.txt
cut -f1 "$out" | sort -u > /tmp/fp_paths.txt
sort -u "$done_list" >> /tmp/fp_paths.txt
sort -u /tmp/fp_paths.txt -o /tmp/fp_paths.txt
comm -23 /tmp/all_audio.txt /tmp/fp_paths.txt   # every remaining file, by name
```

Never trust "the script finished" — verify the set difference is empty (or
only genuinely-corrupt files remain).

## Injection into beets

After the pass completes, bulk-inject via ORM (single transaction) — see
`bulk-injection.md`. Store both fields: `acoustid_fingerprint` (the string)
and `acoustid_length` (integer duration). Including `acoustid_length` in the
dedup key prevents "same opening audio, different length" false groups.
