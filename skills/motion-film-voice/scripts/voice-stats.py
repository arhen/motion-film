"""Objective notes for a voice audition: length, words per second, median pitch, spectral centroid.

    python3 voice-stats.py takes/a.mp3 takes/b.mp3 ...

Words per second needs a timing JSON with the same stem next to the take (as written by vo.mjs).
Lower pitch with a darker centroid tends to read warm and calm; a brighter centroid reads crisp.
These are hints for a shortlist; a person still has to listen.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

SR = 16000


def decode(path):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def median_pitch(x):
    f0 = []
    lo, hi = SR // 400, SR // 60
    for i in range(0, len(x) - 1024, 800):
        frame = x[i : i + 1024]
        if np.sqrt(np.mean(frame**2)) < 0.03:
            continue
        ac = np.correlate(frame, frame, "full")[1023:]
        k = lo + int(np.argmax(ac[lo:hi]))
        f0.append(SR / k)
    return float(np.median(f0)) if f0 else float("nan")


def centroid(x):
    spec = np.abs(np.fft.rfft(x))
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    return float((spec * freqs).sum() / (spec.sum() + 1e-9))


print(f"{'take':32} {'len s':>6} {'w/s':>5} {'pitch Hz':>9} {'centroid Hz':>12}")
for arg in sys.argv[1:]:
    path = Path(arg)
    x = decode(path)
    wps = ""
    timing = path.with_suffix(".json")
    if timing.exists():
        words = json.loads(timing.read_text())["words"]
        if words:
            wps = f"{len(words) / max(words[-1]['end'], 0.01):.2f}"
    print(f"{path.name:32} {len(x) / SR:6.2f} {wps:>5} {median_pitch(x):9.0f} {centroid(x):12.0f}")
