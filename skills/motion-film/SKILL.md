---
name: motion-film
description: Plan, build and ship consistent, high-craft motion videos in code for a product or a body of content (landing-page loops, feature showcases, launch films, showreels, tutorials, term and article explainers, talking-head clips from the owner's own footage, vertical cuts for Reels and TikTok, recurring content series), with picture, voice-over, music and sound effects locked to one clock, built from a video design system derived from the product's or channel's own, directed with numbers instead of adjectives, critiqued in bounded rounds and verified with evidence. Use when asked for a promo, explainer, showreel, product or feature video, tutorial, motion graphics, landing or hero video, social clip, or a series of videos that should look and sound like one family. Entry point that routes to motion-film-brief, motion-film-system, motion-film-voice, motion-film-footage, motion-film-score, motion-film-build, motion-film-qa and motion-film-deliver.
---

# Motion films

A motion video is frontend work with a clock. Every frame is a designed screen, so product-UI craft applies: the design system is the direction, critique is bounded and evidence-based, and nothing ships on "it rendered".

## The bar

A video passes when all of these hold:

1. **Built from real pieces, not screenshots.** Interface on screen is rebuilt from the product's real components and tokens (or the channel's real templates). Screenshots are reference only.
2. **One clock.** Picture, voice-over, music and every sound effect read the same clock file. A spoken word, a hit and a motion land on the same frame because they share one number.
3. **One design system.** Type, colour, logo, icons, third-party marks, layout, motion and sound come from the video design system (`motion-film-system`), which imports the source tokens instead of copying them.
4. **A story, not a template.** Each video has its own subject, setting, arc and motion language. A set of videos must not share one pattern with the names swapped.
5. **Honest.** People, businesses and numbers on screen are real and approved, or fictional and labelled as sample data. No invented customers, metrics, testimonials, prices or dates.
6. **Verified by evidence.** Frames pulled from the real output file, speech-to-text of the final mix, a word-sync table, motion over time, loudness and true peak, the loop seam, a brand audit. Whatever could not be verified (for example how the music feels) is said plainly.
7. **Directed, not defaulted.** Every adjective in the request becomes a value (a curve, a spring, a duration, a colour role), and the brief names the generic looks the model would reach for and bans them.

## Phases and gates

Run them in order. Load each phase skill when you reach it.

| # | Phase | Skill | Output | Gate |
|---|---|---|---|---|
| 0 | Preflight | this file | tools, keys, voices, fonts present | every check passes |
| 1 | Brief | `motion-film-brief` | the kind (menu when unclear), the voice source, `BRIEF.md` with a direction sheet, clock skeleton | owner agrees on kind, story, length, voice (taste calls only) |
| 2 | Design system | `motion-film-system` | video theme, components, catalogue board, `VIDEO-SYSTEM.md` | catalogue board passes one critique round |
| 3 | Voice or footage | `motion-film-voice` or `motion-film-footage` | AI takes, own recording or a footage edit, all as word-timing JSON | speech-to-text matches the script; lines fit their slots; no cut inside a word |
| 4 | Score | `motion-film-score` | mixed WAV per video (synthesized score, or a licensed track with detected beats) | loudness target met; voice band well clear of the bed |
| 5 | Build | `motion-film-build` | compositions | key-frame boards pass one critique round |
| 6 | QA | `motion-film-qa` | evidence pack | all checks pass; findings fixed in one batch, confirmed once |
| 7 | Deliver | `motion-film-deliver` | renders, web encodes, posters, README | files probe correctly; no generated media committed |

Voice comes before the final clock: real line lengths set the slots. The build can start from the brief with placeholder slots and retime once takes exist. A silent or music-only video skips phase 3; a footage-based video takes its timing from the edit.

## 0. Preflight

Check, do not assume. Report everything missing in one message.

```sh
node --version          # 20+
ffmpeg -hide_banner -encoders | grep -E "libx264|libvpx-vp9|libopus|aac"
python3 -c "import numpy, scipy, PIL; print('python ok')"
npx remotion --version  # inside the video project
```

- **Remotion project:** the suite assumes one exists. If not, set it up with Remotion's own guide (https://www.remotion.dev/docs, `npx create-video@latest`), then come back. Remotion has its own licence (https://www.remotion.dev/license): free for individuals, non-profits and companies of up to 3 people; larger companies need a company licence. Tell the owner before building if that may apply.
- **Fonts:** the brand's font files are copied into the video project's `public/fonts/` (keep them out of git if licences or size require).
- **Voice-over:** a text-to-speech provider that returns word or character timestamps (ElevenLabs by default) and a speech-to-text endpoint for checking. The voices you plan to use must exist in that account. Check credits before generating: voice work costs money, so say so up front.
- **Browser:** Chrome plus the `browser-use` CLI, to capture the live product and to check the video in its real page.
- If the project already has a media setup script, run it first, and never commit what it downloads.
- **Copy the scripts and templates into the video project** (for example `video/scripts/`, `video/src/film/`) instead of running them from the skill folder. Node resolves `remotion` from the script's own location, and `synth.py` writes its cache next to itself.

