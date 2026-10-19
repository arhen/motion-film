---
name: motion-film-brief
description: Pre-production for a motion video or a set of videos about a product or a body of content. Name the kind of video (offering a menu when the request is unclear), decide the voice source, read the product or channel truth and the delivery context, pick one story and one motion language per video, test the story against generic-story checks, write the script, budget the length, and lay out a numeric direction sheet and clock skeleton before any picture or sound is built. Use at the start of any promo, showcase, landing loop, tutorial, explainer, talking-head clip or content-series job, or when a set of videos "looks like one template". Part of the motion-film suite.
---

# Brief: decide the video before building it

A great video is decided here; the build only executes this page. Spend the time on story and timing, not on frames. A vague request makes a generic video: the job of this phase is to turn adjectives ("premium", "modern", "cool") into decisions and numbers.

## 1. Intake (read, do not ask)

Read before talking to anyone. Note gaps; do not invent.

| Read | For |
|---|---|
| Product or channel truth (`PRODUCT.md`, about page, pitch, content pillars) | Positioning, audience, the job people hire it for, claims you may and may not make |
| `DESIGN.md`, brand guidelines | Logo rules, palette, type, voice and tone, tagline, domain, sign-off |
| Token files and the component or template inventory | What already exists on screen |
| The live product or recent content (`browser-use`), plus existing screenshots | Real screens, states and formats to rebuild |
| Demo, seed or sample data | One shared fictional cast and dataset, so every video agrees |
| Source material the owner supplied: footage, a recording, an article, a script | What the video must be built from |
| Where the video plays | Hero or card; feed; rendered width; autoplay muted or with sound; loop or end hold; language |
| Earlier videos and feedback | What the owner already liked and rejected |

If the project uses `impeccable`, load its context once: `<impeccable dir>/scripts/impeccable context --target <video dir>`. The critique rounds later reuse it.

Check what is available, without printing secrets: `node ../motion-film-voice/scripts/key.mjs --check` (an ElevenLabs key), and whether `@remotion/install-whisper-cpp` is in the video project (free local transcription).

## 2. Ask only the taste calls

Bundle these into one message (or one question form), each with a recommendation:

1. **The kind of video.** If the request does not name one, or two fit, offer the three likeliest from [KINDS.md](KINDS.md) plus "something else". The kind sets the defaults for everything below.
2. **The voice source:**
   - **AI voice (ElevenLabs).** Consistent, any language, re-timeable; costs credits. Offer it only if a key exists, or say what it costs and how to get one.
   - **Your own recording.** Founder voice, tutorials, authenticity. Transcribed for timings (free locally).
   - **The voice in your footage.** Talking-head and screen-recording kinds (`motion-film-footage`).
   - **No voice.** Muted loops, showreels, music-led pieces; captions or on-screen type carry the story.
3. **The audience or audiences** (one video each).
4. **Length** within the kind's range, and **formats** (landscape, vertical 9:16, 4:5). Each format gets its own layout, not a crop.
5. **Music:** synthesized in code (fits every cue, no licence) or a licensed track the owner supplies (richer; cues snap to its beats). Then the character (warm, kinetic, ambient, cinematic).

Everything else (fps, codecs, sizes, layout) has a conventional default. Decide it and state it. Never generate paid voice-over until the owner says yes.

## 3. Story, one per video

Use the story shape for the kind ([KINDS.md](KINDS.md)). For each video, write:

- **Subject and setting.** A concrete person, place and moment ("6:50 am, a café owner unlocks the shutter"), or for content kinds, the one idea and the one example. Fictional unless real and approved.
- **Three angles, then one.** Sketch three versions from different angles: the product's verb made literal, the pain made visible, and a structural idea (a bookend, one unbroken move, a before and after). Pick the strongest; borrow one element from the others.
- **The hero object.** One thing, ideally from the product's own interface or the idea's own diagram, that stays on screen through the whole video, changes role from shot to shot, and ends as the result or the sign-off. It gives the video continuity and reads with the sound off.
- **The memorable moment.** One image people remember, given the most frames and the cleanest frame around it.
- **An echo.** Plant a phrase or an image early and pay it off at the end, changed by what happened in between. One per video.
- **Motion language.** Pick one from [MOTION-LANGUAGES.md](MOTION-LANGUAGES.md) that fits the subject's world. Two videos in one set should not share a language.
- **Honesty.** Which numbers, names, quotes and sources appear, and where they come from. Plan the sample-data label for product scenes and the source card for content.

**Generic-story checks.** Before locking, run all three; any failure means a new angle, not polish:

