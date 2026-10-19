---
name: motion-film-qa
description: Critique and verify motion videos with evidence. Covers bounded critique rounds on key-frame boards with impeccable and review-animations, frames pulled from the real rendered file at every beat and transition, loop-seam check, speech-to-text of the final mix with a word-sync table, cue onset timing, loudness and true peak, codec and duration probes, brand and honesty audits, poster check, and an embed check in the real page with browser-use. Use after building or re-rendering any product or content video, before delivery, and after any brand or voice change. Part of the motion-film suite.
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
  - for vertical video, nothing important inside the platform safe zones (`grid.py --safe`).
- **Motion:** run `review-animations` on the motion strips and the build code. Check:
  - curves and durations against the motion tokens;
  - overshoot on the logo (never allowed);
  - stagger;
  - reading holds;
  - whether every motion has a purpose;
  - whether frame-to-frame changes are smooth.
- **Story:** does each beat land on its voice line? Is the memorable moment given room? Does a set of videos avoid one template?

### Fix and confirm

1. Collect every finding into one list.
2. Fix all of them in one batch.
3. Re-render the boards once and confirm. If something is still wrong, report it rather than looping.
4. Log the round in `VIDEO-SYSTEM.md` (date, findings, fixes).

## Part 2. Evidence from the real file

Run all of these on the rendered output (the MP4 or WebM), not on stills. Stills render scenes alone and miss stacking bugs, blank frames between scenes, and frozen-copy glitches.

| Check | Command | Pass |
|---|---|---|
| Frames at 0, 25, 50, 75 and 100 %, plus the sign-off | `bash scripts/frames.sh out/<id>.mp4 out/qa 0% 25% 50% 75% 100% <signoff s>` | each frame reads, is on-brand, has no blank or covered scene |
| Transition frames | `bash scripts/frames.sh out/<id>.mp4 out/qa <t-0.2> <t-0.1> <t> <t+0.1> <t+0.2>` | no blank frames, no double-exposed pills, no ghost rings |
| Loop seam | `bash scripts/seam.sh out/<id>.mp4` | first-vs-last PSNR ≥ 40 dB; audio jump ≈ a normal sample step |
| Speech-to-text | `node ../motion-film-voice/scripts/stt.mjs out/<id>.mp4 --lang <code> --json out/qa/stt.json` | transcript matches the script, names included |
| Word sync | `python3 scripts/sync.py clock.json vo/<id> out/qa/stt.json out/<id>.mp4` | median abs(Δ) ≤ 0.15 s; no missing words |
| Cue onsets | `python3 ../motion-film-score/scripts/onsets.py out/<id>.mp4 clock.json <cues…>` | within one frame |
| Loudness, codec, duration | `bash scripts/probe.sh out/<id>.mp4 out/<id>-1080.webm` | target LUFS ± 0.5; true peak under its ceiling; expected duration and fps |
| Brand audit | `bash scripts/brand-audit.sh src` (configure patterns via environment variables) | no hits, or each hit explained |
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
- [scripts/probe.sh](scripts/probe.sh): codec, size, duration, fps, loudness, true peak.
- [scripts/brand-audit.sh](scripts/brand-audit.sh): retyped wordmark, banned fonts, monospace misuse, old domains, raw colours.
