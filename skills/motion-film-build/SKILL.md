---
name: motion-film-build
description: Build motion videos in Remotion (React) from a brief, a clock file and a video design system. Covers the project skeleton, compositions sized from the clock, one layout per format, font gating, seconds-based springs and easing, word-synced captions, scene choreography per motion language, camera moves, motion blur, seamless loops and deterministic randomness, plus the pitfalls that silently break renders (scene stacking, duplicate SVG ids, frozen props, fps-coupled helpers, text measured before fonts). Use when writing or changing the picture of a product or content video. Part of the motion-film suite.
---

# Build the picture

The picture is a pure function of the frame. Everything that moves reads the time, and every time comes from the clock file. Craft lives in curves, timing and restraint; correctness lives in the pitfalls at the bottom of this page.

For motion craft decisions on a single element (curve, duration, what to animate at all), load `animate`. To name an effect, load `animation-vocabulary`.

## 1. Skeleton

```
video/
  clock.json (or one per video)   timings: vo slots + named cues
  src/index.ts, src/Root.tsx      compositions, durations computed from clock.seconds × fps
  src/theme.ts                    imports product tokens (motion-film-system)
  src/lib/anim.ts                 easing, seconds-based springs, noise helpers   ← templates/anim.ts
  src/lib/clock.ts                clock access, word times, beat ↔ seconds       ← templates/clock.ts
  src/lib/FontsGate.tsx           font loading gate                              ← templates/FontsGate.tsx
  src/components/                 rebuilt product components, brand artwork, captions, sample tag
  src/films/<Video>.tsx           one file per video; scenes as functions of t
  scripts/, audio/, vo/, public/  see the voice, score and QA skills
```

- **Pin the Remotion version.** Register every video as a `<Composition>` whose duration is `Math.round(clock.seconds * clock.fps)`.
- **Render settings:** h264, CRF 14-18, `--color-space=bt709`, JPEG frames at quality 92-95, and an explicit concurrency.

### Formats

- **One composition per format,** same component and clock: `<id>` at 1920×1080, `<id>-9x16` at 1080×1920, `<id>-4x5` at 1080×1350 if asked. Never render landscape and crop it.
- **Scenes read the format** with `useVideoConfig()` and switch layout: side by side in landscape, stacked in a tall frame. Pick type sizes with `typeFor(width, height)` from the theme.
- **Captions adapt by themselves** (`Subtitles.tsx`): size, position and chunk length follow the frame. In a tall frame they sit above the bottom safe zone and break into shorter chunks.
- **Keep everything important out of the platform safe zones** (`motion-film-system` §6) and check the key-frame board with `grid.py --safe`.

## 2. Time

- **Work in seconds.** Use `const t = frame / fps`, and pass seconds to springs, easing windows and typing speeds. A file written for 60 fps then still works at 30.
- **Read every cue from the clock** (`clock.cues.turn`) or from a word time (`wordAt(line, word)`). Never type a magic number into a scene.
- **Visuals lead speech slightly.** Start a caption word or a visual 0.08-0.12 s before the word's onset.
- **Beat-driven videos:** convert beats to seconds with `beat × 60 ÷ bpm`. Put structural changes on beats and small events on 8ths or 16ths.

## 3. Motion

- **Entrances ease out; exits ease in; moves and camera ease in-out.** Use only the curves and springs in the video design system.
- **Springs are analytic,** `springT(seconds, f, z)` (in `anim.ts`), so they work at any sub-frame time (needed by motion blur). Calm UI uses `z ≥ 0.75`; playful UI uses `z 0.4-0.6`. The logo never overshoots.
- **Stagger lists** by 40-80 ms. Never animate everything at once.
- **One hero move at a time.** Secondary elements start 100-200 ms after the hero and travel 50-70 % as far, so everything settles together instead of all at once.
- **Distance sets duration.** A longer travel takes longer (a base plus a few ms per 10 px); identical durations for different distances look mechanical. Scale and zoom interpolate in log space (`logLerp`).
- **Camera:** a slow push-in (3-7 % over the video) keeps static scenes alive. For a rack focus, blur and dim the background while the foreground arrives. A whip pan moves both scenes the same way, with motion blur.
- **Life without noise:** low-amplitude drift (`noise2D`, 2-6 px) on floating elements. Deterministic randomness only (`random(seed)`); never `Math.random`.
- **One memorable moment per video,** given the most frames and the cleanest frame around it.

## 3a. Rhythm and readability

People cannot read and track motion at the same time. Give them turns.

