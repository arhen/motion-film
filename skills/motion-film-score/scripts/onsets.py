"""Check that sound hits land on their cues: expected cue time vs the strongest onset near it.

    python3 onsets.py <mix.wav|video.mp4> clock.json <cue>[:index] [...] [--window 0.12]

Each cue may be a number or a list in clock["cues"]; every value is checked, or only one with
`name:0` / `name:-1` (for a range cue whose sound sits on one end).
Checks transients (pops, clicks, hits). Swells (whoosh, riser) peak on the cue by construction; skip them.
A delta within one frame (33 ms at 30 fps, 17 ms at 60 fps) is on time.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 48000
args = sys.argv[1:]
window = 0.12
if "--window" in args:
    i = args.index("--window")
    window = float(args[i + 1])
    del args[i : i + 2]
media, clock_path, names = args[0], args[1], args[2:]
clock = json.loads(Path(clock_path).read_text())
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", media, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
x = np.frombuffer(raw, np.float32)
hop = 240
env = np.sqrt(np.convolve(x**2, np.ones(hop) / hop, "same"))[::hop]
rise = np.diff(env, prepend=env[0])
fps = clock.get("fps", 30)

print(f"{'cue':16} {'expected':>9} {'onset':>9} {'delta ms':>9}")
for spec in names:
    name, _, index = spec.partition(":")
    vals = clock["cues"].get(name)
    if vals is None:
        print(f"{name:16} missing in clock")
        continue
    vals = vals if isinstance(vals, list) else [vals]
    if index:
        vals = [vals[int(index)]]
    for t in vals:
        a, b = int((t - window) * SR / hop), int((t + window) * SR / hop)
        a, b = max(a, 0), min(b, len(rise))
        if a >= b:
            continue
        k = a + int(np.argmax(rise[a:b]))
        onset = k * hop / SR
        delta = (onset - t) * 1000
        flag = "" if abs(delta) <= 1000 / fps else "  << off"
        print(f"{name:16} {t:9.3f} {onset:9.3f} {delta:9.0f}{flag}")
