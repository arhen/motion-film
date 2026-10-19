"""Map a footage edit onto the output timeline: word timings, the cut audio, and a check that no cut splits a word.

    python3 retime.py clock.json footage/talk.words.json vo/clip [--id F1] [--fade 0.012]

Reads clock["footage"] = {"file": "footage/talk.mp4", "segments": [{"in": s, "out": s}, ...]} in source
seconds, played back to back in order. The file path is relative to the clock. Writes:
  <vo dir>/F1.json  the words that survive the edit, in output seconds, in the clock line format, so clock.ts,
                    Subtitles, the mixer and sync.py read it like a voice-over take;
  <vo dir>/F1.wav   the source audio cut to the same segments, with a short fade at every cut so nothing clicks.
Then add {"id": "F1", "at": 0} to clock["vo"] and set clock["seconds"] to at least the printed length.
Exits 1 if a cut falls inside a word, or on loud audio (checked on the audio itself, because transcription
timings can be coarse): move that segment edge into the pause next to it.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quiet import load, loud_at  # noqa: E402

SR = 48000
args = sys.argv[1:]
opts = {"--id": "F1", "--fade": "0.012"}
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if len(args) < 3:
    sys.exit(__doc__)
clock_path, words_path, out_dir = Path(args[0]), Path(args[1]), Path(args[2])
clock = json.loads(clock_path.read_text())
foot = clock["footage"]
segs = foot["segments"]
words = json.loads(words_path.read_text())["words"]

starts, t = [], 0.0
for s in segs:
    if s["out"] <= s["in"]:
        sys.exit(f"segment {s} ends before it starts")
    starts.append(t)
    t += s["out"] - s["in"]
total = t

errors = []
for i, s in enumerate(segs):
    for edge in ("in", "out"):
        b = s[edge]
        for w in words:
            if w["start"] + 0.01 < b < w["end"] - 0.01:
                errors.append(f"segment {i} {edge} {b:.3f} splits '{w['w']}' ({w['start']:.3f} to {w['end']:.3f})")

media = (clock_path.resolve().parent / foot["file"]).resolve()
x16 = load(media)
for i, s in enumerate(segs):
    for edge in ("in", "out"):
        if loud_at(x16, s[edge]):
            errors.append(f"segment {i} {edge} {s[edge]:.3f} lands on loud audio (speech or a hit), not in a pause")

out_words = []
for w in words:
    for s, o in zip(segs, starts):
        if s["in"] - 0.01 <= w["start"] and w["end"] <= s["out"] + 0.01:
            out_words.append({"w": w["w"], "start": round(o + w["start"] - s["in"], 3), "end": round(o + min(w["end"], s["out"]) - s["in"], 3)})
            break

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(media), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
x = np.frombuffer(raw, np.float32)
fade = int(float(opts["--fade"]) * SR)
parts = []
for s in segs:
    p = x[int(s["in"] * SR) : int(s["out"] * SR)].copy()
    if len(p) > 2 * fade:
        p[:fade] *= np.linspace(0, 1, fade)
        p[-fade:] *= np.linspace(1, 0, fade)
    parts.append(p)
audio = np.concatenate(parts) if parts else np.zeros(1, np.float32)

out_dir.mkdir(parents=True, exist_ok=True)
lid = opts["--id"]
(out_dir / f"{lid}.json").write_text(json.dumps({"text": " ".join(w["w"] for w in out_words), "words": out_words, "source": foot["file"]}, indent=1))
wavfile.write(out_dir / f"{lid}.wav", SR, audio.astype(np.float32))

print(f"{len(segs)} segments, {len(segs) - 1} cuts, output {total:.3f} s ({round(total * clock.get('fps', 30))} frames)")
print(f"{len(out_words)}/{len(words)} words kept; wrote {out_dir / (lid + '.json')} and {out_dir / (lid + '.wav')}")
if clock.get("seconds", 0) < total:
    print(f"clock seconds {clock.get('seconds')} is shorter than the edit: set it to at least {total:.3f}")
if errors:
    print("\ncut problems:")
    for e in errors:
        print("  " + e)
    sys.exit(1)
print("every cut falls between words, in quiet audio")
