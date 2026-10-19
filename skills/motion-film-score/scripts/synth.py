"""Synthesis toolkit for video scores: deterministic numpy/scipy instruments, SFX, reverb, VO helpers and loudness.

No samples and no licences: every sound is generated from seeded maths, so a mix is reproducible bit for bit.
Import it from a mixer next to it: sys.path.insert(0, <this dir>); from synth import *
"""

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal

SR = 48000

# Pre-master scratch for every mixer (keep it out of git).
CACHE = Path(__file__).resolve().parent / ".cache"
CACHE.mkdir(exist_ok=True)
rng = np.random.default_rng(548)

def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def tt(n):
    return np.arange(n) / SR


def place(bus, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if sig.ndim == 1:
        a = (pan + 1) * np.pi / 4
        sig = np.stack([sig * np.cos(a), sig * np.sin(a)], 1) * np.sqrt(2)
    if i < 0:
        sig, i = sig[-i:], 0
    if i >= len(bus):
        return
    end = min(i + len(sig), len(bus))
    bus[i:end] += sig[: end - i] * gain


def sos(kind, fc, order=2, q=None):
    if kind == "bp":
        return signal.butter(order, [fc[0], fc[1]], "bandpass", fs=SR, output="sos")
    return signal.butter(order, np.clip(fc, 20, SR / 2 - 100), kind, fs=SR, output="sos")


def filt(x, kind, fc, order=2):
    return signal.sosfilt(sos(kind, fc, order), x, axis=0)


def biquad_lp(fc, q):
    w = 2 * np.pi * np.clip(fc, 20, SR * 0.45) / SR
    al = np.sin(w) / (2 * q)
    cw = np.cos(w)
    b = np.array([(1 - cw) / 2, 1 - cw, (1 - cw) / 2])
    a = np.array([1 + al, -2 * cw, 1 - al])
    return np.concatenate([b / a[0], a / a[0]])[None, :]


def lp_sweep(x, fc, q=0.9, block=64):
    """Resonant lowpass with per-block cutoff; fc is an array the length of x."""
    mono = x.ndim == 1
    xs = x[:, None] if mono else x
    out = np.zeros_like(xs)
    zi = np.zeros((1, 2, xs.shape[1]))
    for s in range(0, len(xs), block):
        so = biquad_lp(fc[min(s, len(fc) - 1)], q)
        out[s : s + block], zi = signal.sosfilt(so, xs[s : s + block], axis=0, zi=zi)
    return out[:, 0] if mono else out


def polyblep(t, dt):
    y = np.zeros_like(t)
    m = t < dt
    u = t[m] / dt[m]
    y[m] = u + u - u * u - 1
    m2 = t > 1 - dt
    u = (t[m2] - 1) / dt[m2]
    y[m2] = u * u + u + u + 1
    return y


def saw(freq, n, phase0=0.0):
    f = np.broadcast_to(np.asarray(freq, float), (n,))
    dt = f / SR
    ph = (phase0 + np.cumsum(dt)) % 1.0
    return 2 * ph - 1 - polyblep(ph, dt)


def exp_env(n, tau, attack=0.002):
    t = tt(n)
    a = np.clip(t / attack, 0, 1) if attack > 0 else 1
    return a * np.exp(-t / tau)


def adsr(n, a, d, s, r, hold):
    t = tt(n)
    env = np.where(t < a, t / max(a, 1e-4), s + (1 - s) * np.exp(-(t - a) / max(d, 1e-4)))
    rel = t > hold
    env[rel] = env[rel] * np.exp(-(t[rel] - hold) / max(r, 1e-4))
    return env


def noise(n, seed=None):
    g = np.random.default_rng(seed) if seed is not None else rng
    return g.standard_normal(n)


def make_ir(rt60=2.2, pre=0.022, damp=0.35, seed=1):
    n = int(SR * rt60 * 1.2)
    t = tt(n)
    g = np.random.default_rng(seed)
    ir = g.standard_normal((n, 2)) * np.exp(-6.9 * t / rt60)[:, None]
    dark = filt(ir, "lowpass", 2500)
    mix = np.clip(t / (rt60 * damp), 0, 1)[:, None]
    ir = ir * (1 - mix) + dark * mix
    ir[: int(pre * SR)] = 0
    for k, (d, gn) in enumerate([(0.011, 0.5), (0.019, 0.35), (0.027, 0.3), (0.041, 0.22)]):
        ir[int(d * SR), k % 2] += gn
    return ir / np.sqrt(np.sum(ir**2) / 2)


def reverb(x, ir, wet):
    y = np.stack([signal.fftconvolve(x[:, c], ir[:, c])[: len(x)] for c in range(2)], 1)
    return y * wet


def pingpong(x, delay, fb=0.45, taps=6, damp=3500):
    out = np.zeros_like(x)
    cur = x.copy()
    d = int(delay * SR)
    for k in range(1, taps + 1):
        cur = filt(cur, "lowpass", damp, 1)
        mono = cur.mean(1)
        side = np.stack([mono, mono * 0.25], 1) if k % 2 else np.stack([mono * 0.25, mono], 1)
        out[k * d :] += side[: len(x) - k * d] * fb**k
    return out


# ---------------------------------------------------------------- instruments


def kick(f0=165, f1=47, length=0.42, tone=0.28):
    n = int(length * SR)
    t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t / 0.032)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / tone)
    click = filt(noise(n, 3) * np.exp(-t / 0.0025), "highpass", 2200) * 0.35
    return np.tanh(1.8 * (body + click)) * 0.9


