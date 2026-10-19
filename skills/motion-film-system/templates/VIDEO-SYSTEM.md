# Video design system: <product or channel>

**Source of truth:** <token source path> · **Brand rules:** <path>, re-read <yyyy-mm-dd> · **Catalogue board:** `<composition id>`

## Typography

| Role | Family | Weight | Size @1080p | Tracking | Notes |
|---|---|---|---|---|---|
| Display / sign-off | <family> | <w> | <px> | <em> | |
| Caption | <family> | <w> | ≥ 56 | <em> | captions = voice-over |
| Interface text | <family> | <w> | ≥ 26 | 0 | inside rebuilt components |
| Label | <family> | <w> | ≥ 22 | 0 | |
| Mono | <family> | <w> | n/a | 0 | only: <timecodes, keys> |

Playback scale factor: <playback width> ÷ <composition width> = <x>.

## Colour roles

| Role | Token | Value | Use |
|---|---|---|---|
| Brand accent | <token> | <hex> | logo, identity accents |
| Ground, light | | | |
| Ground, dark | | | |
| Ink | | | |
| Functional action | | | the one action per scene |
| Positive / negative / warning | | | sentiment |
| Film-only: <name> | n/a | <hex> | <reason> |

## Logo

- Artwork source: <path to vector paths>; variants: <symbol, inline, stacked, wordmark, micro>
- Colours: <colour> on <ground>; <colour> on <ground>
- Minimum size: <px>; below it, use <micro variant>
- Motion: <reveal type>, <duration>, ease out, no overshoot

## Assets

- Icons: <library>, stroke <w>
- Third-party marks: <vendored path>; name-as-text fallback for <list>
- Fonts: <files>, installed by <setup script>

## Components

| Component | Source in product | Video file | States |
|---|---|---|---|
| | | | |

## Layout

- Title-safe area: <inset>; caption band: <y range>; sample-data tag: <corner>; sign-off: <position>
- Card crop safety: <aspect and inset>

## Motion tokens

| Token | Value | Used by |
|---|---|---|
| ease.out | | |
| spring.calm | f, z | |

## Sound tokens

- Sonic logo: <notes>
- Interface sounds: <list, key>
- Loudness: <LUFS / dBTP> per format
- Voices: <registry path>

## Sample data

- Dataset: <path>; label text: "<tag>"
- Never: invented customers, testimonials, metrics, prices or dates

## Review log

| Date | Round | Findings | Fixed |
|---|---|---|---|
