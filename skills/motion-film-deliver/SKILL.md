---
name: motion-film-deliver
description: Deliver finished motion videos. Covers master renders, web encodes (mp4 + webm) and posters at the right sizes, embed guidance for muted autoplay and loops, a README with logline, length, voice and a three-line TLDR per video plus the full script, archiving the previous version, and keeping generated media out of git. Use when a product or content video is approved and must ship to a site, a store listing, social, or a teammate. Part of the motion-film suite.
---

# Deliver

Delivery is part of the craft. The right file at the right size, a poster that tells the story, and a README someone can act on without asking.

## 1. Masters

- **Picture:** render each composition as h264 at CRF 14-18 (showreels 14, web sources 18), yuv420p, with `--color-space=bt709` so players do not shift the colours.
- **Audio:** AAC at 192-320 kbps, using the mixed score.
- **Alternate:** add a VP9 + Opus WebM master when the site serves WebM (`-b:v 0 -crf 33 -row-mt 1`).
- **Poster:** render it as a still at a frame where every caption word on screen has landed and the frame tells the whole story (often the moment of insight). Use JPEG at quality about 88.
- **Re-probe** every file after rendering (`motion-film-qa/scripts/probe.sh`): codec, size, duration, fps, loudness, true peak, colour tags.
- **Check the A/V offset** (`motion-film-qa/scripts/avlag.py out/<id>.mp4 <mix>.wav`). If it is over half a frame, render the picture muted and mux the mix with ffmpeg: `ffmpeg -i picture.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4`, then check again.

## 2. Web encodes

```sh
bash scripts/encode-web.sh out/<id>.mp4 out/<id>-poster.jpg ../site/public/videos <id> 1600 1280
```

This writes `<id>.mp4` (h264 CRF 26, `+faststart`, AAC 96 kbps), `<id>.webm` (VP9 CRF 36, Opus 96 kbps) and `<id>-poster.jpg`, keeping the master's aspect ratio and tagging BT.709. Pick the width from the largest rendered size on the page × device pixel ratio, capped at about 1600 for cards. Keep the poster smaller (about 1280).

- **Vertical on a page:** 720 px wide is usually enough (`encode-web.sh out/<id>-9x16.mp4 … <id>-9x16 720 720`).
- **Short-video apps:** upload the 1080×1920 master itself, not a web encode. The apps re-encode it, and a small upload loses more.

### Platforms

| Where | Upload | Notes |
|---|---|---|
| X | MP4, h264 High, yuv420p, `+faststart`, AAC, up to 60 fps; 1920×1080 (16:9), 1080×1080, 1080×1350 or 1080×1920 | Aspect between 1:3 and 3:1; about 140 s without a paid tier. Feeds autoplay muted: the picture must work silently. |
| Reels, TikTok, Shorts | the 1080×1920 master, h264 + AAC, 30 fps | Keep text out of the app's interface zones (`grid.py --safe`). Length limits change often: check each platform's current upload guide. |
| A page | `encode-web.sh` mp4 + webm + poster | See the embed guidance below. |

Choose the canvas before the first frame: a different aspect is a different layout, not a re-crop.

### GIF (when a platform or a doc needs one)

```sh
ffmpeg -i out/<id>.mp4 -vf "fps=25,scale=1200:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" -loop 0 out/<id>.gif
```

GIF frame delays are whole hundredths of a second, so 24 or 30 fps cannot be timed exactly and the loop drifts; 25 fps (4/100 s) or 20 fps (5/100 s) is exact. Avoid large gradients (they band in 256 colours), keep the file under the platform's limit (X: 15 MB and 350 frames), and make frame 0 a finished composition, since it shows while the GIF loads.

## 3. Embed guidance (hand this to the page owner)

```html
<video autoplay muted loop playsinline preload="metadata" poster="/videos/<id>-poster.jpg">
	<source src="/videos/<id>.webm" type="video/webm" />
	<source src="/videos/<id>.mp4" type="video/mp4" />
</video>
```

- Browsers block autoplay with sound. Start muted. A user gesture (a tab click, a play button) may unmute: set `video.muted = false` and call `play()`.
- Captions carry the story when muted; that is why they are the voice-over.
- Honour reduced motion: show the poster and a play control instead of autoplay.
- One playing video at a time; pause videos that leave the viewport.

## 4. README per set

Copy [templates/README-films.md](templates/README-films.md). For each video, write:

- the title, a one-line logline, and the length;
- the voice name and gender (or "music only");
- a **three-line TLDR** in the site's language, ready to paste next to the video:
  1. the situation;
  2. what the product (or the idea) does;
  3. what the person does, and the result;
- the motion language;
- the script table (voice-over start times and lines; the sign-off marked as not voiced if it is not);
- the files, with sizes and durations;
- shared behaviour (loop, captions, sample data, sound in the browser), the rebuild commands, and any deviation from the brief, with its reason.

Generate the tables from the clock, the scripts and `ffprobe` output rather than typing them.

## 5. Versions and git

- **Archive** the previous set in `out/<set>/v<N>/` before overwriting, so the owner can compare.
- **Commit:** sources, clocks, scripts, voice scripts, word-timing JSON, small posters (if the site needs them in the repo), the README.
- **Never commit:** renders, mixes, audio takes, web video encodes, downloaded fonts. Check `git status` before staging, and stage explicit paths only.
- **Ask before** pushing or uploading anywhere public.

## 6. Hand-off message

- **To an orchestrator:** one line with what changed and the evidence paths.
- **To the owner:** where the files are, what was verified (numbers), what needs their eyes or ears, and any choice that is theirs.
