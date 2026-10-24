# Required FFmpeg pipeline

Remotion creates the picture. `ffmpeg-skill` prepares media, encodes deliverables and checks the real files. Both are required, including for videos without source footage. `motion-film` directs the job; the upstream skill is its processing layer, not a second editor.

## Setup and preflight

Install [ffmpeg-skill v2.14.0](https://github.com/kajisho5/ffmpeg-skill/tree/v2.14.0) beside the nine motion-film skills, at the same scope and for the same agent. This is the tested pin; upgrade it deliberately, not during a render.

```sh
npx skills@latest add https://github.com/kajisho5/ffmpeg-skill/tree/v2.14.0 --skill ffmpeg-skill
```

Discover its installed directory from the agent's skill inventory or install lock; do not assume Claude's home directory. Load its `SKILL.md` for tool usage, with the ownership rules below governing this suite. Set `FFMPEG_SKILL_DIR` to that absolute directory, then:

```sh
export FFMPEG_SCRIPTS="$FFMPEG_SKILL_DIR/scripts"
mkdir -p out/qa
python3 "$FFMPEG_SCRIPTS/_contract.py" doctor --json > out/qa/ffmpeg-doctor.json
python3 "$FFMPEG_SCRIPTS/_contract.py" --json --static > out/qa/ffmpeg-contract.json
```

Preflight is mandatory here, even though upstream normally runs doctor only after failure. Check the reported version is `2.14.0`, each tool planned for this job is usable, and the conditional filters required by the selected flags are available. Doctor's overall `ok`/exit code can also reflect tools this job does not use: inspect its JSON, explicitly record unused missing features, and gate on the actual job's capabilities. Neither a broad pass nor a broad failure replaces that check. Resolve unknown or missing capabilities needed by the job before proceeding. On macOS, HDR conversion and labelled contact sheets may require the keg-only `ffmpeg-full` build; use the effective executable paths doctor reports. If only `drawtext` is absent, `look.py --no-timecode` is a supported label-free sheet: record that choice and its sampling times, or label the frames with the suite's Pillow-based `grid.py`. Never claim missing labels were inspected.

Missing skill, wrong version or incomplete payload blocks the pipeline. Report the install command; do not silently fall back to guessed shell commands. Run upstream scripts from their complete installed package: keep `scripts/_common/`, templates and `package.json` together. Copy only motion-film's own scripts/templates into the video project as usual.

## Ownership and timing

- **One clock:** `clock.json` owns duration, fps, footage segments, word timings and cues. No independently maintained upstream `project.json`, delivery template or edit list.
- **One picture system:** layouts, reframing, captions, overlays, transitions and brand motion stay in Remotion. Do not apply upstream social templates, automatic crops or another caption burn to an approved composition.
- **Prep before timing:** colour conversion, VFR-to-CFR, denoise, stabilization and voice cleanup happen before transcription and cut selection. Keep originals; write derived assets. Probe the result, then transcribe that exact prepared file and use it in `clock.footage.file`.
- **Cuts stay on the clock:** use `pauses.py`, clock segments and `retime.py`. Do not separately bake those cuts with `cut.py` or `silence.py` and then apply the segments again. Any later source-time edit invalidates words, cues, mix and QA; rebuild them together.
- **Delivery preserves timing:** no trimming, speed change, fps conversion or crop after approval. Use `--allow-long` on exports: a preset's duration cap must not silently remove the ending. If the destination needs a different edit or layout, change the brief/clock/composition and re-render.
- **No destructive defaults:** inspect `--dry-run --json` before writing, use explicit new output paths and never `--overwrite` without permission. Dry runs can measure inputs; they are not a sandbox. Keep full command/result JSON in `out/qa/`.
- **Suite scripts remain supported:** `encode-web.sh`, exact-timing GIF encoding and the clock-based audio/QA scripts are deliberate pipeline stages, not guessed fallbacks. Upstream presets do not cover our VP9 web encode or exact 20/25 fps GIF timing.

## 1. Ingest and prepare

Probe every footage, narration, music and B-roll input before planning from it:

```sh
python3 "$FFMPEG_SCRIPTS/probe.py" public/footage/talk.mp4 --json > out/qa/talk-source.json
```

From those measured properties, choose only necessary preparation:

| Measured need | Tool | Rule |
|---|---|---|
| HDR/Dolby Vision or wide-gamut input for our SDR picture | `color.py --to-sdr` | Convert pixels; BT.709 retagging alone is not tone mapping |
| Variable frame rate | `fit.py --fps <composition fps>` | No duration/aspect flags; probe the prepared output before transcription |
| Shaky/noisy footage | `stabilize.py`, `denoise.py` | Inspect before/after frames; no automatic “cinematic” treatment |
| Hiss or room noise in a recording | `audio.py --voice light` | Prepare before word timing; retain the untreated recording |
| External recorder/camera offset | `sync.py` | Prepare alignment before the cut list; this is audio correlation, not visual lip-sync |

Example, only when the source probe reports HDR:

```sh
python3 "$FFMPEG_SCRIPTS/color.py" public/footage/talk.mov --to-sdr -o public/footage/talk-sdr.mp4 --dry-run --json
python3 "$FFMPEG_SCRIPTS/color.py" public/footage/talk.mov --to-sdr -o public/footage/talk-sdr.mp4 --json > out/qa/talk-prep.json
python3 "$FFMPEG_SCRIPTS/probe.py" public/footage/talk-sdr.mp4 --json > out/qa/talk-prepared.json
```

If no preparation is needed, retain the source unchanged and record that decision. A generated-only video has no footage to prepare, but still runs preflight and final-file verification. Music analysis, cue placement and mixing remain in `motion-film-score`.

## 2. Encode approved picture

Probe the approved Remotion master first. If it already meets the destination, use a lossless remux rather than another lossy encode:

```sh
python3 "$FFMPEG_SCRIPTS/export.py" out/film-master.mp4 --preset copy --no-scale --allow-long -o out/film.mp4 --dry-run --json
python3 "$FFMPEG_SCRIPTS/export.py" out/film-master.mp4 --preset copy --no-scale --allow-long -o out/film.mp4 --json > out/qa/film-export.json
```

When a codec conversion is needed, inspect the chosen preset's dry run, then encode once from the master with `--no-scale --allow-long`. Social presets force 30 fps: use them only for a 30 fps composition. For an already compliant 24/25/60 fps master, use `copy` and verify the destination accepts it; otherwise change the composition before approval. Never add `--normalize` to an approved mix by default: meet the brief's loudness in the score, or explicitly fix audio and repeat audio QA.

For web delivery, run `motion-film-deliver/scripts/encode-web.sh` for MP4, VP9/Opus WebM and poster, then run the same verification gate on both videos. Never crop a landscape master into a vertical deliverable.

## 3. Verify every master and delivery encode

Copy `motion-film-qa/scripts/media-check.py` into the video project's `scripts/`. Example for an approved master being delivered to Reels:

```sh
python3 "$FFMPEG_SCRIPTS/probe.py" out/film.mp4 --json > out/qa/film-probe.json
python3 scripts/media-check.py clock.json out/qa/film-probe.json
python3 "$FFMPEG_SCRIPTS/check.py" out/film.mp4 --platform reels --lufs -14 --tp -1 --json > out/qa/film-check.json
python3 "$FFMPEG_SCRIPTS/look.py" out/film.mp4 --tiles 3x2 --safe reels -o out/qa/film-sheet.png --json > out/qa/film-look.json
```

Use the actual destination, loudness and true-peak ceiling from the brief. For a site, use `--platform custom`, not YouTube's assumed defaults. For a different composition size or a resized web derivative, pass its explicit expected `--width` and `--height` to `media-check.py`; never derive those expectations from the output under test.

The gate requires:

- successful commands and a real, non-empty output;
- `media-check.py` passes: fps and intended dimensions match, duration is within one frame of the rounded clock length, exact frame count matches when the container reports it, and no unexpected video start offset;
- destination checks have no FAILs; every WARN or unavailable measurement is reported with its disposition, not hidden behind exit 0;
- the calling agent views the generated contact sheet, including transitions/cuts and safe zones where relevant; no vision means “pixels not inspected”, not a visual pass;
- the full `motion-film-qa` gates still pass: word sync, cue onsets, A/V offset, loudness within ±0.5 LUFS, brand, motion and loop seam.

A deliberate hold, silent track or seamless loop is judged against the brief, not automatically “fixed” by content heuristics. Archive doctor/version, probes, export/check JSON and inspected sheets with the evidence pack. Recheck final encodes, not only their master.