- **Text and action alternate.** Nothing fast moves while a line is read, and a hero move never starts within about 0.2 s of a text arrival. Text being read drifts by no more than about 1.5 px per frame at 30 fps.
- **Hold to read:** about 0.5 s plus 0.28 s per word, at least 1 s (`holdFor(words)`). At most about 8 words of on-screen text visible at once (captions excepted, since they are paced by the voice).
- **Picture time.** In videos without voice, statements are on screen for at most about two thirds of the runtime, with at least 1.5 s of text-free picture in every 10 s.
- **Typing speed by role.** Text typed for the viewer to read: 20-30 characters per second with human rhythm (quicker spaces, a short pause after punctuation). A fast "AI writes it" burst can run faster, but then holds for at least 1 s so it can be read.
- **No dead holds.** No stretch longer than about 1.2 s without a visible change; a hold keeps slow life (0.3-1 px per frame of drift, or a 1-3 % scale creep). One planned near-still moment is allowed, on the key claim.
- **The hook.** Frame 0 is composed and already moving, and something visibly changes within 0.3 s; muted feeds decide in a second.

## 3b. Speed, blur and cuts

- **Speed budget.** Measure the fastest on-screen speed per move (px per frame at the delivery fps). Ordinary moves stay under about 25 px per frame at 60 fps (50 at 30). Motion blur starts to help above roughly 12-40 px per frame. Above about 70 px per frame, blur leaves stepped copies: redesign the move as a cut, a mask wipe or a match cut instead. Frame-filling wipes are the exception.
- **Velocity-matched cuts.** Either both sides of a cut are at rest, or the outgoing move speeds up into the cut and the incoming shot starts at that same speed, in the same screen direction. Match the properties that cross the seam (position, scale, colour). Show a resting pose once, not on both sides.
- **Seam variety.** Several transition types per video, none used more than twice; never cross-fade two copies of one object (morph the one object instead).
- **True-cycle loops** are better than a cross-fade when the design allows: things flowing through, an object leaving one side and re-entering the other, an end state that is the start state. Drive cycles with `loopPhase(t, period)` in whole cycles and drift with `loopNoise()`, so the frame after the last one equals frame 0. Keep text off the seam. The cross-fade into `Freeze(0)` is the fallback.

## 3c. Interface and objects in motion

- **Cause, action, result.** Every product action has a visible cause (a cursor press, a message arriving), then the product's real behaviour, then a result held for reading. The state changes on the frame the cause lands.
- **Push in on what matters.** Story-carrying interactions get a 2-5× push-in; a wide shot of unreadable interface lasts at most about 1.7 s. The cursor appears only while someone acts.
- **Objects with weight** (a mascot, a ball, an icon that jumps): anticipation before a move (a crouch about 1.2 wide by 0.75 tall over 8-12 frames), stretch on take-off (about 0.85 by 1.28), squash on landing (about 1.25 by 0.7), a spring back at z about 0.55, parts that lag the body by 3-6 frames, and paths that arc. Keep the volume roughly constant.

## 3d. Sound from the motion

Compute sound cue times from the animation itself, not by typing numbers: a pop at the spring's settle (`springSettle()`), a whoosh peak at the move's peak speed (`springPeakSpeed()`), an impact on the contact frame. Picture leads sound: a hit lands on its visual frame or one frame after it, never before. Export these times into the clock's `cues`, so the mixer reads them.

Patterns with code (word-by-word reveal, bouncing-ball lead, card-to-node morph, iris close, stroke-dash trace reveal, text-to-particles, counting numbers, 3D assembly, notification stack, button press and result) are in [PATTERNS.md](PATTERNS.md).

## 4. Captions

Copy [templates/Subtitles.tsx](templates/Subtitles.tsx).

