---
name: motion-film-voice
description: Voice-over for motion videos. Choose the voice source (an AI voice, the owner's own recording, the voice in their footage, or none), audition and choose voices with recorded evidence, generate takes with word-level timestamps (ElevenLabs by default), check every line with speech-to-text, fit lines to their slots on the clock, fix pace and pronunciation without breaking sync, and ship takes so picture, captions and music stay locked. Also transcribes a recording for word timings, locally with whisper.cpp or with a speech-to-text API. Use when a video needs narration, captions synced to speech, a voice change, or a line regenerated. Part of the motion-film suite.
---

# Voice-over

The voice sets the clock. Word timestamps from the TTS drive caption reveals, visual cues and the music duck, so a take is not just audio: it is timing data.

## 0. Choose the source

Decided in the brief; confirm it here before spending anything.

| Source | Use when | Cost | Path |
|---|---|---|---|
| **AI voice** (ElevenLabs by default) | No recording; a consistent brand voice; many languages; lines must re-time | Credits per character; needs a key | Sections 1 to 6 below |
| **Own recording** | Founder or creator voice, tutorials, authenticity | Free with local transcription | [Own recording](#own-recording) |
| **Voice in the footage** | Talking-head clips, narrated screen recordings | Free | `motion-film-footage` |
| **None** | Muted loops, showreels, music-led pieces | Free | Skip this skill; captions or on-screen type carry the story |

`node scripts/key.mjs --check` says whether an ElevenLabs key exists, without printing it. With no key, recommend the own recording or no voice, and say what the AI voice would cost.

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

## Own recording

The owner records the script; the takes become timing data the same way as AI takes.

1. **Record:** a quiet room, the mouth a hand's width from the microphone (a phone works), 48 kHz. One take per line (`V1.wav`, `V2.wav`), or one continuous take as a single line.
2. **Trim** leading and trailing silence to about 0.2 s. Do not process further: the mixer high-passes, adds presence and compresses.
3. **Transcribe for timings:**
   ```sh
   node scripts/transcribe.mjs vo/<film>/V1.wav vo/<film>/V1.json --lang en          # local whisper.cpp, free
   node scripts/transcribe.mjs vo/<film>/V1.wav vo/<film>/V1.json --engine scribe   # ElevenLabs speech-to-text, paid
   ```
   Local transcription needs `npx remotion add @remotion/install-whisper-cpp` in the video project; the first run builds whisper.cpp and downloads the model (`--model base` by default; `small` or `medium` are more accurate and slower; `.en` models for English only). Its word times are re-timed against the audio's real pauses, which is close enough for captions (within about 0.2 s). Use `--engine scribe` when word-exact timing matters, such as a highlighted-word caption on fast speech.
4. **Correct the text** in the JSON: names, terms and numbers as the script spells them. Keep the times.
5. **Place on the clock** and continue with section 4 (check) and 5 (place), exactly as for AI takes. The mixer and the build read `V1.wav` like `V1.mp3`.

## Other providers

The method needs two things from any provider: per-character or per-word timestamps, and a speech-to-text endpoint. Swap the request in `vo.mjs`, `stt.mjs` or `transcribe.mjs` and keep the output shape: `{"text": …, "words": [{"w", "start", "end"}]}`.