def clap(seed=5):
    n = int(0.45 * SR)
    t = tt(n)
    nz = noise(n, seed)
    env = np.zeros(n)
    for k, off in enumerate([0, 0.009, 0.018, 0.026]):
        i = int(off * SR)
        tau = 0.006 if k < 3 else 0.13
        env[i:] += np.exp(-(t[: n - i]) / tau) * (0.8 if k < 3 else 1)
    x = filt(nz * env, "bp", (900, 5200), 2)
    return np.tanh(x * 1.6) * 0.7


def snare(seed=9, pitch=190):
    n = int(0.3 * SR)
    t = tt(n)
    body = np.sin(2 * np.pi * pitch * t) * np.exp(-t / 0.05)
    nz = filt(noise(n, seed), "bp", (1400, 9000)) * np.exp(-t / 0.11)
    return (body * 0.5 + nz) * 0.6


METAL = [205.3, 304.4, 369.6, 522.7, 540.0, 800.0]


def hat(open_=False, seed=11):
    n = int((0.5 if open_ else 0.09) * SR)
    t = tt(n)
    sq = sum(np.sign(np.sin(2 * np.pi * f * 1.9 * t + k)) for k, f in enumerate(METAL))
    x = filt(sq * 0.6 + noise(n, seed) * 0.8, "bp", (7000, 15000), 2)
    return x * np.exp(-t / (0.16 if open_ else 0.022)) * 0.45


def crash(length=2.4, seed=13):
    n = int(length * SR)
    t = tt(n)
    g = np.random.default_rng(seed)
    sq = sum(np.sign(np.sin(2 * np.pi * f * 3.1 * t + k)) for k, f in enumerate(METAL))
    out = []
    for c in range(2):
        x = filt(sq * 0.3 + g.standard_normal(n), "highpass", 4200, 2)
        out.append(x * np.exp(-t / 0.75) * (0.4 + 0.6 * np.exp(-t / 0.05)))
    return np.stack(out, 1) * 0.35


def supersaw(notes, dur, attack=0.01, decay=0.4, sustain=0.7, release=0.3, detune=0.16, voices=7, seed=21):
    hold = dur
    n = int((dur + release * 4) * SR)
    env = adsr(n, attack, decay, sustain, release, hold)
    g = np.random.default_rng(seed)
    out = np.zeros((n, 2))
    for m in notes:
        for v in range(voices):
            spread = (v / (voices - 1) - 0.5) * 2
            f = midi(m + spread * detune)
            x = saw(f, n, g.random())
            p = spread * 0.85
            a = (p + 1) * np.pi / 4
            out[:, 0] += x * np.cos(a)
            out[:, 1] += x * np.sin(a)
    out *= env[:, None] / (len(notes) * voices) * 2.2
    return out


def pluck(m, dur=0.35, bright=4200, seed=31):
    n = int((dur + 0.4) * SR)
    t = tt(n)
    x = saw(midi(m), n, 0.1) * 0.7 + saw(midi(m) * 1.003, n, 0.5) * 0.5
    fc = 300 + bright * np.exp(-t / 0.07)
    x = lp_sweep(x, fc, q=1.4)
    return x * exp_env(n, 0.16, 0.001) * 0.8


def bell(m, dur=1.2, ratio=2.0, index=2.6, idecay=0.09, tau=0.45):
    n = int(dur * SR)
    t = tt(n)
    fc = midi(m)
    mod = index * np.exp(-t / idecay) * np.sin(2 * np.pi * fc * ratio * t)
    x = np.sin(2 * np.pi * fc * t + mod) + 0.25 * np.sin(4 * np.pi * fc * t) * np.exp(-t / 0.12)
    return x * exp_env(n, tau, 0.0015) * 0.5


def bass_note(m, dur, cutoff=420):
    n = int((dur + 0.05) * SR)
    t = tt(n)
    sub = np.sin(2 * np.pi * midi(m - 12) * t)
    top = filt(saw(midi(m), n), "lowpass", cutoff, 2)
    env = np.clip(t / 0.004, 0, 1) * np.clip((dur + 0.04 - t) / 0.03, 0, 1)
    return np.tanh((sub * 0.9 + top * 0.55) * 1.4) * env * 0.6


def pop(m, length=0.16):
    n = int(length * SR)
    t = tt(n)
    f = midi(m) * (1 + 0.6 * np.exp(-t / 0.012))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    return x * exp_env(n, 0.045, 0.001) * 0.6


