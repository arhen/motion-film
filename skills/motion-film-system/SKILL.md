---
name: motion-film-system
description: Build the video design system that makes every motion video for a product or channel look and sound like one family. It is derived from (and imports) the product's design tokens and brand rules, then extended for video. Covers the type scale for real playback sizes, colour roles, logo and asset rules, third-party marks, rebuilt components, layout and safe areas, motion tokens, sound tokens, sample-data rules, plus a catalogue board that is critiqued before any video is built and an audit that catches drift. Use before the first video of a project, when videos look inconsistent, or when a design or brand update must reach the videos. Part of the motion-film suite.
---

# Video design system

Consistency comes from a system, not from discipline. Build this once per project; every video imports it. When the brand changes, change it here and re-render.

## Principles

- **Import, never copy.** The video theme imports the product's token source (generated TS/JSON, CSS variables parsed at build) and the brand's artwork paths. A copied hex value drifts the day the brand changes.
- **Extend, never override.** Video needs things the app lacks: bigger type, film-only tints, motion and sound tokens. Add them as named, documented tokens next to the imported ones.
- **One place per decision.** Fonts, logo, captions, the sample-data tag and the sign-off each live in one component that every video uses.
- **Review the system before any video.** A catalogue board that shows every token and component is cheaper to critique than a film.

## 1. Intake

1. Run the `impeccable` context once (`<impeccable dir>/scripts/impeccable context --target <product src>`). It loads the product brief and the design document.
2. Read the brand guidelines end to end. Write down the hard rules: logo use, colours per ground, fonts and weights, tracking, domain, tagline, sign-off, and what is banned.
3. Find the token source and the component inventory. If the product has none, run `impeccable document` to write the design document, or `impeccable extract` to pull tokens and components out of existing code.
4. Capture the live product with `browser-use`: every screen and state the brief needs, at desktop and mobile widths, light and dark if both exist. Save them as reference stills next to the video project. They are reference, never footage.

## 2. Typography

The video type scale is built for the size at which the video is actually seen.

- **Scale factor** = playback width ÷ composition width. A 1920 frame shown in a 900 px card plays at 0.47×.
- **Minimums per format.** Aim for about 26 px captions, 12 px interface text and 10 px labels on the viewer's screen, then divide by the scale factor:

| Format | Composition | Usually seen at | Scale | Captions | UI text | Labels |
|---|---|---|---|---|---|---|
| Landscape in a page card | 1920×1080 | ~900 px card | 0.47 | ≥ 56 px | ≥ 26 px | ≥ 22 px |
| Landscape full width (hero) | 1920×1080 | 1280 px and up | ≥ 0.67 | ≥ 40 px | ≥ 20 px | ≥ 16 px |
| Vertical, square, 4:5 on a phone | 1080×1920, 1080×1080, 1080×1350 | ~390 px wide | 0.36 | ≥ 72 px | ≥ 34 px | ≥ 28 px |

  The theme template holds the first and last rows as `TYPE` and `TYPE_PHONE`; `typeFor(width, height)` picks one. Use the card row for a hero video too unless you know it never plays small.
- **Roles:** display (titles, captions, sign-off) uses the brand display face; interface text uses the product's UI face; monospace only where the brand allows it (often timecodes and keyboard hints only). Use sentence case unless the brand says otherwise.
- **Tracking and weight** come from the brand table, not taste.
- **Measurement:** any layout that depends on text width (word-by-word reveals, centred lockups, particle text) measures with the real font after it has loaded. See `motion-film-build`.

Run `impeccable typeset` on the catalogue board when the scale is first set.

## 3. Colour roles

- **Brand colours** (logo, identity accents, grounds) and **functional colours** (actions, sentiment, warnings) are separate roles even when the hex values look close. Keep both, named.
- **Grounds:** decide light and dark grounds per motion language, and the logo colour on each.
- **Film-only shades** (hairlines tuned for compression, glows, tints for large areas) are allowed when documented with a reason.
- **One accent rule:** if the brand has a single accent, every scene spends it on one thing: the brand, the alert, or the one action. Keep it under about 8 % of the frame's pixels outside one planned full-frame moment; new items can arrive in the accent and settle to neutral over 0.2-0.5 s. `motion-film-qa/scripts/accent.py` measures it on stills.
- **Contrast:** text keeps at least 4.5:1 against what is behind it on every frame, including mid-transition and over footage.
- **Flashes:** no more than three bright flashes per second, and no large saturated red flashes. Viewers with photosensitive epilepsy see your video too; `motion-film-qa/scripts/motion.py` flags it.

