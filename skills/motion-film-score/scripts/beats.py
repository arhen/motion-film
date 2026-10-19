"""Beat grid of a supplied music track, so a video's cues can lock to it.

    python3 beats.py track.mp3 [--min 70] [--max 180] [--json out/track-beats.json]

Prints the tempo, how well a fixed grid fits (produced music fits within a few ms; live music drifts),
the downbeats (bar starts, estimated from the low end), and candidate section starts where the
energy jumps. Feed the JSON to snap.py to move the clock's cues onto the grid.
Assumes 4/4. Check the downbeats against the drum pattern; the estimate can be one beat off.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

SR = 22050
HOP = 256
FPS = SR / HOP

args = sys.argv[1:]
opts = {"--min": "70", "--max": "180", "--json": ""}
for k in list(opts):
    if k in args:
        i = args.index(k)
        opts[k] = args[i + 1]
        del args[i : i + 2]
if not args:
    sys.exit(__doc__)
src = args[0]
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
x = np.frombuffer(raw, np.float32).astype(np.float64)
if len(x) < SR * 4:
    sys.exit("track shorter than 4 s")

# Onset strength: positive spectral flux of log magnitude, trend removed.
f, _, Z = signal.stft(x, SR, nperseg=1024, noverlap=1024 - HOP, boundary=None, padded=False)
M = np.log1p(100 * np.abs(Z))
flux = np.maximum(0, np.diff(M, axis=1))
onset = flux.sum(0)
onset = np.maximum(0, onset - np.convolve(onset, np.ones(16) / 16, "same"))
onset /= onset.std() + 1e-9
low = flux[f < 150].sum(0)
times = (np.arange(len(onset)) + 1) * HOP / SR + 512 / SR

# Tempo: autocorrelation of the onset envelope, weighted towards 120 BPM by an octave-wide prior.
ac = np.correlate(onset, onset, "full")[len(onset) - 1 :]
ac /= ac[0] + 1e-9
cands = np.arange(float(opts["--min"]), float(opts["--max"]) + 0.01, 0.05)
lags = 60 * FPS / cands
score = np.interp(lags, np.arange(len(ac)), ac) * np.exp(-0.5 * np.log2(cands / 120) ** 2)
period = 60 * FPS / cands[int(np.argmax(score))]


def track(period):
    """Beat tracking by dynamic programming (Ellis 2007): onsets that keep a steady period."""
    n = len(onset)
    best = onset.copy()
    back = np.full(n, -1)
    lo, hi = int(round(period / 2)), int(round(period * 2))
    for i in range(lo, n):
        prev = np.arange(max(0, i - hi), i - lo + 1)
        if not len(prev):
            continue
        cost = best[prev] - 100 * np.log((i - prev) / period) ** 2
        k = int(np.argmax(cost))
        best[i] = onset[i] + cost[k]
        back[i] = prev[k]
    i = n - int(period) + int(np.argmax(best[n - int(period) :]))
    frames = []
    while i >= 0:
        frames.append(i)
        i = back[i]
    return np.array(frames[::-1])


frames = track(period)
# Half-tempo trap: a backbeat (clap on 2 and 4) makes the two-beat period correlate best. If the
# points halfway between beats hit nearly as hard as the beats, the real tempo is double.
mids = ((frames[:-1] + frames[1:]) // 2).astype(int)
ratio = onset[mids].mean() / (onset[frames].mean() + 1e-9)
if ratio > 0.6 and 2 * 60 * FPS / period <= float(opts["--max"]):
    period /= 2
    frames = track(period)

# Refine each beat onto the first strong attack near it (1 ms energy envelope, ±35 ms).
# First, not strongest: a clap or a flam has several bursts, and the beat is the first.
env = np.sqrt(np.convolve(x**2, np.ones(44) / 44, "same"))
rise = np.diff(env, prepend=env[0])
beats = []
for fr in frames:
    c = int(times[fr] * SR)
    a, b = max(0, c - int(0.035 * SR)), min(len(rise), c + int(0.035 * SR))
    seg = rise[a:b]
    beats.append((a + int(np.argmax(seg >= 0.5 * seg.max()))) / SR if b > a and seg.max() > 0 else times[fr])
beats = np.array(beats)

# Fixed-grid fit: number the beats one interval at a time, then a line fit with outlier rejection.
step = period / FPS
k = np.concatenate([[0], np.cumsum(np.maximum(1, np.round(np.diff(beats) / step)))])
keep = np.ones(len(beats), bool)
for _ in range(3):
    slope, icpt = np.polyfit(k[keep], beats[keep], 1)
    resid = beats - (icpt + slope * k)
    keep = np.abs(resid) < 0.04
bpm = 60 / slope
fit_rms = float(np.sqrt(np.mean(resid[keep] ** 2)) * 1000)
first = icpt - np.floor(icpt / slope + 0.01) * slope
fixed = fit_rms < 15
if fixed:
    beats = np.arange(first, len(x) / SR, slope)
else:
    beats = beats[keep]

# Downbeats: the beat phase (of 4) with the most low-end attack plus the biggest level jumps.
# Four-on-the-floor kicks tie on the low end; sections (drops, entries) start on downbeats.
fr_of = np.clip(np.searchsorted(times, beats), 0, len(low) - 1)
lowb = np.array([low[max(0, fr - 2) : fr + 3].max() for fr in fr_of])
edges = np.clip((np.append(beats, beats[-1] + slope) * SR).astype(int), 0, len(x))
bdb = np.array([20 * np.log10(np.sqrt(np.mean(x[a:b] ** 2)) + 1e-9) if b > a else -120.0 for a, b in zip(edges[:-1], edges[1:])])
jump = np.maximum(0, np.diff(bdb, prepend=bdb[0]))
vote = [lowb[p::4].mean() / (lowb.mean() + 1e-9) + jump[p::4].mean() / (jump.mean() + 1e-9) for p in range(4)]
phase = int(np.argmax(vote))
downbeats = beats[phase::4]
bar = 4 * slope
down0 = downbeats[0] - np.floor(downbeats[0] / bar + 0.01) * bar if fixed else downbeats[0]

# Sections: bars where the level jumps by 3 dB or more.
bars = []
for t0 in np.arange(down0, len(x) / SR - bar, bar):
    seg = x[max(0, int(t0 * SR)) : int((t0 + bar) * SR)]
    bars.append({"t": round(float(t0), 3), "db": round(float(20 * np.log10(np.sqrt(np.mean(seg**2)) + 1e-9)), 1)})
jumps = sorted(((abs(bars[i]["db"] - bars[i - 1]["db"]), bars[i]["t"], bars[i]["db"] - bars[i - 1]["db"]) for i in range(1, len(bars))), reverse=True)
sections = sorted([(t, d) for m, t, d in jumps if m >= 3][:8])

print(f"{src}")
print(f"  tempo {bpm:.2f} BPM   beat {slope * 1000:.1f} ms   bar {bar:.3f} s   {len(x) / SR:.1f} s long")
grid = "fixed grid fits (produced music)" if fixed else "tempo drifts: snap.py will use the tracked beats"
print(f"  grid fit rms {fit_rms:.1f} ms over {int(keep.sum())}/{len(keep)} tracked beats: {grid}")
print(f"  first beat {first:.3f} s   first downbeat {down0:.3f} s (estimate, phase {phase} of 4)")
print("  downbeats: " + " ".join(f"{t:.2f}" for t in downbeats[:12]) + (" ..." if len(downbeats) > 12 else ""))
if sections:
    print("  section starts (level jump): " + "  ".join(f"{t:.2f} s ({d:+.1f} dB)" for t, d in sections))
print("  start the video on a downbeat or a section start: snap.py --from <seconds>")

if opts["--json"]:
    out = {
        "source": src,
        "bpm": round(float(bpm), 3),
        "firstBeat": round(float(first), 4),
        "firstDownbeat": round(float(down0), 4),
        "fitRmsMs": round(fit_rms, 1),
        "fixedGrid": bool(fixed),
        "beats": [round(float(t), 4) for t in beats],
        "downbeats": [round(float(t), 4) for t in downbeats],
        "bars": bars,
        "sections": [t for t, _ in sections],
    }
    Path(opts["--json"]).parent.mkdir(parents=True, exist_ok=True)
    Path(opts["--json"]).write_text(json.dumps(out, indent=1))
    print(f"  wrote {opts['--json']}")
