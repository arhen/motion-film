"""Onion skins and frame pairs from the rendered file, for judging spacing, arcs and glitches.

    python3 onion.py out/film.mp4 out/qa/onion-turn.jpg --at 6.2 [--frames 8] [--step 2]
    python3 onion.py out/film.mp4 out/qa/pair-6.23.jpg --pair 6.233

Onion: --frames frames from --at, every --step frames, laid over each other at equal weight, so the spacing
of a move is visible in one image (even spacing = linear; bunching at the end = ease out; a gap = a jump).
Pair: two adjacent frames side by side plus their difference amplified, to find exactly what changed (a pop,
a one-frame shift, a texture swap).
"""

import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

args = sys.argv[1:]
opts = {"--at": None, "--frames": "8", "--step": "2", "--pair": None}
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if len(args) < 2 or not (opts["--at"] or opts["--pair"]):
    sys.exit(__doc__)
src, out = args
rate = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate", "-of", "csv=p=0", src], check=True, capture_output=True, text=True).stdout.strip()
num, den = (int(v) for v in rate.split("/"))
fps = num / den


def grab(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t + 0.5 / fps:.4f}", "-i", src, "-frames:v", "1", "-vf", "scale=960:-2", "-f", "image2pipe", "-vcodec", "png", "-"], check=True, capture_output=True).stdout
    from io import BytesIO

    return Image.open(BytesIO(raw)).convert("RGB")


if opts["--pair"]:
    t = float(opts["--pair"])
    k = round(t * fps)
    a, b = grab(k / fps), grab((k + 1) / fps)
    diff = np.clip(np.abs(np.asarray(a, np.int16) - np.asarray(b, np.int16)) * 4, 0, 255).astype(np.uint8)
    sheet = Image.new("RGB", (a.width * 3, a.height + 24), (28, 26, 23))
    for j, (im, label) in enumerate([(a, f"frame {k}"), (b, f"frame {k + 1}"), (Image.fromarray(diff), "difference x4")]):
        sheet.paste(im, (j * a.width, 24))
        ImageDraw.Draw(sheet).text((j * a.width + 8, 6), label, fill=(255, 255, 255))
else:
    t0, count, step = float(opts["--at"]), int(opts["--frames"]), int(opts["--step"])
    k0 = round(t0 * fps)
    frames = [np.asarray(grab((k0 + j * step) / fps), np.float32) for j in range(count)]
    sheet = Image.fromarray(np.clip(np.mean(frames, axis=0), 0, 255).astype(np.uint8))
    ImageDraw.Draw(sheet).text((8, 6), f"onion: frames {k0}-{k0 + (count - 1) * step} every {step}", fill=(229, 72, 77))
sheet.save(out, quality=90)
print(out, sheet.size)
