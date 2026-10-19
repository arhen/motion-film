---
name: motion-film-voice
description: Voice-over for motion videos. Audition and choose voices with recorded evidence, generate takes with word-level timestamps (ElevenLabs by default), check every line with speech-to-text, fit lines to their slots on the clock, fix pace and pronunciation without breaking sync, and ship takes so picture, captions and music stay locked. Use when a video needs narration, captions synced to speech, a voice change, or a line regenerated. Part of the motion-film suite.
---

# Voice-over

The voice sets the clock. Word timestamps from the TTS drive caption reveals, visual cues and the music duck, so a take is not just audio: it is timing data.

## Ground rules

- **It costs money.** Check the account's credits and tier before generating, and tell the owner roughly how many characters a job will use.
- **The voice must exist in the account** that generates it. Library voices can usually be used by id; if not, add them first.
- **Generate with timestamps,** not plain TTS. Save the word timings next to each take.
- **Never regenerate a shipped take** unless the owner asks. A new take changes the timings.
- **Commit the timing JSON and the script; never commit audio takes.**

## 1. Script file

Copy [templates/script.json](templates/script.json). Top level: `voiceId`, `modelId`, `settings`. Per line:

| Field | Meaning |
|---|---|
| `id` | Line id; also the take and timing file names (`V1.mp3`, `V1.json`) |
| `text` | The spoken line; captions use the same text |
| `direction` | An English style tag prepended to the text, for example `[calm, warm, conversational] ` |
| `voiceId`, `modelId`, `settings`, `seed` | Per-line overrides; the default seed is 7 |
| `context` | `false` stops sending the neighbouring lines as prosody context |
| `tempo` | A pitch-preserving speed change, applied only when shipping |

## 2. Audition (when the voice is not decided)

1. Shortlist 2-3 voices from the library by language, gender, age, use case ("narrative", "conversational") and descriptors ("calm", "warm").
2. Generate the **same two lines** with each voice, model, direction and seed (`scripts/vo.mjs` with a per-line `voiceId`).
3. Measure each take with `python3 scripts/voice-stats.py <takes...>`: length, words per second, median pitch, spectral centroid (brightness).
4. Transcribe each take with `node scripts/stt.mjs <takes...>` and check the words.
5. Record everything in [templates/takes.md](templates/takes.md): voice ids, settings, numbers, transcript and a recommendation. Ask the owner to listen and choose; you cannot judge timbre.

Rough guide: a lower median pitch with a darker centroid reads "warm and calm"; a brighter centroid reads "crisp, announcer". This is a hint for the shortlist, not a verdict.

## 3. Generate

```sh
VO_SCRIPT=vo/<film>/script.json VO_AUDIO_DIR=vo/<film> VO_ALIGN_DIR=vo/<film> node scripts/vo.mjs          # all missing lines
VO_SCRIPT=vo/<film>/script.json VO_AUDIO_DIR=vo/<film> VO_ALIGN_DIR=vo/<film> node scripts/vo.mjs V2 V3    # just these
```

`vo.mjs` sends neighbouring lines as context (consistent intonation), drops `[...]` tag characters from the word list, and prints each line's length and word onsets.

## 4. Check every line

1. **Transcribe:** run `node scripts/stt.mjs vo/<film>/*.mp3 --lang <iso-639-3>`, or join the takes with ffmpeg's concat first to save calls. Compare against the script:
   - brand and product names, numbers, codes;
   - any words in a second language;
   - the direction tag: it must not appear in the transcript, and must not have produced a laugh or sigh.
2. **Fit:** run `python3 scripts/slotfit.py clock.json vo/<film>`. It prints each line's start, end and gap to the next line, and fails on any overlap or any line running past the video's end.
3. **Fix** with the cheapest tool that works:

| Problem | Fix |
|---|---|
| A word is slurred or mispronounced | Regenerate the line with another `seed` (try 3); keep the take whose length is closest to the original |
| The direction tag was read aloud | Use an English tag; confirm with speech-to-text |
| A line is too long for its slot | Add `[upbeat, brisk pace]` to the direction (some models ignore `speed`); or set `tempo` 1.04-1.08 and apply it at ship time; or shorten the text |
| A long pause after a comma | A brisk direction, or rewrite the punctuation |
| Visuals must land on a word | Place the line with `alignWord` (that word lands on `at` or `beat`), not with a start time |

After any regeneration, run the check again.

## 5. Place on the clock

Clock voice entries (see `motion-film-brief/templates/clock.json`):

- `{"id": "V1", "at": 0.6}`: the line starts at 0.6 s.
- `{"id": "V3", "alignWord": 2, "at": 9.5}`: word 2 of the line starts at 9.5 s.
- `{"id": "V4", "alignWord": 0, "beat": 24}`: word 0 lands on beat 24 (uses `bpm` and `beatOffset`).

Visual cues that should meet a word use the word's absolute time: line placement plus the word's `start`.

## 6. Ship

- **Tempo:** if a line has `tempo`, ship it with `ffmpeg -filter:a atempo=<tempo>` (pitch kept) and divide its word times by the tempo.
- **Variants:** keep alternative voices or reads in `vo/variants/<name>/`, with their own `script.json` and an optional `timeline` block of clock overrides. Ship one by copying its takes and timing JSON into place. To render a variant without touching the shipped takes, swap in a copy, render, and restore under `trap` so a failure cannot leave the swap behind.
- **Re-check:** after the final mix, speech-to-text the rendered video and build the sync table (`motion-film-qa`).

## Other providers

The method needs two things from any provider: per-character or per-word timestamps, and a speech-to-text endpoint. Swap the request in `vo.mjs` and `stt.mjs` and keep the output shape: `{"text": …, "words": [{"w", "start", "end"}]}`.