- **The text is the voice-over,** word for word, revealed per word on its timestamp.
- **Chunks** split at punctuation, fit the frame width (at most 44 characters in landscape, about 19 in a 1080-wide tall frame, so the pill clears the app's button column), and merge into the previous chunk when shorter than 0.9 s and there is room.
- **Chunks play strictly in sequence:** the next pill fades in only after the previous one has faded out. Overlapping pills look broken.
- **Size and style:** ≥ 56 px in landscape for card playback, ≥ 72 px in vertical, in the display face, in a pill that fits light or dark grounds.
- **They stop** before the sign-off lockup.

## 5. Loops and endings

- **Seamless loop.** Render frames 0 to N-1; frame N is frame 0 again and must not be rendered twice. Build each video so frame 0 is a composed, readable opening that is already moving. Over the last 0.4-0.5 s, cross-fade into a frozen copy of the scene at frame 0 (`<Freeze frame={0}>`). [templates/FilmShell.tsx](templates/FilmShell.tsx) does this, and also layers the sign-off, the captions, the sample tag, the grain and the audio.
- **End hold:** the sign-off lockup holds at least 1.2 s; then fade the audio, not the picture.

## 6. Motion blur

Use [templates/MotionBlur.tsx](templates/MotionBlur.tsx) for accumulation blur: N samples at sub-frame times, added with `plus-lighter` at `1/N` opacity.

- **Only in windows.** Apply it during fast moves (whips, flights, implosions), defined in the clock or as a list of time ranges. It multiplies render time by N.
- **The blurred subtree must read the frame itself** (a component that calls `useCurrentFrame`). Props computed outside the blur are frozen, so every sample is identical.
- **Use 5-10 samples** with a shutter of 0.5-1.2 frames. If you see ghost rings, raise the samples.

## 7. Design system in code

- **Fonts:** wrap every composition in `FontsGate` (copy [templates/FontsGate.tsx](templates/FontsGate.tsx)). It loads the brand fonts and preloads image assets before `continueRender`, so the first frame and every text measurement use real metrics.
- **The logo is artwork:** draw it from the brand's path data. Reveal it with masks (a wipe, a sweep, or a stroke-dash trace along the mark's centre line) and ease out. Never retype, deform, or spring-overshoot it.
- **Rebuilt components** take a size multiplier and content props, and pull colours from the theme. A raw hex value in a scene is a missing token.
- **Third-party marks** come from the vendored set, preloaded.

## 7a. Footage

Real footage (a talking head, a screen recording) goes through `motion-film-footage`: the cut list, retiming and `Footage.tsx` (reframing, punch-ins, zooms and the full, split, bubble and cutaway layouts). Explanations draw in `explainRegion()`.

## 8. Review while building

Render key frames at half scale while you work (`motion-film-qa/scripts/stills.mjs`) and look at them: one still per story beat, plus the first and last frame. When a video's scenes are all in place, run the bounded critique round in `motion-film-qa`.

## Pitfalls

The first nine rows each shipped a broken frame once; the rest are known traps of headless rendering.

| Symptom | Cause | Fix |
|---|---|---|
| Blank or covered frames between scenes in the MP4, but stills look fine | A later scene's opaque background covers the earlier scene's exit while both are mounted | Give scenes that overlap a transparent root; put the ground on the shell; or set an explicit `zIndex` per scene |
| A frozen copy shows the wrong clip or mask (an open shutter that should be closed) | Two copies of the same SVG `id` in the DOM; `url(#id)` resolves to the first | Per-instance ids: `` `${name}-${React.useId().replace(/[^a-zA-Z0-9]/g, '')}` `` |
| Motion blur does nothing | Time passed as a prop into the blurred subtree | The subtree calls `useCurrentFrame` itself |
| Springs and typing run at half speed | Helpers divide by a hard-coded 60 fps | Use `useVideoConfig().fps`, or seconds everywhere |
| Centred text sits off-centre in the first render | Text measured before the font loaded | `FontsGate` + `delayRender`; measure inside the gate |
| A dot or particle never arrives at frame N-1 | Travel ends exactly at `seconds`, so the last frame is one frame short | End travel at least one frame before the last frame |
| Images pop in on the first frames | Images inside SVG do not delay rendering | Preload and decode them in the font gate |
| Inconsistent layouts between renders | `Math.random`, `Date.now`, or state | `random(seed)`, `noise2D(seed, …)`, pure functions of `t` |
| Long render times | Motion blur everywhere, heavy filters on many elements | Blur only in windows; cap blurred elements; render stills at 0.5 scale for review |
| Slow text rises tick or shimmer | The headless browser snaps text to whole pixels at low speed | End rises with some speed left (ease out quint, not expo, on long rises), or move the parent with `transform` and keep the text still inside it |
| Animated CSS `filter: blur()` on a large layer steps or flickers | Blur radius is quantised per frame | Cross-fade between a sharp and a pre-blurred copy, or keep the radius fixed and animate opacity |
| Ghost frames on a blurring layer | `will-change` on an element whose filter animates | Remove `will-change` there |
| A shape freezes or vanishes mid-move | A width, height or radius went negative | Clamp geometry at zero or above |
| Gradients band in the encode | 8-bit gradients over large areas | Add grain or ±1-level noise to large gradients, or bake the gradient as a dithered image |
| A loop hitches once per cycle | Frame N rendered as well as frame 0 | Render frames 0 to N-1 |
| Sounds land a frame early on the final file | The audio was typed, not derived from the motion, or the encoder delayed the picture | Derive cue times from the motion; check A/V offset with `motion-film-qa/scripts/avlag.py` |
