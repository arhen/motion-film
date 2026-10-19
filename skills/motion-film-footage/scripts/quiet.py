"""Speech and silence from the audio itself, so cuts do not depend on transcription timing (which can be coarse).

    from quiet import load, silences, loud_at
"""

import subprocess

import numpy as np

SR = 16000
HOP = 160  # 10 ms


def load(media):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(media), "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def envelope(x):
    n = len(x) // HOP
    frames = x[: n * HOP].reshape(n, HOP)
    return 20 * np.log10(np.sqrt(np.mean(frames**2, axis=1)) + 1e-9)


def threshold(db):
    """Silence sits 30 dB under the loud speech level, clamped between -70 and -35 dBFS."""
    speech = np.percentile(db, 90)
    return float(np.clip(speech - 30, -70, -35))


def silences(x, min_len=0.6):
    """[(start, end)] in seconds of every stretch quieter than the threshold for at least min_len."""
    db = envelope(x)
    quiet = db < threshold(db)
    out, start = [], None
    for i, q in enumerate(np.append(quiet, False)):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * HOP / SR >= min_len:
                out.append((start * HOP / SR, i * HOP / SR))
            start = None
    return out


def loud_at(x, t, window=0.04):
    """True if the audio around t (± window) is speech-loud, so a cut there would clip a sound."""
    db = envelope(x)
    th = threshold(db)
    a, b = max(0, int((t - window) * SR / HOP)), min(len(db), int((t + window) * SR / HOP) + 1)
    return bool(b > a and db[a:b].max() > th + 6)
