---
name: motion-film-qa
description: Critique and verify motion videos with evidence. Covers bounded critique rounds on key-frame boards with impeccable and review-animations, frames pulled from the real rendered file at every beat and transition, loop-seam check, speech-to-text of the final mix with a word-sync table, cue onset timing, motion over time (hook, dead holds, pops, flashes, energy curve), A/V offset, loudness and true peak, codec, colour and duration probes, brand and honesty audits, poster check, and an embed check in the real page with browser-use. Use after building or re-rendering any product or content video, before delivery, and after any brand or voice change. Part of the motion-film suite.
---

# Critique and QA

Two jobs, in this order. First, **critique**: is it good? That is a bounded design review. Then **verify**: is it correct? That is evidence from the real file.

## Part 1. Bounded critique rounds

Render boards, critique once, fix everything in one batch, confirm once, stop. Open-ended self-polish burns time and makes things worse.

### Boards

1. **Key-frame board:** one still per story beat, plus the first and last frame and the sign-off. Render at 0.5 scale:
   ```sh
   COMP=<id> OUT=out/qa SCALE=0.5 node scripts/stills.mjs --seconds 0 1.2 3.4 6.0 9.5 12.8 15.0 18.2
   python3 scripts/grid.py out/qa/board-<id>.jpg --cols 4 --fps <fps> out/qa/<id>-f*.jpg
   ```
2. **Motion strip:** a contact sheet of 6-12 consecutive frames across each important move (an entrance, a transition, the logo reveal), pulled from the rendered file (`frames.sh`).
3. **Onion skins** of the key moves (`onion.py out/<id>.mp4 out/qa/onion-<move>.jpg --at <s> --frames 8 --step 2`): the spacing of a move in one image. Even spacing reads as linear, bunching at the end as ease out, a gap as a jump.
4. **Phone-width board** for social and vertical work: the key frames at 480 px wide (`grid.py --w 480`), judged at arm's length. If a word cannot be read there, it is too small.

### Critique

`impeccable` and `review-animations` sharpen this round. Without them, the checklists below are the critique: go through every item on every board and write down each miss.

- **Load context once:** `<impeccable dir>/scripts/impeccable context --target <video dir>`, plus its `reference/craft-floor.md`. Marketing and landing videos are **Persuade** mode; product-demo scenes inside them follow **Operate** rules for the interface they show.
- **Design:** run `impeccable critique` on the key-frame board, against the product truth, the design document, the brand rules and the video design system. Check:
  - hierarchy per frame (one focal point);
  - type sizes at playback width;
  - colour roles and one-accent discipline;
  - logo use and clear space;
  - sample-data labels;
  - copy (language and register);
  - for vertical video, nothing important inside the platform safe zones (`grid.py --safe`);
  - the brief's banned defaults: none of them made it in;
  - accent coverage (`accent.py <accent> out/qa/<id>-f*.jpg`) and text contrast of at least 4.5:1, mid-transition too.
- **Motion:** run `review-animations` on the motion strips and the build code. Check:
  - curves and durations against the motion tokens;
  - overshoot on the logo (never allowed);
  - stagger;
  - reading holds;
  - whether every motion has a purpose;
  - whether frame-to-frame changes are smooth;
  - one hero move at a time; text and action taking turns;
  - cuts either at rest or velocity-matched.
- **Story:** does each beat land on its voice line? Is the memorable moment given room? Does a set of videos avoid one template? Does the hero object carry through? Does the energy curve (`motion.py`) peak late and keep moving in the last third?

### Findings

Write every finding in one shape, so the fix batch is concrete:

| Field | Content |
|---|---|
| id | F1, F2, … |
| severity | **blocker** (breaks a key beat or the story), **visible** (noticeable at normal speed), **pause-only** (only on a paused frame) |
| where | frame range or time range, and the file and component |
| what | what is wrong, in one sentence |
| fix | a concrete change at file level ("ease out quint and 0.6 s on the card rise in `Scene3.tsx`"), never "make it better" or "add a caption" |

**Refute before fixing.** Before the batch, take a second look at each blocker and visible finding and try to disprove it from the frames and the code: is it invisible at playback speed, already fixed, or would the fix make something else worse? Fix only what survives. Critics, human or model, are often confidently wrong.

### Owner feedback, translated

Owners give feelings; fixes need numbers. Translate before changing anything, and say the translation back.

| The owner says | Try |
|---|---|
| "Make it pop" | a scale pulse 1.0 → 1.08 → 1.0 over about 0.2 s, peaking on the beat or the spoken word |
| "More premium" | ease out quint entrances, springs at z 0.8, no overshoot on text, fewer moving elements, longer holds |
| "It drags" | cut each hold by one beat (or about 0.4 s); start the next element when the previous is 30-50 % done |
| "Too busy" | one hero move at a time; secondary moves 150 ms later at about 60 % of the travel; remove decoration |
| "Feels cheap" or "looks like AI" | name the generic defaults on screen (glows, particles, neon, gradients, stock icons), ban each one, re-render |
| "I can't read it" | longer holds (`holdFor()`), larger type for the format, nothing moving while the line is read |
| "Too fast" or "too slow" | adjust durations by distance, not by one global factor; keep the slowest move at least 3× the fastest |

Point at frames ("at 4.2 s the cards land before the voice says 'three'"), not at impressions.

### Fix and confirm

