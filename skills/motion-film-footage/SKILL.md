---
name: motion-film-footage
description: Turn existing footage (a talking-head recording, a narrated screen recording, a webinar or podcast video) into motion clips on the same clock as everything else. Transcribe it with word timings (local whisper.cpp or a speech-to-text API), read it like an editor, pick the clip, draft a cut list that removes pauses and fillers, check that no cut splits a word, retime the words onto the output timeline, reframe 16:9 to 9:16, punch in on cuts and key lines, zoom to regions of a screen, and combine the speaker with visual explanations (split, bubble and cutaway layouts, highlighted-word captions, callouts). Use for Reels, TikTok and Shorts clips from a longer video, tutorials from a screen recording, or any video built around real footage. Part of the motion-film suite.
---

# Footage: clips from real recordings

The footage is the voice and the clock's backbone; motion design explains around it. Every tool here keeps one promise: a cut never lands inside a word, and the words, captions, cues and audio all move together when the edit changes.

## 0. Before you start

- **Rights and consent.** The owner owns the footage, and the people in it agreed to it being used and edited. Write it in the brief.
- **Meaning.** A cut never changes what the speaker meant: no splicing words into a sentence they did not say, no cutting a qualifier ("not", "only", "sometimes") out of a claim, no reordering that flips an argument.
- **Copy the scripts and templates** into the video project: `scripts/` (these, plus `motion-film-voice/scripts/transcribe.mjs`, `models.mjs` and `key.mjs`) and `src/film/` (`Footage.tsx` next to `anim.ts`). Put the footage in `public/footage/`; keep it out of git.

## 1. Probe, prepare and transcribe

Follow the required [FFmpeg pipeline](../motion-film/FFMPEG.md) first: probe every source with `ffmpeg-skill`, prepare HDR/VFR/noisy media only as needed, and probe the prepared result. Preparation must finish before transcription or cut selection. Set `FFMPEG_SCRIPTS` during preflight.

```sh
python3 "$FFMPEG_SCRIPTS/probe.py" public/footage/talk.mp4 --json > out/qa/talk-source.json
node scripts/transcribe.mjs public/footage/talk.mp4 footage/talk.words.json --lang en
```

The example assumes the probe found no preparation needed. Otherwise transcribe the prepared file instead and use that same path in `clock.footage.file`. Preserve the original and record the derivation. Do not bake the clock's cuts with upstream `cut.py`/`silence.py`: `retime.py` and `Footage.tsx` already apply those segments; applying them twice breaks sync.

- **Local and free** by default (whisper.cpp through `@remotion/install-whisper-cpp`; add it with `npx remotion add @remotion/install-whisper-cpp`). Word times are re-timed against the audio's real pauses: good for cut lists and captions, within about 0.2 s.
- **`--engine scribe`** (paid) gives word-exact times and handles names and mixed languages better. Use it for highlighted-word captions on fast speech.
- **Correct the transcript text** (names, terms, numbers) before anything reads it. Keep the times.
- Match the composition's fps to the footage (usually 30, sometimes 25 or 60).

## 2. Read it like an editor and pick the clip

```sh
python3 scripts/pauses.py footage/talk.words.json --media public/footage/talk.mp4 [--from 120 --to 210]
```

It prints the transcript one phrase per line with source times, the pauses (measured on the audio), filler words in brackets, and a draft list of keep segments.

For a clip from a long recording, propose two or three candidates to the owner, each with its source range, its first line and why it works:

- **One idea** per clip, complete on its own.
- **A hook in the first two seconds:** the strongest, most specific line, moved to the front only if it does not change the meaning.
- **Length** for the platform: 15-60 s for short-video feeds.
- **An ending:** the payoff, or a clean call to action.

## 3. The cut list

Paste the chosen segments into the clock as `footage`. Tighten by hand:

- remove pauses longer than about 0.4-0.6 s, keeping about 0.1 s of air on each side;
- cut standalone fillers ("um", "uh") and false starts, unless they carry character;
- keep breaths that separate thoughts; a clip with no air sounds machine-made.

```json
"footage": {"file": "public/footage/talk.mp4", "segments": [{"in": 12.64, "out": 15.77}, {"in": 17.12, "out": 19.08}]},
"vo": [{"id": "F1", "at": 0}]
```

