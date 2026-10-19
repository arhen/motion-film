"""Read a word-timed transcript the way an editor does, and draft a cut list.

    python3 pauses.py footage/talk.words.json --media footage/talk.mp4 [--gap 0.6] [--pad 0.12]
                      [--from 12.0] [--to 58.0] [--fillers um,uh,erm,er,ah,hmm,mm,eh,emm] [--edl out/talk.edl.json]

Prints the transcript with source timestamps, one phrase per line, a new phrase at every pause of --gap
seconds or more, with filler words in brackets. Pauses come from the audio itself when --media is given
(recommended: local transcription timings can run words together), else from gaps between words.
Then proposes keep segments: the speech with --pad seconds of air on each side and the long pauses removed.
Filler words are marked for you to cut by hand. The proposal is a first draft: read the transcript, pick the
clip, and edit the segments.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quiet import load, silences  # noqa: E402

args = sys.argv[1:]
opts = {"--gap": "0.6", "--pad": "0.12", "--from": None, "--to": None, "--fillers": "um,uh,erm,er,ah,hmm,mm,eh,emm", "--edl": None, "--media": None}
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if not args:
    sys.exit(__doc__)
src = Path(args[0])
data = json.loads(src.read_text())
gap, pad = float(opts["--gap"]), float(opts["--pad"])
lo = float(opts["--from"]) if opts["--from"] else 0.0
hi = float(opts["--to"]) if opts["--to"] else 1e9
fillers = {f.strip().lower() for f in opts["--fillers"].split(",") if f.strip()}
words = [w for w in data["words"] if w["start"] >= lo - 0.01 and w["end"] <= hi + 0.01]
if not words:
    sys.exit("no words in range")
hi = min(hi, words[-1]["end"] + 1.0)


def norm(s):
    return re.sub(r"[^\w]", "", s.lower())


if opts["--media"]:
    quiet = [(a, b) for a, b in silences(load(opts["--media"]), gap) if b > lo and a < hi]
else:
    quiet = [(a["end"], b["start"]) for a, b in zip(words, words[1:]) if b["start"] - a["end"] >= gap]


def pause_after(i):
    """The pause between word i and the next one, if any (by midpoint, so coarse word ends still match)."""
    if i + 1 >= len(words):
        return None
    for a, b in quiet:
        if words[i]["start"] < (a + b) / 2 <= words[i + 1]["start"]:
            return (a, b)
    return None


print(f"# {data.get('source', src.name)}  ({len(words)} words, {words[0]['start']:.2f} to {words[-1]['end']:.2f} s)")
print(f"# pauses from {'the audio' if opts['--media'] else 'word gaps'}, {gap} s or longer\n")
line, start = [], words[0]["start"]
for i, w in enumerate(words):
    line.append(f"({w['w']})" if norm(w["w"]) in fillers else w["w"])
    p = pause_after(i)
    if p or i == len(words) - 1:
        end = p[0] if p else w["end"]
        print(f"[{start:7.2f} {end:7.2f}]  {' '.join(line)}")
        if p:
            print(f"{'':19}... pause {p[1] - p[0]:.2f} s")
            start = p[1]
        line = []

speech, t = [], max(lo, words[0]["start"] - pad)
for a, b in sorted(quiet):
    if b <= t:
        continue
    if a > t:
        speech.append([t, a])
    t = b
speech.append([t, min(hi, words[-1]["end"] + pad)])
segs = []
for a, b in speech:
    a, b = max(0.0, a - pad), b + pad
    if b - a < 0.15:
        continue
    if segs and a <= segs[-1][1]:
        segs[-1][1] = b
    else:
        segs.append([a, b])
kept = sum(b - a for a, b in segs)
span = segs[-1][1] - segs[0][0] if segs else 0
print(f"\nproposed keep segments: {len(segs)} ({max(0, len(segs) - 1)} cuts), {kept:.2f} s kept of {span:.2f} s")
for a, b in segs:
    print(f'  {{"in": {a:.3f}, "out": {b:.3f}}}')
marked = [w for w in words if norm(w["w"]) in fillers]
if marked:
    print("filler words to review: " + ", ".join(f"{w['w']}@{w['start']:.2f}" for w in marked))
if opts["--edl"]:
    edl = {"file": data.get("source", ""), "segments": [{"in": round(a, 3), "out": round(b, 3)} for a, b in segs], "seconds": round(kept, 3)}
    Path(opts["--edl"]).parent.mkdir(parents=True, exist_ok=True)
    Path(opts["--edl"]).write_text(json.dumps(edl, indent=1))
    print(f"wrote {opts['--edl']} (paste segments into clock.footage.segments)")
