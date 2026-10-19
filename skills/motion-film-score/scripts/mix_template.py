"""Template mixer: a bed, SFX on the clock's cues, voice-over, ducking, optional loop wrap, two-pass loudness.

    python3 mix_template.py clock.json vo/film out/film.wav [--loop] [--lufs -16] [--tp -1.5]

Copy this file per video. Edit CHORDS, bed() and CUE_SOUNDS for its motion language; keep the rest.
Voice placement follows the clock rules used by slotfit.py and sync.py. Missing takes mix as silence.
With "music" in the clock (written by snap.py), the supplied track replaces the synthesized bed.
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from synth import *  # noqa: E402,F403
from synth import CACHE, SR  # noqa: E402

args = sys.argv[1:]
flags = {"--loop": False, "--lufs": "-16", "--tp": "-1.5"}
for f in list(flags):
    if f in args:
        i = args.index(f)
        if f == "--loop":
            flags[f] = True
            del args[i]
        else:
            flags[f] = args[i + 1]
            del args[i : i + 2]
clock = json.loads(Path(args[0]).read_text())
vo_dir = Path(args[1])
out = Path(args[2])

LEN = clock["seconds"]
N = int(SR * LEN)
TAIL = SR * 4
BPM = clock.get("bpm", 96)
BEAT = 60 / BPM
OFFSET = clock.get("beatOffset", 0.0)
CUES = clock.get("cues", {})
MUSIC = clock.get("music")

# IV, V, iii, vi in C: (bass root, chord voicing) as MIDI notes.
CHORDS = [(41, [57, 60, 64, 67]), (43, [59, 62, 64, 67]), (40, [55, 59, 62, 66]), (45, [55, 60, 64, 71])]


def bus():
    return np.zeros((N + TAIL, 2))


def cue_times(name, mode="each"):
    """Times for a cue: 'each' = every value, 'start' = first value only, 'end' = last value."""
    v = CUES.get(name)
    if v is None:
        return []
    vals = v if isinstance(v, list) else [v]
    return {"each": vals, "start": vals[:1], "end": vals[-1:]}[mode]


def bed():
    pads, plucks, low = bus(), bus(), bus()
    bars_per_chord = 2
    t, k = 0.0, 0
    while t < LEN + 2:
        root, notes = CHORDS[k % len(CHORDS)]
        dur = BEAT * 4 * bars_per_chord
        place(pads, supersaw(notes, dur * 0.98, attack=0.6, decay=1.5, sustain=0.8, release=0.9, detune=0.12, seed=k), t, 0.5)
        n = int(dur * SR)
        x = tt(n)
        sub = np.sin(2 * np.pi * midi(root - 12) * x) * np.clip(x / 0.4, 0, 1) * np.clip((dur - x) / 0.4, 0, 1)
        place(low, sub, t, 0.2)
        for s, i in enumerate([0, 2, 1, 3, 2, 1, 0, 2] * bars_per_chord):
            place(plucks, pluck(notes[i] + 12, bright=1400), t + s * BEAT / 2, 0.08, pan=0.3 * np.sin(s))
        t += dur
        k += 1
    pads = filt(pads, "lowpass", 1700, 2)
    plucks = plucks + pingpong(plucks, BEAT * 0.75, 0.4, 4)
    return pads * 0.7 + plucks + low + reverb(pads * 0.5 + plucks * 0.8, make_ir(2.4, 0.03, 0.3, 4), 0.35)


def track():
    """The supplied track from music.from, level-matched to the synthesized bed (RMS about -18 dBFS)."""
    path = Path(args[0]).resolve().parent / MUSIC["file"]
    start = MUSIC.get("from", 0)
    xf = min(BEAT * 4, LEN / 4)
    pre = int(min(start, xf) * SR)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", str(start - pre / SR), "-i", str(path), "-t", str(pre / SR + LEN + TAIL / SR), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        check=True,
        capture_output=True,
    ).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)
    lead, x = x[:pre], x[pre:]
    if len(x) < N:
        print(f"  track ends {(N - len(x)) / SR:.2f} s before the video does", file=sys.stderr)
    b = bus()
    b[: len(x)] = x[: len(b)]
    gain = 0.126 / (np.sqrt(np.mean(b[:N] ** 2)) + 1e-9) * 10 ** (MUSIC.get("gainDb", 0) / 20)
    b *= gain
    lead = lead * gain
    if flags["--loop"]:
        # Equal-power cross-fade over the last bar. Preferred: into the music just before `from`, so the
        # seam plays the track's own lead-in to the opening. Without enough lead-in: blend the bar after
        # the seam into the opening instead.
        n = int(xf * SR)
        k = np.linspace(0, np.pi / 2, n)[:, None]
        if len(lead) >= n:
            b[N - n : N] = b[N - n : N] * np.cos(k) + lead[-n:] * np.sin(k)
        else:
            n = min(n, TAIL)
            b[:n] = b[:n] * np.sin(k[:n]) + b[N : N + n] * np.cos(k[:n])
    else:
        fade = int(min(BEAT * 4, 2.0) * SR)
        b[N - fade : N] *= np.linspace(1, 0, fade)[:, None]
    b[N:] = 0
    return b


def chime(m):
    return bell(m, 1.4, ratio=2.0, index=1.6, idecay=0.05, tau=0.4)


# cue name -> (mode, factory(index) -> signal, gain[, lead]). Pitch notes to the key; edit per motion language.
# lead = seconds the sound starts before its cue, so a swell (whoosh, riser) peaks on the cue: length × peak.
CUE_SOUNDS = {
    "elementsIn": ("each", lambda k: pop([79, 83, 86, 88, 91][k % 5]), 0.12),
    "turn": ("start", lambda k: whoosh(0.5, 0.7, 250, 3500, -0.3, 0.3, 300), 0.25, 0.35),
    "insight": ("start", lambda k: chime(81), 0.2),
    "action": ("start", lambda k: click(), 0.35),
    "result": ("start", lambda k: chime(88), 0.14),
    "signoff": ("start", lambda k: bell(84, 1.8, ratio=1.0, index=0.7, idecay=0.12, tau=0.7), 0.16),
}


def sfx():
    b = bus()
    for name, (mode, make, gain, *lead) in CUE_SOUNDS.items():
        for k, t in enumerate(cue_times(name, mode)):
            place(b, make(k), max(0.0, t - (lead[0] if lead else 0.0)), gain)
    return b + reverb(b, make_ir(1.0, 0.012, 0.5, 5), 0.18)


def vo_start(entry, words):
    if "alignWord" in entry:
        anchor = OFFSET + entry["beat"] * BEAT if "beat" in entry else entry["at"]
        return anchor - words[entry["alignWord"]]["start"]
    return OFFSET + entry["beat"] * BEAT if "beat" in entry else entry["at"]


def voice():
    v = np.zeros(N + TAIL)
    for entry in clock.get("vo", []):
        timing = vo_dir / f"{entry['id']}.json"
        if not timing.exists():
            continue
        words = json.loads(timing.read_text())["words"]
        x = load_mp3(vo_dir / f"{entry['id']}.mp3")
        s = max(0, int(vo_start(entry, words) * SR))
        v[s : s + len(x)] += x[: len(v) - s]
    if not np.any(v):
        return v
    v = filt(v, "highpass", 90, 2)
    v = v + 0.2 * filt(v, "highpass", 3200, 1)
    v = compress(v)
    return v / (np.max(np.abs(v)) + 1e-9) * 0.8


def duck(v):
    w = int(0.03 * SR)
    env = np.convolve(np.abs(v), np.ones(w) / w, "same")
    act = (env > 0.012).astype(float)
    a_att, a_rel = np.exp(-1 / (0.05 * SR)), np.exp(-1 / (0.38 * SR))
    d = np.maximum(signal.lfilter([1 - a_att], [1, -a_att], act), signal.lfilter([1 - a_rel], [1, -a_rel], act))
    return np.clip(d, 0, 1)


v = voice()
d = duck(v)
st = np.stack([v, v], 1)
st = st + reverb(st, make_ir(0.8, 0.01, 0.5, 6), 0.05)
fx = sfx()
music = track() if MUSIC else bed()
mix = music * 0.55 * (1 - 0.55 * d)[:, None] + fx * 0.85 * (1 - 0.3 * d)[:, None] + st
stem = CACHE / f"{out.stem}-sfx.wav"
wavfile.write(stem, SR, (fx[:N] / (np.max(np.abs(fx)) + 1e-9) * 0.9).astype(np.float32))
print(f"sfx stem (for onsets.py): {stem}")
master = mix[:N].copy()
if flags["--loop"]:
    master[: len(mix) - N] += mix[N:]
else:
    fade = int(0.4 * SR)
    master[-fade:] *= np.linspace(1, 0, fade)[:, None]
master = np.tanh(master / (np.max(np.abs(master)) + 1e-9) * 1.2) / np.tanh(1.2)
pre = CACHE / f"{out.stem}-pre.wav"
wavfile.write(pre, SR, (master * 0.95).astype(np.float32))
out.parent.mkdir(parents=True, exist_ok=True)
measured = loudnorm(pre, out, f"I={flags['--lufs']}:TP={flags['--tp']}:LRA=11")
print(f"{out}  input {measured} LUFS -> {flags['--lufs']} LUFS, TP {flags['--tp']} dB")