Then retime:

```sh
python3 scripts/retime.py clock.json footage/talk.words.json vo/clip
```

It writes `vo/clip/F1.json` (the surviving words in output seconds, in the same format as a voice-over take) and `vo/clip/F1.wav` (the audio cut to the same segments, with a short fade at each cut). It fails if a cut lands inside a word or on loud audio, and prints the output length for `clock.seconds`. From here, captions, cues, the mixer and the sync check treat `F1` like any voice line.

## 4. Picture: framing, camera and layouts

Use [templates/Footage.tsx](templates/Footage.tsx). The video is muted; its audio reaches the mix through `F1.wav`, so voice, music and effects share one master.

- **Reframe** 16:9 footage for 9:16 with the shot focus: `{"at": 0, "scale": 1, "x": 0.42, "y": 0.4}` keeps that point of the source centred. Check the face stays in frame across the whole clip on a frame board.
- **Jump cuts:** alternate the framing on each cut (`scale` 1.0, then about 1.12, then 1.0) with `ease: 0`, so the cut reads as deliberate rather than as a glitch.
- **Punch-ins on a key line:** `scale` 1.08-1.15 with `ease` 0.3-0.6 s, then back out at the next cut.
- **Screen recordings:** zoom to the region of the action (`scale` 1.8-3, `x` and `y` on the control), hold through the action, zoom out before the next step. Check the enlarged text is still sharp; a 1080p recording zoomed 3× is soft.
- **Layouts** over time, from the clock:

| Mode | Footage | The explanation |
|---|---|---|
| `full` | fills the frame | small callouts only, away from the face |
| `split` | bottom 55 % (tall) or the right half (landscape) | the rest of the frame, via `explainRegion()` |
| `bubble` | a round inset (top left in tall frames, clear of the app's buttons) | the whole frame |
| `cutaway` | hidden; its audio continues | the whole frame |

Change layout at a sentence boundary or on the keyword that the explanation illustrates, never mid-word. Changes take 0.4 s.

## 5. Visual explanations

Build them with the motion language "Talking head with overlays", or "Kinetic explainer" for the cutaways (`motion-film-brief/MOTION-LANGUAGES.md`), from the video design system's components:

- **Keyword callouts** arrive 0.1 s before the spoken keyword (its time is in `F1.json`) and leave before the next one.
- **Diagrams** in the split or cutaway area build piece by piece on the words that name each piece.
- **Captions:** `Subtitles` with `highlight` set to the accent colour for the spoken-word style; keep them off the face and out of the safe zones.
- **One overlay at a time.**

## 6. Sound

Mix with `motion-film-score/scripts/mix_template.py`: the speaker is the voice track (`F1.wav`), the bed ducks under it, and effects stay sparse (layout changes, the hook, the end). Target -14 LUFS for social, true peak at or below -1.0 dBTP.

## 7. Check

- `retime.py` passes: no cut inside a word or on loud audio.
- Frames from the rendered file at every cut and every layout change, with `grid.py --safe` for vertical: the face is in frame, nothing covers the mouth or eyes, captions and callouts are out of the safe zones.
- Word sync: transcribe the render (`transcribe.mjs out/clip.mp4 qa/out.words.json`) and run `sync.py clock.json vo/clip qa/out.words.json out/clip.mp4`. With local transcription on both sides, expect a median within about 0.2 s; with Scribe, within 0.15 s.
- Listen to every cut (a person must): no clipped consonants, no doubled breath, no jump in room tone. A cut that sounds wrong usually needs 30-80 ms more air.

## Files

- [scripts/pauses.py](scripts/pauses.py): transcript by phrase, pauses from the audio, fillers, a draft cut list.
- [scripts/retime.py](scripts/retime.py): applies the cut list to words and audio; fails on cuts inside words or on loud audio.
- [scripts/quiet.py](scripts/quiet.py): speech and silence measured on the audio (used by both).
- [templates/Footage.tsx](templates/Footage.tsx): the edit, the camera (reframe, punch-ins, zooms) and the layouts, plus `explainRegion()` and `modeAt()` for the overlays.
- `motion-film-voice/scripts/transcribe.mjs`: word-timed transcripts, local or by API.
