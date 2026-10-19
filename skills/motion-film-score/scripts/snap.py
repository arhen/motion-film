"""Lock a clock to a supplied track: move cues onto its beat grid and record the music in the clock.

    python3 snap.py clock.json track-beats.json --from 12.34 [--to beat|half|bar] [--max 0.25]
                    [--only drop,turn] [--skip loop,opening] [--gain-db 0] [--dry]

--from     where in the track the video starts (seconds); pick a downbeat or a section start from beats.py
--to       grid to snap to (default beat); bar suits scene changes, half suits fast UI events
--max      leave a cue where it is if the nearest grid point is further than this (seconds)
--only     snap only these cues; --skip leaves these alone (for example the loop window)

Writes into the clock: "bpm", "beatOffset" (video time of a downbeat, so beat 0 is a bar start) and
"music" {file, from, gainDb}, which mix_template.py, clock.ts, slotfit.py and sync.py read.
Voice slots are not moved: re-run slotfit.py afterwards. The clock is rewritten in place (keep it in git).
"""

import json
import os
import sys
from pathlib import Path

import numpy as np

args = sys.argv[1:]
opts = {"--from": None, "--to": "beat", "--max": "0.25", "--only": "", "--skip": "", "--gain-db": "0"}
dry = "--dry" in args
if dry:
    args.remove("--dry")
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if len(args) < 2 or opts["--from"] is None:
    sys.exit(__doc__)
clock_path, beats_path = Path(args[0]), Path(args[1])
clock = json.loads(clock_path.read_text())
bt = json.loads(beats_path.read_text())
start = float(opts["--from"])
beat = 60 / bt["bpm"]
bar = 4 * beat
seconds = clock["seconds"]

if bt.get("fixedGrid"):
    down = (bt["firstDownbeat"] - start) % bar
    grids = {
        "beat": down + beat * np.arange(-8, int(seconds / beat) + 8),
        "half": down + beat / 2 * np.arange(-16, int(seconds / beat * 2) + 16),
        "bar": down + bar * np.arange(-2, int(seconds / bar) + 2),
    }
else:
    b = np.array(bt["beats"]) - start
    d = np.array(bt["downbeats"]) - start
    down = float(d[d >= -0.05][0]) if np.any(d >= -0.05) else 0.0
    grids = {"beat": b, "half": np.sort(np.concatenate([b, (b[:-1] + b[1:]) / 2])), "bar": d}
FINER = {"bar": "beat", "beat": "half", "half": "half"}

only = {c for c in opts["--only"].split(",") if c}
skip = {c for c in opts["--skip"].split(",") if c}
limit = float(opts["--max"])
rows = []


def nearest(t, unit):
    g = grids[unit]
    return round(float(g[np.argmin(np.abs(g - t))]), 3)


def snap_cue(name, v):
    vals = v if isinstance(v, list) else [v]
    if (only and name not in only) or name in skip:
        return v
    unit = opts["--to"]
    new = [nearest(t, unit) for t in vals]
    note = ""
    if len(set(new)) < len(new):
        # Two values on one grid point would fire together: try the next finer grid, else leave the list.
        unit = FINER[unit]
        new = [nearest(t, unit) for t in vals]
        note = f"{unit} grid (coarser grid merged values)"
        if len(set(new)) < len(new):
            new, note = vals, "values too close for the grid, left as is"
    out = []
    for t, g in zip(vals, new):
        if abs(g - t) > limit:
            rows.append((name, t, t, "too far, left as is"))
            out.append(t)
        else:
            rows.append((name, t, g, note))
            out.append(g)
    return out if isinstance(v, list) else out[0]


for name, v in clock.get("cues", {}).items():
    clock["cues"][name] = snap_cue(name, v)

clock["bpm"] = round(bt["bpm"], 3)
clock["beatOffset"] = round(float(down), 4)
src = Path(bt["source"])
clock["music"] = {"file": os.path.relpath(src.resolve(), clock_path.resolve().parent), "from": start, "gainDb": float(opts["--gain-db"])}

print(f"{'cue':16} {'was':>8} {'now':>8} {'moved ms':>9}")
for name, a, b, note in rows:
    print(f"{name:16} {a:8.3f} {b:8.3f} {(b - a) * 1000:9.0f}  {note}")
bars = seconds / bar
print(f"\nbpm {clock['bpm']}  beatOffset {clock['beatOffset']} s  music {clock['music']['file']} from {start} s")
if abs(bars - round(bars)) > 0.02:
    lo_, hi_ = int(np.floor(bars)), int(np.ceil(bars))
    print(f"length {seconds} s = {bars:.2f} bars; a musical loop needs whole bars: {lo_ * bar:.3f} s ({lo_} bars) or {hi_ * bar:.3f} s ({hi_} bars)")
if not bt.get("fixedGrid"):
    print("tempo drifts: snapped to the tracked beats; 'beat' placements in the clock use the average tempo")
if dry:
    print("(dry run, clock not written)")
else:
    clock_path.write_text(json.dumps(clock, indent="\t") + "\n")
    print(f"wrote {clock_path}; re-run slotfit.py to check the voice slots")