## Working rules

- **Reversible work goes ahead.** Building, rendering, retiming and re-mixing can be undone: do them and show the result.
- **Ask only the taste calls.** The kind of video when the request is unclear, the story, the voice source and voice, the music character, and anything that spends money or overwrites shipped media. Offer options with a recommendation, in one message.
- **Translate feedback into numbers** before changing anything ("make it pop" becomes a 1.0 → 1.08 → 1.0 pulse over 0.2 s on the beat), and point at frames, not impressions (`motion-film-qa`).
- **Re-read the brand rules at the start of every job.** They change between jobs, sometimes back and forth. Memory is not a source.
- **Never regenerate shipped voice-over** unless the owner asks. A new take changes word timings and breaks the sync.
- **Never commit generated media** (renders, mixes, audio takes, downloaded fonts). Commit sources, clocks, scripts and word-timing JSON.
- **Run long renders in the background.** Wait with an `until` loop on a sentinel, not chained sleeps. Never render review stills while a swap-and-restore render is running; they share files.

## Companion skills

All optional. Each makes a phase better; none is required. Check which ones are installed and use them; without one, use the fallback.

| Need | Skill | Get it | Without it |
|---|---|---|---|
| Project context, critique, typography, extracting and documenting tokens and components, final polish | `impeccable` (`context`, `critique`, `typeset`, `extract`, `document`, `polish`) | https://github.com/pbakaus/impeccable (`npx impeccable install`) | Critique with the checklists in `motion-film-qa` Part 1; take tokens by hand as `motion-film-system` describes |
| Motion critique of key-frame boards and timing | `review-animations` | https://github.com/emilkowalski/skills (`npx skills@latest add emilkowalski/skills`) | Use the motion checklist in `motion-film-qa` Part 1 |
| Building one animation right; naming an effect | `animate`, `animation-vocabulary` | same repo | `motion-film-build/PATTERNS.md` and the motion tokens |
| Polish and invisible details | `emil-design-eng` | same repo | The bar above and the lessons below |
| Capturing live product screens and states; checking the video in its page | `browser-use` (browser-harness) | https://github.com/browser-use/browser-harness | Any headless browser that can take screenshots (Playwright, Puppeteer); check the embed by hand |

## Lessons that cost a re-render

Details live in the phase skill named in brackets.

1. **Stills miss stacking bugs.** They render each scene alone. A later scene with an opaque background can cover the previous scene's exit. Always pull transition frames from the real output file. (qa, build)
2. **A second copy of a scene duplicates SVG ids.** Loop overlays and motion-blur samples render extra copies, and a copy can pick up the live copy's clip path or mask. Use per-instance ids. (build)
3. **Motion blur can blur nothing.** If the blurred subtree gets time as a prop from outside, every sample is identical. The subtree must read the frame itself. (build)
4. **Hard-coded fps breaks speed.** Helpers written for 60 fps ran at half speed in a 30 fps video. Express springs, typing speed and durations in seconds. (build)
5. **Text measured before fonts load lays out wrong**, and silently. Gate rendering on font load. (build)
6. **Some TTS models ignore `speed`.** Use an English pace direction (for example `[upbeat, brisk pace]`) or a pitch-preserving tempo change at ship time. (voice)
7. **A direction tag in a non-English language was spoken aloud.** Use English tags, and confirm with speech-to-text that the tag is silent. (voice)
8. **Speech-to-text catches slurred names** a skimming listener misses. Regenerate with another seed and keep a take of the same length. (voice)
9. **You cannot hear.** Verify audio with speech-to-text, loudness, stem levels and a spectrogram, and say that the music still needs human ears. (score, qa)
10. **Overlapping caption pills look broken.** Play caption chunks in sequence and split at punctuation. (build)
11. **Posters catch captions mid-reveal.** Pick the poster frame after every word on screen has landed. (qa, deliver)
12. **"Ends near frame 0" is not a loop.** Cross-fade into a frozen copy of frame 0, then check first-vs-last-frame PSNR ≥ 40 dB. (build, qa)
13. **Logos never overshoot.** No bouncy springs on brand artwork; reveal it with masks and ease-out. (system)
14. **Never retype a wordmark.** Draw it from the brand's artwork paths. (system)
15. **A set built on one template gets rejected.** Give each video its own story and its own motion language. (brief)
16. **Third-party names are fine as text; their logos come only from an approved, vendored set**, in their own colours. (system)
17. **Small playback shrinks everything.** A 1920-wide frame shown 900 px wide scales text by about 0.47. At 1080p keep captions ≥ 56 px and interface text ≥ 26 px. Vertical video has its own minimums and safe zones. (system, build)
18. **Stop polishing after one confirming round.** Batch every finding, fix once, confirm once. (qa)

## Reporting

- **To an orchestrator or another agent:** one line with what changed and the paths of the evidence you checked.
- **To the owner:** what was made and where; what was verified, with numbers; what still needs human eyes or ears; any decision that is theirs.
