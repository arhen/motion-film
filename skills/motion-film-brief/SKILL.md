---
name: motion-film-brief
description: Pre-production for a motion video or a set of videos about a product or a body of content. Read the product or channel truth, the design system and the delivery context, pick one story and one motion language per video, write the voice-over script, budget the length, and lay out the beat sheet and clock skeleton before any picture or sound is built. Use at the start of any promo, showreel, explainer, landing-video or content-series job, or when a set of videos "looks like one template". Part of the motion-film suite.
---

# Brief: decide the video before building it

A great video is decided here; the build only executes this page. Spend the time on story and timing, not on frames.

## 1. Intake (read, do not ask)

Read before talking to anyone. Note gaps; do not invent.

| Read | For |
|---|---|
| Product or channel truth (`PRODUCT.md`, about page, pitch, content pillars) | Positioning, audience, the job people hire it for, claims you may and may not make |
| `DESIGN.md`, brand guidelines | Logo rules, palette, type, voice and tone, tagline, domain, sign-off |
| Token files and the component or template inventory | What already exists on screen |
| The live product or recent content (`browser-use`), plus existing screenshots | Real screens, states and formats to rebuild |
| Demo, seed or sample data | One shared fictional cast and dataset, so every video agrees |
| Where the video plays | Hero or card; rendered width; autoplay muted or with sound; loop or end hold; poster; language |
| Earlier videos and feedback | What the owner already liked and rejected |

If the project uses `impeccable`, load its context once: `<impeccable dir>/scripts/impeccable context --target <video dir>`. The critique rounds later reuse it.

## 2. Ask only the taste calls

Bundle these into one message, each with a recommendation:

- The audience or audiences (one video each).
- Length range (web loops 15-22 s; showreels and launch films about 30 s; social cuts 6-15 s).
- Voice-over or silent; voice character and gender per video; caption style.
- Formats: landscape for the web, vertical (9:16) for short-video apps, or both. Each format gets its own layout, not a crop.
- Music: a score synthesized in code (fits every cue, no licence needed, simpler sound) or a licensed track the owner supplies (richer sound; cues snap to its beats). Then the character (warm, kinetic, ambient, cinematic, civic).

Everything else (fps, codecs, sizes, layout) has a conventional default. Decide it and state it.

## 3. Story, one per video

For each video, write:

- **Subject and setting.** A concrete person, place and moment ("6:50 am, a café owner unlocks the shutter"). Fictional unless real and approved.
- **Arc.** Situation → the product or idea meets it → one clear insight or turn → the person acts → a visible result. The structure comes from the story; never from step labels like 01/02/03/04 laid over a template.
- **The memorable moment.** One image people remember: the queue shortens and moves; a crowd of dots lights up one by one; the water recedes.
- **Motion language.** Pick one from [MOTION-LANGUAGES.md](MOTION-LANGUAGES.md) that fits the subject's world. Two videos in one set should not share a language.
- **Honesty.** Which numbers and names appear, and where they come from in the shared dataset. Plan the sample-data label for product scenes.

## 4. Script

- **Captions are the voice-over,** word for word.
- **Line length:** 6-12 words per line. Budget 2.0-2.5 words per second for a calm voice and 2.5-3.0 for an energetic one.
- **Voice:** use the brand's register and the audience's language. Read every line aloud and cut filler.
- **Ending:** the canonical tagline or sign-off as a visual lockup that holds about 1.2 s. Voice it only if the length budget allows.
- **Numbers and names:** keep the written form unless speech-to-text later shows the voice mispronounces them.

## 5. Length budget and clock skeleton

1. Estimate each line as `words ÷ pace` seconds, plus 0.2-0.5 s gaps.
2. Add an opening breath (0.3-0.8 s), the sign-off (about 2 s), and either a loop cross-fade (0.4-0.5 s) or an end hold.
3. Pick the fps: 60 for showreels with fast interface motion, 30 for web loops and social (smaller files).
4. For beat-driven videos, make the length a whole number of bars: `bpm = beats × 60 ÷ seconds`. For example, 128 BPM gives exactly 16 bars in 30 s.
5. Copy [templates/clock.json](templates/clock.json) and fill in the voice slots, then every visual and sound cue by name, in seconds (or beats for beat-driven pieces). Picture, music and effects will all read this file.

Then write the beat sheet as a table with one row per event that matters: time, voice line, what we see, what we hear.

## 6. Components needed

List every on-screen element per beat and where it comes from:

- It exists in the source design system: rebuild it in video from that component.
- It is missing: add it once to the video design system (`motion-film-system`), then reuse it.

## 7. Deliverables spec

Decide and write down:

- Compositions and ids, one per format (`<id>`, `<id>-9x16`), resolution and fps.
- Codec and bitrate targets, and the loudness target.
- Loop or hold.
- Poster time: after every caption word on screen has landed.
- Web encode sizes and the minimum caption size at the playback width (`motion-film-system` §2 has the table per format).
- For a supplied music track: its source and licence, written down before it is used.
- File names and output folders.

## 8. Write the brief and get the go

Fill in [templates/BRIEF.md](templates/BRIEF.md). Show it to the owner in one message, together with the taste calls from step 2. On "go", or if the owner said to proceed without review, move to `motion-film-system` and `motion-film-voice`.

## Pitfalls

- **Template sameness.** A set of videos that reuse one hero shot, one notification card and one beat order reads as a template, even with different copy.
- **Stories that need missing numbers.** They tempt invented metrics. Change the story, not the honesty rule.
- **Long lines.** They force a fast read; split the line rather than speeding up the voice.
- **Captions that are not the voice-over.** They drift out of sync and double the reading load.
