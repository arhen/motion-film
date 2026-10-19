"""How much of each frame the accent colour covers.

    python3 accent.py '#3355ff' out/qa/*.jpg [--tol 48] [--max 8]

Counts the pixels within --tol (RGB distance) of the accent. A single accent spent on one thing per scene
stays under about --max percent of the frame; one planned full-frame moment is the exception.
Exits 1 if any frame is over the limit.
"""

import sys

import numpy as np
from PIL import Image

args = sys.argv[1:]
opts = {"--tol": "48", "--max": "8"}
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if len(args) < 2:
    sys.exit(__doc__)
hexv = args[0].lstrip("#")
accent = np.array([int(hexv[i : i + 2], 16) for i in (0, 2, 4)], np.float32)
tol, limit = float(opts["--tol"]), float(opts["--max"])
over = 0
for path in args[1:]:
    px = np.asarray(Image.open(path).convert("RGB"), np.float32)
    share = 100 * (np.linalg.norm(px - accent, axis=2) < tol).mean()
    flag = "  << over" if share > limit else ""
    over += bool(flag)
    print(f"{share:5.1f} %  {path}{flag}")
sys.exit(1 if over else 0)