1. Collect every finding into one list.
2. Fix all of them in one batch.
3. Re-render the boards once and confirm. If something is still wrong, report it rather than looping.
4. Log the round in `VIDEO-SYSTEM.md` (date, findings, fixes).
5. **A segment that is still the weakest after two rounds** gets redesigned, not patched: draft three alternatives for it (one led by story, one by camera, one by rhythm), pick one, build it.

## Part 2. Evidence from the real file

Run all of these on the rendered output (the MP4 or WebM), not on stills. Stills render scenes alone and miss stacking bugs, blank frames between scenes, and frozen-copy glitches.

**Required file gate:** follow [FFMPEG.md §3](../motion-film/FFMPEG.md#3-verify-every-master-and-delivery-encode) on every master and final encode: upstream `probe.py`, this skill's `media-check.py` against the clock, upstream `check.py` for the actual destination, and an inspected `look.py` sheet. Preserve full JSON evidence. Supply expected dimensions explicitly for alternate formats/web derivatives. A successful platform check does not establish story timing, word sync, brand correctness or an inaudible seam; the checks below remain required. Report every warning or unmeasured value with its disposition.

| Check | Command | Pass |
|---|---|---|
| Frames at 0, 25, 50, 75 and 100 %, plus the sign-off | `bash scripts/frames.sh out/<id>.mp4 out/qa 0% 25% 50% 75% 100% <signoff s>` | each frame reads, is on-brand, has no blank or covered scene |
| Transition frames | `bash scripts/frames.sh out/<id>.mp4 out/qa <t-0.2> <t-0.1> <t> <t+0.1> <t+0.2>` | no blank frames, no double-exposed pills, no ghost rings |
| Loop seam | `bash scripts/seam.sh out/<id>.mp4` | first-vs-last PSNR ≥ 40 dB; audio jump ≈ a normal sample step |
| Speech-to-text | `node ../motion-film-voice/scripts/stt.mjs out/<id>.mp4 --lang <code> --json out/qa/stt.json` | transcript matches the script, names included |
| Word sync | `python3 scripts/sync.py clock.json vo/<id> out/qa/stt.json out/<id>.mp4` | median abs(Δ) ≤ 0.15 s; no missing words |
| Cue onsets | `python3 ../motion-film-score/scripts/onsets.py out/<id>.mp4 clock.json <cues…>` | within one frame |
| Motion over time | `python3 scripts/motion.py out/<id>.mp4 --png out/qa/motion-<id>.png` | first change within 0.3 s; no unplanned hold over 1.2 s; no pops, frozen frames or flash risk; peak energy late, last third still moving |
| A/V offset | `python3 scripts/avlag.py out/<id>.mp4 <mix>.wav` | under half a frame; audio and video streams the same length |
| Loudness, codec, duration, colour | `bash scripts/probe.sh out/<id>.mp4 out/<id>-1080.webm` | target LUFS ± 0.5; true peak under its ceiling; expected duration and fps; BT.709 tags |
| Footage cuts (footage kinds) | `python3 ../motion-film-footage/scripts/retime.py clock.json <words> vo/<id>`, then frames at every cut | no cut inside a word or on loud audio; the face stays in frame; nothing covers the mouth or eyes |
| Brand and code audit | `bash scripts/brand-audit.sh src` (configure patterns via environment variables) | no hits, or each hit explained; no time-based CSS animation |
| Honesty | read every number and name on screen in the key-frame board | all come from the shared dataset; the sample tag is visible on product scenes |
| Poster | open the poster | every caption word on screen has landed; the frame tells the story |

### Embed check (when the video goes into a page)

Open the page with `browser-use`, using a fresh, throwaway browser that is closed afterwards, and headed for anything timed. Check that:

- the poster shows before play;
- autoplay starts muted where intended;
- the video loops without a visible jump;
- switching tabs or controls swaps the video;
- a user gesture can unmute it;
- the reduced-motion preference shows the poster or pauses the video;
- the video fits its card at mobile and desktop widths without cropping captions or the essential action.

## Report

- **Evidence:** paths to the boards, frames and tables; numbers for loudness, seam PSNR, sync medians and the transcript result.
- **Critique:** findings and fixes from the round, with anything left open.
- **Not verifiable here:** how the music and voice feel (it needs human ears); colour on the target display.

## Scripts

- [scripts/stills.mjs](scripts/stills.mjs): bundles once and renders stills by frame or by second.
- [scripts/grid.py](scripts/grid.py): labelled contact sheet.
- [scripts/frames.sh](scripts/frames.sh): frames from the rendered file at percentages or seconds, plus a sheet.
- [scripts/seam.sh](scripts/seam.sh): loop seam PSNR and audio jump.
- [scripts/sync.py](scripts/sync.py): expected vs heard word onsets.
- [scripts/media-check.py](scripts/media-check.py): gate an upstream probe against clock duration, fps, frame count, dimensions and video start offset; no FFmpeg reimplementation.
- [scripts/probe.sh](scripts/probe.sh): codec, size, duration, fps, loudness, true peak.
- [scripts/brand-audit.sh](scripts/brand-audit.sh): retyped wordmark, banned fonts, monospace misuse, old domains, raw colours, non-deterministic sources, time-based CSS animation.
- [scripts/motion.py](scripts/motion.py): hook, dead holds, pops, frozen frames, flash risk and the energy curve, from the rendered file.
- [scripts/onion.py](scripts/onion.py): onion skins of a move, and adjacent frame pairs with their difference.
- [scripts/avlag.py](scripts/avlag.py): audio offset of the final file against its mix, and stream lengths.
- [scripts/accent.py](scripts/accent.py): accent colour coverage per still.