## 4. Logo and assets

- **Logo:** draw it from the brand's vector artwork (exported path data), never retyped in a font. Never rotate, mirror, recolour outside the approved pairs, or deform it. Keep its clear space.
- **Logo motion:** uniform scale, opacity, and mask reveals only (a wipe, a sweep, or a stroke-dash trace along the mark's centre line under a mask). Ease out; **no overshoot**. Use the small-size drawing (favicon or micro variant) below its minimum size.
- **Third-party marks:** platform and partner logos come only from an approved, vendored set, at their own colours; otherwise show the name as text with a neutral icon. Preload raster or SVG marks before the first frame.
- **Icons:** one icon library, one stroke weight.
- **Illustrations and scenes:** built as vector shapes in code, in the brand palette, so they animate and stay consistent. Avoid stock footage.
- **Fonts:** licensed files copied into the video project by a setup script, loaded with a font gate.
- **End card:** the lockup assembles over about 1 s, then holds about 1 s while still moving slightly (a small push or settle); under about 2.5 s in all. One practical line (the URL, a date, the call to action) arrives after the name and stays readable for at least 1.5 s. The logo appears once, here, not on every scene.

## 5. Components

Rebuild the product's components for video, at video scale:

1. Start from the component's real source and the captured reference still.
2. Scale it to the video type scale. Usually that means a size multiplier prop; keep internal proportions.
3. Keep data out of components: pass in the content from the shared sample dataset.
4. Add video-only states the app does not have, such as a notification arriving or a button mid-press.
5. Register every component on the catalogue board.

The usual set: cards and list items, chips and sentiment tags, buttons (rest, hover, pressed, done), notification banners, phone and laptop frames, charts and graphs, the cursor, the caption pill, the sample-data tag, the sign-off lockup.

## 6. Layout

- **Safe areas, landscape:** keep text inside the title-safe area (90 % of the frame) and the essential action inside the card crop if the page crops the video.
- **Safe areas, vertical (Reels, TikTok, Shorts):** the app draws its own interface over the video. Keep text, faces, the product and the logo out of these zones on 1080×1920:
  - top 0 to 220 px (status bar, tabs);
  - right 940 to 1080 px from y 670 to 1440 (like, comment, share buttons);
  - bottom 1440 to 1920 px (username, post caption, music line).

  Check with `motion-film-qa/scripts/grid.py --safe`. The zones are approximate and move between app versions; check each platform's current guide before shipping.
- **Fixed bands:** a caption band (landscape: bottom, about 94 % of the height; vertical: about 70 % of the height, above the bottom zone), a corner for the sample-data tag, and the sign-off position.
- **One layout per format.** A vertical cut is designed, not cropped: the same story, clock and components, rearranged for a tall frame (stack instead of side by side, bigger type, fewer elements per frame). See `motion-film-build` §1.
- **Vertical inside horizontal:** to show 9:16 content in a landscape video, place the device at the left or centre and keep the right side for the story.

## 7. Motion tokens

Write these down and use only these. They are defaults to start from, not laws; each motion language picks its subset.

**Curves**

| Token | Value | Use |
|---|---|---|
| Ease out expo | cubic-bezier(0.16, 1, 0.3, 1) | text and logo reveals |
| Ease out quint | cubic-bezier(0.22, 1, 0.36, 1) | calm, premium entrances |
| Ease in-out cubic | cubic-bezier(0.65, 0, 0.35, 1) | moves, layout changes |
| Ease in-out quart | cubic-bezier(0.76, 0, 0.24, 1) | camera pushes and pans (the softest) |
| Ease in quint / expo | (0.64, 0, 0.78, 0) / (0.7, 0, 0.84, 0) | exits, falls |
| Ease out back | cubic-bezier(0.34, 1.56, 0.64, 1) | a playful pop on objects only |
| Linear | | rotation, progress bars, loop phase only |

Enter with ease out, leave with ease in, and make exits 40-50 % shorter than entrances.

**Springs** (natural frequency `f` in Hz, damping ratio `z`; in seconds, so they survive an fps change)

| Token | Value | Feel |
|---|---|---|
| Calm, premium | f 2.2, z 0.75-0.85 | settles with a hint of life |
| Playful | f 2.6, z 0.4-0.6 | visible bounce; never on the logo |
| Kinetic | f 3.0-3.4, z 0.42-0.55 | snappy social motion |
| Critically damped | z 1.0 | no overshoot at all |

Below z 0.3 reads as cartoonish. Position and scale may overshoot; opacity and colour never do. Converting a Remotion spring config: `z = damping ÷ (2 × √(stiffness × mass))`, `f = √(stiffness ÷ mass) ÷ 2π`. Remotion's default (mass 1, damping 10, stiffness 100) is z 0.5, which is playful, not calm (`fromRemotionSpring()` in `anim.ts`).

**Durations and spacing**

| Token | Value |
|---|---|
| Interface feedback | 100-200 ms |
| Interface moves | 200-500 ms, longer for longer travel |
| Hero reveals | 600-900 ms |
| Camera moves | 0.6-3 s; the slowest move in a video is at least 3× the fastest |
| Stagger | letters 1 frame; words 60-120 ms; list items 40-80 ms; flicks 100-150 ms |
| Overlap | the next element starts when the previous is 30-50 % done |
| Secondary motion | travels 50-70 % as far as the hero and starts 100-200 ms after it, so both settle together |
| Ambient drift | under 5 % of the hero's travel; 2-6 px |
| Parallax layers | foreground 1.0, middle 0.5, background 0.2 |
| Caption word reveal | 0.15-0.2 s rise with a short blur |
| Reading hold | about 0.5 s plus 0.28 s per word, at least 1 s (`holdFor()`) |
| Logo reveal | 0.5 s mask sweep, ease out, no overshoot |
| Phone exaggeration | key poses 10-30 % further than they would be for a large screen |

## 8. Sound tokens

- **Sonic logo:** two or three notes that close every video.
- **Interface sounds:** pop, click, chime, swish and stamp, pitched to the score's key.
- **Loudness targets:** about -14 LUFS for showreels and -16 LUFS for web loops, with a true peak at or below -1.0 to -1.5 dBTP.
- **Voice registry:** active voices and their ids, plus retired and audition voices clearly marked.

## 9. Sample-data rules

- **One shared fictional dataset:** cast, businesses, handles, numbers. Every video quotes it, so numbers agree across videos.
- **Label:** a quiet sample-data tag, styled like the product's own, on product scenes.
- **No invented** customers, testimonials, metrics, prices or dates.
- **The data checks itself.** Write the dataset as code that asserts its own consistency when it loads: weekdays match dates, counts match the items listed, sums and percentages add up, sorted lists are sorted, story facts hold (the person who paid is the person in the receipt). A frame paused anywhere, in-betweens included, must still make sense.
- **Proofing:** "No messages", never "0 messages", and "1 message", never "1 messages"; one date, time and currency format; typographic quotes and apostrophes; tabular figures for every number that changes; no placeholder names or lorem ipsum. A word revealed letter by letter must not spell another word on the way.

## 10. The catalogue board and its review

Copy [templates/Catalog.tsx](templates/Catalog.tsx) into the video project. It is one still composition that shows:

- type specimens per role;
- the colour roles on each ground;
- the logo on each ground, at large and small size;
- every component in every state;
- the caption pill, the sample-data tag and the sign-off.

Render it, then run **one bounded critique round** on it:

1. `impeccable critique` on the board against the brand and design documents.
2. `review-animations` on a short strip of motion token samples, if you render one.
3. Fix every finding in one batch, re-render once, and stop.

Then fill in [templates/VIDEO-SYSTEM.md](templates/VIDEO-SYSTEM.md) and keep it next to the video project.

## 11. Drift audit

Before every delivery, run `motion-film-qa/scripts/brand-audit.sh` with the project's patterns. It flags:

- a retyped wordmark;
- banned fonts, or monospace outside its allowed roles;
- old domains;
- raw hex values outside the theme.
