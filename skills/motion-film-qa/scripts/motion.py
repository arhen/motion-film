"""Motion over time, measured on the rendered file: the hook, dead holds, pops, frozen frames, flashes, energy.

    python3 motion.py out/film.mp4 [--hold 1.2] [--stills 8.2-9.4,15.0-15.6] [--png out/qa/motion.png]

Decodes small grey frames and measures how much each frame changes from the one before (mean absolute
difference, 0-255). Reports:
  hook     the first visible change; aim for 0.3 s or less (a loop's frame 0 should already be moving);
  holds    stretches longer than --hold seconds with no visible change, except planned stills (--stills);
  pops     a single frame that differs from both neighbours while they match each other (a wrong frame);
  frozen   a repeated frame inside motion (a stutter: a dropped or duplicated frame);
  flashes  more than three bright-dark flashes in any one second (a seizure risk; whole-frame estimate);
  energy   change per second, where the peak and the quietest stretch fall as % of the runtime (and a PNG).
Exits 1 on pops, frozen frames or flash risk.
"""

import json
import subprocess
import sys

import numpy as np

args = sys.argv[1:]
opts = {"--hold": "1.2", "--stills": "", "--png": None}
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if not args:
    sys.exit(__doc__)
src = args[0]
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-of", "json", src], check=True, capture_output=True).stdout)["streams"][0]
num, den = (int(v) for v in probe["r_frame_rate"].split("/"))
fps = num / den
W = 192
H = int(round(probe["height"] * W / probe["width"] / 2) * 2)
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vf", f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"], check=True, capture_output=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
n = len(f)
d = np.concatenate([[0.0], np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))])
lum = f.mean(axis=(1, 2))
STILL, MOVING = 0.05, 0.3
stills = []
for part in filter(None, opts["--stills"].split(",")):
    a, b = (float(v) for v in part.split("-"))
    stills.append((a, b))
planned = lambda t: any(a <= t <= b for a, b in stills)
problems = 0

first = next((i for i in range(1, n) if d[i] > STILL), None)
print(f"{src}: {n} frames at {fps:g} fps, {n / fps:.2f} s")
print(f"hook: first visible change at {first / fps:.2f} s" + ("" if first is not None and first / fps <= 0.3 else "  << later than 0.3 s") if first else "hook: nothing ever changes")

hold = float(opts["--hold"])
run = 0
for i in range(1, n + 1):
    quiet = i < n and d[i] <= STILL
    if quiet:
        run += 1
    elif run:
        a, b = (i - run) / fps, i / fps
        if (b - a) >= hold and not planned((a + b) / 2):
            print(f"hold: {a:.2f}-{b:.2f} s ({b - a:.2f} s) with no visible change")
        run = 0

for i in range(1, n - 1):
    across = np.abs(f[i + 1] - f[i - 1]).mean()
    if d[i] > 4 * across + 2 and d[i + 1] > 4 * across + 2:
        print(f"pop: frame {i} ({i / fps:.2f} s) differs from both neighbours ({d[i]:.1f} vs {across:.1f} across)")
        problems += 1
    if d[i] < 0.01 and d[i - 1] > MOVING and d[i + 1] > MOVING:
        print(f"frozen: frame {i} ({i / fps:.2f} s) repeats the frame before it inside motion")
        problems += 1

steps = np.diff(lum)
flips = [(i, np.sign(s)) for i, s in enumerate(steps, 1) if abs(s) >= 25]
worst = 0
for k, (i, sgn) in enumerate(flips):
    window = [s for j, s in flips[k:] if j - i < fps]
    worst = max(worst, sum(1 for a, b in zip(window, window[1:]) if a != b) // 2 + (1 if len(window) > 1 else 0))
if worst > 3:
    print(f"flashes: {worst} bright-dark flashes within one second  << seizure risk, slow them down")
    problems += 1

sec = max(1, int(round(fps)))
energy = np.array([d[i : i + sec].mean() for i in range(0, n, sec)])
if len(energy) >= 4:
    peak = int(np.argmax(energy))
    mid = energy[len(energy) // 3 : -1] if len(energy) > 4 else energy
    low = len(energy) // 3 + int(np.argmin(mid))
    last = energy[2 * len(energy) // 3 :].mean() / (energy.mean() + 1e-9)
    print(f"energy: peak at {100 * (peak + 0.5) / len(energy):.0f} % ({peak}-{peak + 1} s), quietest at {100 * (low + 0.5) / len(energy):.0f} %, last third at {last:.2f}x the average")
    print("  per second: " + " ".join(f"{e:.1f}" for e in energy))
    if opts["--png"]:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (40 * len(energy) + 40, 220), (251, 250, 247))
        dr = ImageDraw.Draw(img)
        top = energy.max() + 1e-9
        for k, e in enumerate(energy):
            h = int(180 * e / top)
            dr.rectangle((20 + 40 * k + 4, 200 - h, 20 + 40 * k + 36, 200), fill=(51, 85, 255) if k != peak else (229, 72, 77))
            dr.text((20 + 40 * k + 10, 204), str(k), fill=(107, 101, 92))
        img.save(opts["--png"])
        print(f"  wrote {opts['--png']}")
sys.exit(1 if problems else 0)
