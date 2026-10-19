---
name: motion-film-score
description: Music and sound effects for motion videos, locked to the same clock as the picture. Either a score synthesized in code (tempo chosen so the length is whole bars, an arrangement that follows the story beats) or a supplied licensed track (beats and downbeats detected, the clock's cues snapped onto its grid). Also an SFX palette per motion language pitched to the key, music ducked under voice-over, seamless loops, mastering to a loudness target, and verification without listening (loudness, spectrogram, onset timing, beat grid). Use when a video needs a score, sound design, a song laid under it, a re-mix after retiming, or an audio QA. Part of the motion-film suite.
---

# Score and sound effects

Two ways to get music, both locked to the clock:

- **A. Synthesized in code** (sections 1 to 4). Every hit lands on a cue, nothing needs a licence, and a re-time is a re-run. The cost is craft and a simpler sound.
- **B. A supplied track** (section 5). A song the owner has the rights to: richer sound, and the picture follows the music instead. Its beats are detected and the cues snap onto them.

Either way: keep it under the voice, and say plainly that a person must listen to it.

## 1. Tempo and form from the clock

- **Whole bars.** Choose the tempo so the video's length is a whole number of bars: `bpm = beats × 60 ÷ seconds`. For example, 32 beats over 15.5 s is 123.9 BPM, which gives 8 bars.
- **Form follows the beat sheet.** Use intro → build → (silence) → drop → body → breakdown → final hit for showreels. Loops use an even bed that ends where it began.
- **Harmony.** A four-chord loop in one key is enough (for example IV-V-iii-vi), with one chord per bar or per two bars. Resolve to the tonic on the sign-off.
- **Character comes from the motion language** (see `motion-film-brief/MOTION-LANGUAGES.md`): warm keys and plucks for liquid; kick, clap and stabs for kinetic; pads and felt piano for atmospheric; a rain bed and soft piano for cartographic; a full arrangement for showreels.

## 2. Sound effects on cues

Every SFX reads its time from the clock's `cues`, never from a number typed into the mixer.

- **Pitch to the key.** Pops, chimes and blips are notes, so an ascending set (for example a pentatonic run as items appear) sounds composed, not random.
- **One palette per motion language:** drips and pour for liquid; swish, stamp and record beep for kinetic; twinkles and chimes for atmospheric; pin thocks, pencil scratch and hum for cartographic; impacts, risers, whooshes and clicks for showreels.
- **Sonic logo.** The same two or three notes close every video (see the video design system).
- **Restraint.** Keep a short gap of silence before a drop. One effect per visual event is enough.

## 3. Voice-over in the mix

- **Placement.** Place the takes with the same rule as the clock (`at`, or `alignWord` with `at` or `beat`).
- **Voice processing.** High-pass at about 90 Hz, add a touch of presence above 3 kHz, use gentle compression, and normalise the peak.
- **Ducking.** Build an envelope from the voice's energy (40-50 ms attack, 300-400 ms release). Pull the bed down 6-8 dB under speech and the SFX about 3 dB.
- **Target.** In the 300 Hz to 4 kHz band, the voice sits at least 12 dB above the bed while it speaks.
- **No takes yet, or `NO_VO=1`.** Mix the takes as silence, so a music-only render still works.

## 4. Loop wrap and mastering

- **Loops:** render the length plus a 3-4 s tail, then add the tail onto the start, so reverb and the bed continue across the seam.
- **Soft-clip** gently, then **normalise in two passes, linear**, with `loudnorm` (the helper `loudnorm()` in `synth.py`):

| Format | Integrated loudness | True peak |
|---|---|---|
| Showreels, launch films | -14 LUFS | ≤ -1.2 dBTP (master to -1.6, because the AAC encode adds peaks) |
| Web loops, background video | -16 LUFS | ≤ -1.5 dBTP |
| Social | -14 LUFS | ≤ -1.0 dBTP |

## 5. A supplied track

**Rights first.** Use only music the owner has a written licence for, covering this use (web, ads, social; some stock licences exclude ads or paid promotion). Write the title, source and licence into the brief before the track goes into a mix. No licence, no track: fall back to path A.

1. **Read the beat grid:**
   ```sh
   python3 scripts/beats.py music/track.mp3 --json out/track-beats.json
   ```
   It prints the tempo, how well a fixed grid fits, the downbeats and the section starts (level jumps such as a drop). Produced music fits a fixed grid within a few ms; live music drifts, and the tools then use the tracked beats. Assumes 4/4. If the tempo feels half or double, rerun with `--min` and `--max` around the right one. The downbeat is an estimate: check it against the drum pattern.
2. **Pick where the video starts in the track:** a downbeat, usually a section start, so the opening frame meets a musical entry.
3. **Snap the clock:**
   ```sh
   python3 scripts/snap.py clock.json out/track-beats.json --from 31.88 --to beat --skip loop,opening
   ```
   Cues move to the nearest beat (`--to bar` for scene changes, `half` for fast interface events). A list that would collapse onto one beat moves to the finer grid; a cue further than `--max` from the grid stays and is flagged. The clock gets `bpm`, `beatOffset` and a `music` block; the mixer, `clock.ts`, `slotfit.py` and `sync.py` all read them. Voice slots do not move: re-run `slotfit.py`.
4. **Fit the length to whole bars** for a loop (`snap.py` prints the two nearest lengths), and set `seconds` and the `loop` cue to match.
5. **Mix** with the same mixer: `mix_template.py` uses the track when the clock has `music`. It level-matches the track, ducks it under the voice, and either fades out the last bar (end hold) or, for a loop, cross-fades the last bar into the music just before `from`, so the seam plays the track's own lead-in to the opening.
6. **Keep sound effects sparse.** The track already carries rhythm. Keep transitions, the memorable moment and the sonic logo; drop most per-item pops. Pitch the ones you keep to the track's key.
7. **Check the result:** `beats.py out/film.wav` should report the same tempo with the first downbeat at `beatOffset`, and `onsets.py` on the SFX stem should show the cues within a frame.

## 6. Verify without listening

You cannot hear the result. Measure it, and say the music still needs human ears.

```sh
bash scripts/audio-report.sh out/film.wav out/qa                      # loudness, true peak, spectrogram and waveform PNGs
python3 scripts/onsets.py scripts/.cache/film-sfx.wav clock.json elementsIn action result:0   # SFX stem: expected cue time vs the onset near it
python3 scripts/onsets.py out/film.wav clock.json drop                                 # full mix: only for prominent hits
```

- Check transients (pops, clicks, hits). A swell (whoosh, riser) starts early by its `lead` so its peak lands on the cue; skip it in the onset check.
- `name:0` or `name:-1` checks one end of a range cue, when its sound sits only there.
- Look at the spectrogram. You want no empty low end where energy is intended, no hard clipping walls, and visible gaps where silence is designed.
- On the SFX stem, every cue onset should be within one frame (33 ms at 30 fps) of the expected time. On the full mix, the bed's own transients (plucks, hats) sit near the cues and can mislead the detector, so check only prominent hits there.
- After rendering the video, run speech-to-text on the final mix (`motion-film-qa`). If a word disappears in the mix but not in the raw take, the bed or an effect is masking it. Turn that sound down; do not turn the voice up.

## Files

- [scripts/synth.py](scripts/synth.py): the toolkit (oscillators, filters, reverb, delay, drums, supersaw, pluck, FM bell, risers, whooshes, impacts, interface sounds, VO loading, compression, two-pass loudnorm). Everything is seeded and deterministic.
- [scripts/mix_template.py](scripts/mix_template.py): a complete mixer (synthesized bed or supplied track, cue-driven SFX, voice-over, duck, loop wrap, master). Copy it per video and edit the bed and the `CUE_SOUNDS` table.
- [scripts/beats.py](scripts/beats.py): tempo, beat grid, downbeats and section starts of a supplied track (numpy and scipy only).
- [scripts/snap.py](scripts/snap.py): snaps the clock's cues onto the track's grid and records the music in the clock.
- [scripts/audio-report.sh](scripts/audio-report.sh), [scripts/onsets.py](scripts/onsets.py): the checks.

## Pitfalls

- **Events after the buffer end.** An event scheduled past the end of the buffer crashes a naive `place()`. The toolkit guards for it; keep that guard if you write your own.
- **Separate layers of different lengths.** Two layers with different lengths cannot be added directly; pad them first.
- **Effects that mask speech.** A riser or a shimmer of bells under a line can mask a brand word. Duck the effects as well as the bed.
- **Shipped vs bed loudness.** Verify the loudness of the shipped container (mp4 or webm), not only the WAV.
- **Beat detection on a finished mix.** Voice-over on top of music throws the tempo off. Run `beats.py` on the music alone.
- **Cutting a track mid-bar.** A loop or an end that is not whole bars sounds clipped even when the seam is click-free. Fit the length to the bar.
