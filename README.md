<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg">
    <img alt="motion-film: picture, voice-over, music and sound effects locked to one clock" src="assets/hero-light.svg" width="100%">
  </picture>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-3355FF?style=flat-square"></a>
  <img alt="9 agent skills" src="https://img.shields.io/badge/agent%20skills-9-16130F?style=flat-square">
  <a href="https://www.remotion.dev"><img alt="Built for Remotion" src="https://img.shields.io/badge/built%20for-Remotion-0B84F3?style=flat-square"></a>
  <img alt="Works with Claude Code, Codex, Pi, Cursor, OpenCode and more" src="https://img.shields.io/badge/works%20with-Claude%20Code%20%C2%B7%20Codex%20%C2%B7%20Pi%20%C2%B7%20Cursor%20%C2%B7%20OpenCode-0E9F8A?style=flat-square">
</p>

**motion-film** is a set of agent skills that teach your coding agent to make **consistent, high-craft motion videos in code**, for a product or for content: landing-page loops, feature showcases, launch films, showreels, tutorials, explainers of a term or an article, and clips cut from your own talking-head footage for Reels, TikTok and Shorts.

The idea is simple: a video is frontend work with a clock. Every frame is a designed screen, so it is built from your design system, critiqued like UI, and checked with evidence. Picture, voice-over, music and sound effects all read **one clock file**, so a spoken word, a sound hit and a motion land on the same frame.

```sh
npx skills@latest add arhen/motion-film --skill '*'
```

<br>

## What you get

<table>
  <tr>
    <td width="33%" valign="top"><b>A process with gates</b><br>Eight phases from brief to delivery. Each has an output and a gate, so nothing ships on "it rendered".</td>
    <td width="33%" valign="top"><b>One clock</b><br><code>clock.json</code> holds every voice slot and named cue. Picture, captions, music, sound effects and QA all read it.</td>
    <td width="33%" valign="top"><b>Your design system, for video</b><br>Tokens imported, not copied. Type minimums for the real playback size, logo rules, rebuilt components, safe zones per format.</td>
  </tr>
  <tr>
    <td valign="top"><b>Voice three ways</b><br>An AI voice (ElevenLabs), your own recording, or the voice in your footage. All become word-timed lines on the clock.</td>
    <td valign="top"><b>Music two ways</b><br>A score synthesized in code that hits every cue, or your own licensed track with the cues snapped onto its beats.</td>
    <td valign="top"><b>Evidence QA</b><br>Frames from the real file, motion over time, loop seam, word sync, A/V offset, loudness, brand and honesty audits.</td>
  </tr>
  <tr>
    <td valign="top"><b>Any kind of video</b><br>Ten kinds from landing loops to article explainers, each with its length, format and story shape. Unclear request? You get a menu.</td>
    <td valign="top"><b>From your own footage</b><br>Transcribe, cut the pauses (never inside a word), reframe to 9:16, punch in, and explain beside you with split and bubble layouts.</td>
    <td valign="top"><b>Directed, not defaulted</b><br>Adjectives become numbers: curves, springs, durations, holds. The generic looks a model reaches for are named and banned.</td>
  </tr>
</table>

## Quick start

**1. Have a Remotion project.** These skills do not create one. Follow Remotion's guide ([remotion.dev/docs](https://www.remotion.dev/docs)), usually `npx create-video@latest`.

**2. Install the skills** (all nine; they work as a suite):

```sh
npx skills@latest add arhen/motion-film --skill '*'          # into this project
npx skills@latest add arhen/motion-film --skill '*' -g       # for your user, all projects
npx skills@latest add arhen/motion-film --skill '*' -a claude-code   # one agent only
```

