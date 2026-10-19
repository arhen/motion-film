"""Labelled contact sheet from still images.

    python3 grid.py out.jpg [--cols 4] [--w 640] [--fps 30] [--safe] img...

Each tile is captioned with its file name, or with "frame  time" when the name holds fNNNN.
--safe tints the areas that short-video apps (Reels, TikTok, Shorts) cover with their own
interface on vertical tiles: top bar, right-hand buttons, bottom caption and username.
The zones are approximate; check each platform's current guide before shipping.
"""

import re
import sys

from PIL import Image, ImageDraw

args = sys.argv[1:]
out = args.pop(0)
cols, width, fps, safe = 4, 640, 30, False
SAFE_ZONES = [(0, 0, 1, 0.115), (0.87, 0.35, 1, 0.75), (0, 0.75, 1, 1)]  # (x0, y0, x1, y1) as fractions
while args and args[0].startswith("--"):
    key = args.pop(0)
    if key == "--safe":
        safe = True
        continue
    val = args.pop(0)
    if key == "--cols":
        cols = int(val)
    elif key == "--w":
        width = int(val)
    elif key == "--fps":
        fps = float(val)
if not args:
    sys.exit("no images")
tiles = []
for path in args:
    im = Image.open(path).convert("RGB")
    im = im.resize((width, round(im.height * width / im.width)))
    if safe and im.height > im.width * 1.2:
        tint = Image.new("RGBA", im.size, (0, 0, 0, 0))
        dt = ImageDraw.Draw(tint)
        for x0, y0, x1, y1 in SAFE_ZONES:
            dt.rectangle((x0 * im.width, y0 * im.height, x1 * im.width - 1, y1 * im.height - 1), fill=(230, 40, 40, 70), outline=(230, 40, 40, 200))
        im = Image.alpha_composite(im.convert("RGBA"), tint).convert("RGB")
    m = re.search(r"f(\d{4,})", path.rsplit("/", 1)[-1])
    label = f"{int(m.group(1))}  {int(m.group(1)) / fps:.2f}s" if m else path.rsplit("/", 1)[-1]
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8 + 7 * len(label), 18), fill=(28, 26, 23))
    d.text((4, 3), label, fill=(255, 255, 255))
    tiles.append(im)
rows = (len(tiles) + cols - 1) // cols
h = max(t.height for t in tiles)
sheet = Image.new("RGB", (cols * width, rows * h), (120, 120, 120))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * width, (i // cols) * h))
sheet.save(out, quality=88)
print(out, sheet.size)
