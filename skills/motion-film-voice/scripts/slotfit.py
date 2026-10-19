"""Check that voice-over lines fit their slots on the clock.

    python3 slotfit.py clock.json vo/film [--min-gap 0.05]

Clock voice entries (one per line, in order):
  {"id": "V1", "at": 0.6}                    line starts at 0.6 s
  {"id": "V3", "alignWord": 2, "at": 9.5}    word 2 starts at 9.5 s
  {"id": "V4", "alignWord": 0, "beat": 24}   word 0 lands on beat 24 (needs "bpm")
Each line needs a timing JSON (<id>.json with "words": [{"w", "start", "end"}]) in the VO folder.
Exits 1 when lines overlap, gaps fall below --min-gap, or a line ends after "seconds".
"""

import json
import sys
from pathlib import Path

args = sys.argv[1:]
min_gap = 0.05
if "--min-gap" in args:
    i = args.index("--min-gap")
    min_gap = float(args[i + 1])
    del args[i : i + 2]
clock = json.loads(Path(args[0]).read_text())
vo_dir = Path(args[1])
beat = 60 / clock["bpm"] if "bpm" in clock else None
offset = clock.get("beatOffset", 0.0)


def placement(entry, words):
    if "alignWord" in entry:
        anchor = offset + entry["beat"] * beat if "beat" in entry else entry["at"]
        return anchor - words[entry["alignWord"]]["start"]
    if "beat" in entry:
        return offset + entry["beat"] * beat
    return entry["at"]


ok = True
prev_end = None
print(f"{'line':6} {'start':>7} {'end':>7} {'gap':>7}  first words")
for entry in clock["vo"]:
    words = json.loads((vo_dir / f"{entry['id']}.json").read_text())["words"]
    start = placement(entry, words)
    end = start + words[-1]["end"]
    gap = None if prev_end is None else start - prev_end
    flag = ""
    if gap is not None and gap < min_gap:
        flag, ok = "  << overlap" if gap < 0 else "  << tight", False
    if start < 0:
        flag, ok = "  << starts before 0", False
    if "seconds" in clock and end > clock["seconds"]:
        flag, ok = "  << runs past the end", False
    first = " ".join(w["w"] for w in words[:4])
    print(f"{entry['id']:6} {start:7.2f} {end:7.2f} {'' if gap is None else f'{gap:+7.2f}':>7}  {first}{flag}")
    prev_end = end
sys.exit(0 if ok else 1)