1. **Swap the name.** Put a competitor's name in. If the video still works, it shows the category, not this product.
2. **Downgrade the feature.** Imagine a cruder version of the product. If the video is just as true of it, the proof shows the wrong thing.
3. **Delete the benefit.** Remove the beats where something gets better for the person. If the video still "works", it is a feature tour.

Also reject category clichés as the main image: rockets, shields, gears, globes, light bulbs, handshakes, glowing brains.

## 4. Script

- **Captions are the voice-over,** word for word. For footage, captions are the corrected transcript.
- **Line length:** 6-12 words per line. Budget 2.0-2.5 words per second for a calm voice and 2.5-3.0 for an energetic one.
- **Register:** the brand's voice and the audience's language. Read every line aloud and cut filler.
- **Banned openers and words:** "Introducing", "Meet", "Say hello to", "unlock", "unleash", "supercharge", "seamless", "game-changer", "the future of", "revolutionize", a rhetorical question as the first line, a three-word slogan as the last. Grep the script for them.
- **On-screen statements without voice** (loops, showreels): short phrases, at most about 8 words visible at once, each held about 0.5 s plus 0.25-0.3 s per word, with picture-only stretches between them.
- **Ending:** the canonical tagline or sign-off as a visual lockup that holds about 1.2 s. Voice it only if the length budget allows.
- **Numbers and names:** keep the written form unless speech-to-text later shows the voice mispronounces them.

## 5. Direction sheet and clock skeleton

Turn the story into numbers. A directed brief beats a vague one by a wide margin: every adjective becomes a value.

1. **Length:** estimate each line as `words ÷ pace` seconds plus 0.2-0.5 s gaps; add an opening breath (0.3-0.8 s), the sign-off (about 2 s), and a loop cross-fade (0.4-0.5 s) or an end hold.
2. **Frame rate:** 60 for fast interface motion and showreels, 30 for web loops, social and footage-based clips (match the footage).
3. **Beat-driven videos:** make the length a whole number of bars (`bpm = beats × 60 ÷ seconds`); 128 BPM gives exactly 16 bars in 30 s.
4. **Shots:** one row per shot in the beat sheet: time range, the one hero move, the hero object's role, the seam into the next shot (cut, match cut, mask wipe, morph, camera move), and the sound. Use several seam types, none more than twice, and never cross-fade two copies of one object; morph the one object instead.
5. **Energy:** an early hook (a visible change within 0.3 s; the problem felt by about 1 s; the product or idea named by about a quarter of the runtime), a short planned lull between about 55 and 85 % of the runtime, the biggest moment between 75 and 90 %, and no stretch longer than about 1.2 s without a visible change.
6. **Look and motion values:** palette roles, the one accent, type sizes for the format, the curves and springs by name from the video design system.
7. **Banned defaults for this video:** name the generic looks the model would reach for here and ban them (for example: bloom and glow orbs, neon on dark navy, floating particles, a product spinning on a turntable, an invented tagline, a stock gradient background). The QA round checks the list.
8. Copy [templates/clock.json](templates/clock.json) and fill in the voice slots, then every visual and sound cue by name, in seconds (or beats). Picture, music, effects and checks all read this file.

## 6. Components needed

List every on-screen element per shot and where it comes from:

- It exists in the source design system: rebuild it in video from that component.
- It is missing: add it once to the video design system (`motion-film-system`), then reuse it.

## 7. Deliverables spec

Decide and write down:

- Compositions and ids, one per format (`<id>`, `<id>-9x16`), resolution and fps.
- Codec and bitrate targets, and the loudness target.
- Loop or hold.
- Poster time: after every caption word on screen has landed.
- Web encode sizes and the minimum caption size at the playback width (`motion-film-system` §2 has the table per format).
- For a supplied music track or footage: its source and licence or consent, written down before it is used.
- File names and output folders.

## 8. Write the brief and get the go

Fill in [templates/BRIEF.md](templates/BRIEF.md). Show it to the owner in one message, together with the taste calls from step 2. On "go", or if the owner said to proceed without review, move on: `motion-film-system`, then `motion-film-voice` or `motion-film-footage`.

## Pitfalls

- **Guessing the kind.** A landing loop and a talking-head clip share almost nothing. Ask when it is unclear.
- **Adjectives as direction.** "Premium" and "modern" produce the model's defaults. Replace each with a value.
- **Template sameness.** A set of videos that reuse one hero shot, one notification card and one beat order reads as a template, even with different copy.
- **Stories that need missing numbers.** They tempt invented metrics. Change the story, not the honesty rule.
- **Long lines.** They force a fast read; split the line rather than speeding up the voice.
- **Captions that are not the voice-over.** They drift out of sync and double the reading load.