No Node? Copy the folders by hand: see [Manual install](#manual-install). Already installed an older version? See [Upgrade](#upgrade).

**3. Ask your agent for a video.** The entry skill is `motion-film`; it runs the phases in order and asks you only the taste calls. If your request does not say what kind of video, it offers a short menu first, and it asks where the voice comes from before spending anything.

> Use motion-film to make a 20-second looping explainer for our landing page. Our tokens are in `src/styles/tokens.css` and the brand rules are in `brand/`.

> Cut three 30-second Reels from `footage/webinar.mp4`, one idea each, with captions and a diagram beside me when I explain the pricing.

> Make a 60-second explainer of the term "vector database" for TikTok, from this article: <url>.

> Turn my screen recording `footage/setup.mov` into a 90-second tutorial with zooms on each step. I'll narrate it myself.

> Lay our licensed track `music/launch.mp3` under the launch film and lock the scene changes to its beats.

> Run a QA pass on `out/launch.mp4`: frames, motion, loop seam, word sync and loudness.

<br>

## For AI agents

> **If you are an AI agent** and a user asked you to install or use this repository, follow these steps exactly. Ask the user before anything that overwrites files, costs money, or is not listed here.

1. **Install all nine skills together.** They reference each other's scripts by relative path, so a single skill on its own is incomplete.
   ```sh
   npx skills@latest add arhen/motion-film --skill '*' -y
   ```
   - Add `-g` to install for the user (all projects) instead of the current project. If the user did not say, ask which they want.
   - Add `-a <agent>` to target one agent, for example `-a claude-code`, `-a codex`, `-a pi`, `-a cursor`, `-a opencode`.
2. **If `npx` is unavailable or the command fails**, install by hand (see [Manual install](#manual-install)): clone the repository, copy every `skills/motion-film*` folder into the agent's skills folder, and do not overwrite an existing folder of the same name without asking.
3. **Verify.** There must be nine folders (`motion-film`, `motion-film-brief`, `motion-film-system`, `motion-film-voice`, `motion-film-footage`, `motion-film-score`, `motion-film-build`, `motion-film-qa`, `motion-film-deliver`), each with a `SKILL.md` whose `name` matches the folder.
   ```sh
   ls <skills dir> | grep motion-film
   head -3 <skills dir>/motion-film/SKILL.md
   ```
4. **Do not, as part of installing:**
   - create a Remotion project;
   - install companion skills;
   - generate voice-over or call any paid API;
   - commit anything.

   Offer these to the user instead.
5. **Report to the user:**
   - what you installed and where;
   - which [companion skills](#companion-skills-optional) are optional;
   - what they need ([Requirements](#requirements));
   - how to start: "ask for a video; the entry skill is `motion-film`".
6. **If the skills are already installed** (the folders exist, or `skills-lock.json` lists `motion-film`), you are upgrading: follow [Upgrade](#upgrade). Run the same install command with the same scope; `npx skills update` alone misses newly added skills. Then tell the user what changed from [CHANGELOG.md](CHANGELOG.md), and ask before overwriting scripts or templates they copied into their video project.
7. **When you use the skills:**
   - load `motion-film` first and follow its phases in order;
   - copy scripts and templates into the user's video project before running them;
   - never commit generated media.

<br>

## How it works

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/pipeline-dark.svg">
  <img alt="Eight phases, each with an output and a gate: preflight, brief, design system, voice or footage, music, picture, critique and QA, deliver" src="assets/pipeline-light.svg" width="100%">
</picture>

| Skill | What it does |
|---|---|
| [`motion-film`](skills/motion-film/SKILL.md) | **Entry point.** The whole process, the quality bar, preflight checks, lessons that cost a re-render. |
| [`motion-film-brief`](skills/motion-film-brief/SKILL.md) | **1. Brief.** The kind of video, the voice source, one story and one motion language per video, generic-story checks, the script, a numeric direction sheet, the clock skeleton. |
| [`motion-film-system`](skills/motion-film-system/SKILL.md) | **2. Design system.** Video theme from your tokens, type minimums per format, logo and asset rules, components, a catalogue board. |
| [`motion-film-voice`](skills/motion-film-voice/SKILL.md) | **3. Voice-over.** AI voice or your own recording: audition, takes with word timings, local or API transcription, speech-to-text checks, slot fitting. |
| [`motion-film-footage`](skills/motion-film-footage/SKILL.md) | **3. Footage.** Clips from your own recordings: transcript, pauses, a cut list that never splits a word, reframing, punch-ins, zooms, split, bubble and cutaway layouts. |
| [`motion-film-score`](skills/motion-film-score/SKILL.md) | **4. Music and SFX.** Synthesized score or a supplied track, SFX on cues, ducking, loops, loudness. |
| [`motion-film-build`](skills/motion-film-build/SKILL.md) | **5. Picture.** Remotion patterns, one layout per format, captions, loop seams, motion blur, pitfalls. |
| [`motion-film-qa`](skills/motion-film-qa/SKILL.md) | **6. Critique and QA.** One bounded critique round with a refute pass and feedback translated into numbers, then evidence from the real file. |
| [`motion-film-deliver`](skills/motion-film-deliver/SKILL.md) | **7. Deliver.** Masters, web encodes, posters, embed snippet, a README with a summary per video. |

### Kinds of video

| Product | Content |
|---|---|
| Landing-page loop, 15-22 s | Tutorial or how-to, 30 s-3 min |
| Feature showcase, 20-45 s | Term or concept explainer, 30-90 s |
| Launch or marketing film, 30-60 s | Article explainer, 45-120 s |
| Showreel, 20-40 s | Talking-head clip from your footage, 15-60 s |
| App store or onboarding preview, 15-30 s | Series kit: intro, lower thirds, end card |

Each kind comes with its formats, voice and music defaults, a story shape and its honesty rules ([KINDS.md](skills/motion-film-brief/KINDS.md)).

### One clock

Every timing lives in one file. Scenes read cues by name, captions read word timestamps, the mixer places voice and sound effects from the same numbers, and the QA scripts compare the result against it.

```json
{
  "fps": 30, "seconds": 20.0, "bpm": 96, "width": 1920, "height": 1080,
  "vo": [
    {"id": "V1", "at": 0.6},
    {"id": "V3", "alignWord": 2, "at": 9.5},
    {"id": "V4", "alignWord": 0, "beat": 24}
  ],
  "cues": {
    "elementsIn": [1.2, 1.6, 2.0, 2.4],
    "turn": 6.2, "insight": 9.5, "signoff": 17.6,
    "loop": [19.5, 20.0]
  }
}
```

A voice line can start at a time, put a chosen word on a time, or put a word on a beat.

### Formats

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/formats-dark.svg">
  <img alt="A landscape layout and a vertical layout of the same story, with caption bands and the zones that short-video apps cover" src="assets/formats-light.svg" width="100%">
</picture>

Each format gets its own layout from the same story, clock and components. Type minimums come from the playback size, and vertical cuts stay clear of the buttons and text that Reels, TikTok and Shorts draw over the video. `grid.py --safe` tints those zones on review boards.

### Music

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/music-dark.svg">
  <img alt="A song's beat grid with cues moving from where they were written onto the nearest beat" src="assets/music-light.svg" width="100%">
</picture>

- **Synthesized in code:** the tempo makes the length whole bars, every hit sits on a cue, and no licence is needed.
- **Your own track:**
  - `beats.py` finds the tempo, the beat grid, the bar starts and the drops.
  - `snap.py` moves the cues onto beats and writes the track into the clock.
  - The mixer ducks the song under the voice. A loop cross-fades into the track's own lead-in, so the seam is inaudible.

### Evidence

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/evidence-dark.svg">
  <img alt="Example evidence: loop seam 44.7 dB, word sync 0.03 s, loudness -16.0 LUFS, true peak -1.7 dB, cue onsets within 4 ms, beat grid 128.02 BPM" src="assets/evidence-light.svg" width="100%">
</picture>

Critique is bounded: render the boards, critique once, fix everything in one batch, confirm once, stop. Then every check runs on the real MP4 or WebM, because stills miss stacking bugs, blank frames and loop glitches. Whatever cannot be measured, such as how the music feels, is reported as needing human ears.

<br>

## Requirements

- A **Remotion** project ([setup guide](https://www.remotion.dev/docs)).
- **Node 20+**, **Python 3** with numpy, scipy and Pillow, and **ffmpeg** with libx264, libvpx-vp9, libopus and aac.
- For an AI voice: an **ElevenLabs** account (text to speech with timestamps, speech to text). Optional; your own recording or no voice works too.
- For free local transcription (your own recording, footage): `npx remotion add @remotion/install-whisper-cpp` in the video project. The first run builds whisper.cpp (needs git, make and a C compiler) and downloads a model.
- For capturing your product and checking embeds: **Chrome** and a browser automation tool.

Tested on macOS. Linux should work; on Windows, use WSL.

## Licences and costs

- **Remotion** has its own licence: free for individuals, non-profits and companies of up to 3 people; larger companies need a company licence. Check [remotion.dev/license](https://www.remotion.dev/license).
- **ElevenLabs** (or any voice provider) charges per character. The voice skill asks before spending.
- **Fonts** must be licensed for video. Brand fonts usually are; check before copying them into a project.
- **Music:** a synthesized score needs no licence. A supplied track needs a written licence that covers the use (web, ads, social).
- **Footage:** you need the rights to it and the consent of the people in it. Cuts never change what a speaker meant.
- **Sample data:** people, businesses and numbers on screen are either real and approved, or fictional and labelled as sample data.

## Companion skills (optional)

The suite leans on frontend skills instead of repeating them. Each phase says what to do without them.

| Skill | From | Used for |
|---|---|---|
| `impeccable` | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | Project context, design critique, typography, extracting tokens and components |
| `review-animations`, `animate`, `animation-vocabulary`, `emil-design-eng` | [emilkowalski/skills](https://github.com/emilkowalski/skills) | Motion critique, building one animation right, naming effects, polish |
| `browser-use` | [browser-use/browser-harness](https://github.com/browser-use/browser-harness) | Capturing live product screens, checking the video in its page |
| `anatomy` | [wheresryan22/anatomy](https://github.com/wheresryan22/anatomy) | Technical ideas drawn as isometric machines, for mechanism explainers; animated from the clock in video |

```sh
npx impeccable install
npx skills@latest add emilkowalski/skills
npx skills@latest add https://github.com/wheresryan22/anatomy --skill anatomy
```

For browser-harness, follow its [install guide](https://github.com/browser-use/browser-harness/blob/main/install.md).

## Manual install

```sh
git clone --depth 1 https://github.com/arhen/motion-film /tmp/motion-film
cp -R /tmp/motion-film/skills/motion-film* <skills dir>/
```

| Agent | For your user | For one project |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex, Pi, Cline, Warp, Zed | `~/.agents/skills/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.agents/skills/` |
| Cursor | `~/.cursor/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` | `.agents/skills/` |
| GitHub Copilot | `~/.copilot/skills/` | `.agents/skills/` |

If your project keeps its skills in `.agents/skills/` with symlinks from `.claude/skills/`, install for both at once, so the installer keeps one copy and the symlinks: `npx skills@latest add arhen/motion-film --skill '*' -a claude-code -a codex`.

## Upgrade

**1. Re-run the install command,** with the same flags you installed with (`-g`, `-a ...`). It updates every skill and adds any new one:

```sh
npx skills@latest add arhen/motion-film --skill '*'
```

`npx skills update` refreshes the skills you already have but does not add new ones (v0.2.0 added `motion-film-footage`), so the entry skill would point to a skill you do not have. Prefer the command above.

**2. Pin or roll back** to a version (git tags; see [CHANGELOG.md](CHANGELOG.md)):

```sh
npx skills@latest add https://github.com/arhen/motion-film/tree/v0.3.0 --skill '*'
```

**3. Update your video project's copies.** The skills tell you to copy scripts and templates into your project, and those copies do not change when the skills do. Compare them with the new versions:

```sh
diff -ru <skills dir>/motion-film-build/templates src/film        # and the same for the scripts you copied
```

Copy over the files you never edited. Merge the ones you did by hand. The "Check your project" notes in the changelog list every change that alters output.

**4. Manual install:** pull or re-clone the repository and copy `skills/motion-film*` over the old folders.

## Versions

Each release is a git tag with notes in [CHANGELOG.md](CHANGELOG.md). Watch the repository's releases to hear about new ones.

## What is inside

```
skills/
  motion-film/            entry point: phases, gates, preflight, lessons
  motion-film-brief/      KINDS.md, MOTION-LANGUAGES.md, templates/BRIEF.md, templates/clock.json
  motion-film-system/     templates/theme.ts, Catalog.tsx, VIDEO-SYSTEM.md
  motion-film-voice/      scripts/vo.mjs, stt.mjs, transcribe.mjs, slotfit.py, voice-stats.py
  motion-film-footage/    scripts/pauses.py, retime.py, quiet.py, templates/Footage.tsx
  motion-film-score/      scripts/synth.py, mix_template.py, beats.py, snap.py, onsets.py
  motion-film-build/      PATTERNS.md, templates/anim.ts, clock.ts, Subtitles.tsx, FilmShell.tsx …
  motion-film-qa/         scripts/stills.mjs, frames.sh, grid.py, onion.py, motion.py, seam.sh, sync.py, avlag.py, accent.py, probe.sh, brand-audit.sh
  motion-film-deliver/    scripts/encode-web.sh, templates/README-films.md
assets/                   README diagrams (python3 assets/build.py rebuilds them)
```

Copy scripts and templates into your video project before running them; Node resolves packages from the script's own folder.

## Contributing

New motion languages, patterns, voice providers and formats are welcome. A contribution should:

- pass the same gates the skills ask of a video;
- include the evidence: boards, frames, numbers;
- stay generic, with no product names, data or paths from one project.

## Licence

[MIT](LICENSE)
