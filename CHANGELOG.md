# Changelog

Versions are git tags. Install or roll back to one with `npx skills@latest add https://github.com/arhen/motion-film/tree/<tag> --skill '*'`.

"Check your project" lists changes that alter the output of scripts or templates you may already have copied into a video project.

## v0.3.0 (2026-10-20)

**Added**
- Motion language "Mechanism explainer": a technical idea drawn as an isometric machine that assembles, runs and comes apart to name its parts.
- Build rules for using interactive web figures in a video: keep the drawing, drive every moving part from the clock, switch off the figure's own timers and CSS motion.
- `anatomy` as an optional companion skill.

**Check your project:** nothing; documentation only.

## v0.2.0 (2026-10-20)

**Added**
- New skill `motion-film-footage`: clips from your own recordings, with `pauses.py`, `retime.py`, `quiet.py` and `Footage.tsx`.
  - Transcript and pauses, and a cut list that never splits a word.
  - Reframing to 9:16, punch-ins, zooms, and full, split, bubble and cutaway layouts.
- Brief:
  - `KINDS.md`, a menu of ten video kinds with story shapes, offered when a request is unclear;
  - the voice source as a taste call;
  - generic-story checks, a hero object, an echo, banned defaults and a numeric direction sheet.
- Voice: an own-recording path and `transcribe.mjs` (local whisper.cpp aligned to the audio, or ElevenLabs Scribe). `key.mjs --check` reports whether a key exists without printing it.
- Three motion languages: kinetic explainer, screen tutorial, talking head with overlays.
- Design system: a full motion-token table (curves, springs and Remotion spring conversion, durations, staggers), contrast and flash limits, end-card anatomy, self-checking sample data, proofing rules.
- Build: rhythm and readability rules, a speed budget for moves and blur, velocity-matched cuts, true-cycle loops, cause-action-result for interfaces, objects with weight, sound timed from the motion, headless-render traps.
- Score: sound restraint, an ending that gets quieter, scoring without voice-over, AAC true-peak headroom.
- QA:
  - a findings format, a refute pass before fixing, owner feedback translated into numbers;
  - new scripts `motion.py` (hook, dead holds, pops, frozen frames, flashes, energy curve), `onion.py`, `avlag.py` and `accent.py`.
- Deliver: BT.709 masters, an A/V offset check, platform notes, GIF export with exact timing.

**Check your project**
- `anim.ts`: `hit()` now ramps up over 30 ms instead of jumping to 1 in one frame, so pulses start softer. There are new helpers (`springSettle`, `springPeakSpeed`, `fromRemotionSpring`, `logLerp`, `holdFor`, `loopPhase`, `loopNoise`, `ease.inOutQuart`, `ease.outBack`).
- `Subtitles.tsx`: chunks fit the frame width (at most 44 characters by default), and the size and position default from the format. There is a new `highlight` prop. Captions can split differently, so re-check the boards.
- `mix_template.py`: reads `.wav` takes as well as `.mp3`, removes DC offset, and fades both ends by 2 ms. Loudness can move by a few hundredths of a LUFS.
- `encode-web.sh`: tags BT.709, so players that guessed the colours before may show them slightly differently (now correctly).
- `sync.py`: also accepts `transcribe.mjs` output.
- `PATTERNS.md`: typed text the viewer reads now runs at 20-30 characters per second, not 90-140.

## v0.1.0 (2026-10-19)

First release: eight skills.
- One clock file for picture, voice, music and checks.
- A video design system built from the product's tokens.
- ElevenLabs voice-over with word timings.
- A synthesized score, or a supplied track with its beats snapped.
- Remotion templates, one layout per format with safe zones.
- Bounded critique and evidence QA.
- Web delivery.