def blip(m, length=0.25):
    return pop(m, length) * 0.5 + bell(m + 12, length, ratio=3.5, index=1.2, idecay=0.03, tau=0.06)[: int(length * SR)] * 0.6


def riser(length, f_from=380, f_to=9000, seed=41):
    n = int(length * SR)
    t = tt(n)
    k = t / length
    fc = f_from * (f_to / f_from) ** (k**1.6)
    nz = noise(n, seed)
    x = lp_sweep(filt(nz, "highpass", 200), fc, q=3.0)
    tone = saw(midi(57) * 2 ** (k**1.5 * 1.5), n) * 0.08
    tone = lp_sweep(tone, fc * 0.6 + 300, q=1.5)
    amp = k**2.2
    y = (x * 0.45 + tone) * amp
    return np.stack([y * (1 - 0.3 * k), y * (0.7 + 0.3 * k)], 1)


def whoosh(length=0.45, peak=0.6, lo=250, hi=4200, pan_from=-0.7, pan_to=0.7, seed=51):
    n = int(length * SR)
    t = tt(n)
    k = t / length
    bell_ = np.exp(-((k - peak) ** 2) / (2 * 0.16**2))
    fc = lo + (hi - lo) * bell_
    x = lp_sweep(filt(noise(n, seed), "highpass", 150), fc, q=2.2) * bell_
    p = pan_from + (pan_to - pan_from) * k
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1) * 1.1


def impact(seed=61):
    n = int(2.2 * SR)
    t = tt(n)
    f = 32 + 40 * np.exp(-t / 0.18)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.7)
    crunch = filt(noise(n, seed), "lowpass", 900) * np.exp(-t / 0.12) * 0.6
    x = np.tanh((boom + crunch) * 1.5)
    return np.stack([x, x], 1) * 0.8


def click():
    n = int(0.12 * SR)
    t = tt(n)
    x = np.zeros(n)
    for off, g in [(0, 1.0), (0.055, 0.6)]:
        i = int(off * SR)
        m = n - i
        x[i:] += (filt(noise(m, 71), "highpass", 2500) * np.exp(-t[:m] / 0.0018) + np.sin(2 * np.pi * 3800 * t[:m]) * np.exp(-t[:m] / 0.003)) * g
    return x * 0.5


def stamp():
    n = int(0.25 * SR)
    t = tt(n)
    f = 70 + 90 * np.exp(-t / 0.02)
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07)
    slap = filt(noise(n, 81), "lowpass", 2200) * np.exp(-t / 0.018)
    return np.tanh((thump + slap * 0.7) * 1.3) * 0.55


def swish(seed=91, length=0.24):
    return whoosh(length, 0.55, 600, 5200, -0.3, 0.3, seed) * 0.55


def sonar(m=84):
    a = bell(m, 2.4, ratio=1.0, index=0.6, idecay=0.2, tau=0.9)
    b = bell(m + 7, 2.4, ratio=2.0, index=0.4, idecay=0.1, tau=0.5) * 0.35
    return a + b


def load_mp3(path):
    """A VO take as mono float at SR. Missing take, or NO_VO=1: silence, so a fresh clone mixes music + SFX only."""
    if os.environ.get("NO_VO") == "1":
        return np.zeros(1)
    if not Path(path).exists():
        print(f"  no VO take {path} (silence; run scripts/vo.mjs to generate it)", file=sys.stderr)
        return np.zeros(1)
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        check=True,
        capture_output=True,
    ).stdout
    return np.frombuffer(raw, np.float32).astype(float)


def compress(x, thr_db=-22, ratio=3.0, att=0.004, rel=0.12):
    env = np.abs(x)
    a_att, a_rel = np.exp(-1 / (att * SR)), np.exp(-1 / (rel * SR))
    env_s = signal.lfilter([1 - a_rel], [1, -a_rel], env)
    env_s = np.maximum(env_s, signal.lfilter([1 - a_att], [1, -a_att], env))
    lvl = 20 * np.log10(env_s + 1e-9)
    over = np.maximum(lvl - thr_db, 0)
    gain = 10 ** (-over * (1 - 1 / ratio) / 20)
    return x * gain


def loudnorm(src, dst, target="I=-16:TP=-1.5:LRA=11", sr=SR):
    """Two-pass linear EBU R128 normalisation with ffmpeg."""
    import json

    probe = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(src), "-af", f"loudnorm={target}:print_format=json", "-f", "null", "-"],
        check=True,
        capture_output=True,
        text=True,
    ).stderr
    m = json.loads(probe[probe.rindex("{") : probe.rindex("}") + 1])
    measured = ":".join(
        f"{k}={m[v]}"
        for k, v in [("measured_I", "input_i"), ("measured_TP", "input_tp"), ("measured_LRA", "input_lra"), ("measured_thresh", "input_thresh"), ("offset", "target_offset")]
    )
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(src), "-af", f"loudnorm={target}:{measured}:linear=true", "-ar", str(sr), "-c:a", "pcm_s24le", str(dst)],
        check=True,
    )
    return m["input_i"]
