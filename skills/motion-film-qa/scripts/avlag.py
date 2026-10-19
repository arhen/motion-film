"""Audio offset of the final file against the mix it was made from, plus stream lengths.

    python3 avlag.py out/film.mp4 audio/film.wav

Encoders and muxers can shift audio by a few tens of milliseconds (codec priming), which moves every sound
hit off its frame. This cross-correlates the decoded file audio with the source mix at three points and
reports the lag (positive: the file's audio is late). Also compares the audio and video stream lengths.
Exits 1 if the lag is more than half a frame or the lengths differ by more than a frame.
"""

import json
import subprocess
import sys

import numpy as np

SR = 48000
if len(sys.argv) < 3:
    sys.exit(__doc__)
media, mix = sys.argv[1], sys.argv[2]


def pcm(path):
    # first_pts=0 pads to the container timeline, so a delayed audio stream shows up as lag instead of vanishing.
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vn", "-af", "aresample=async=1:first_pts=0", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    return np.diff(x, prepend=x[:1])


a, b = pcm(media), pcm(mix)
probe = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,duration,r_frame_rate", "-of", "json", media], check=True, capture_output=True).stdout)["streams"]
video = next(s for s in probe if s["codec_type"] == "video")
num, den = (int(v) for v in video["r_frame_rate"].split("/"))
frame_ms = 1000 * den / num
win, reach = SR * 2, int(SR * 0.1)
lags = []
for frac in (0.25, 0.5, 0.75):
    c = int(len(b) * frac)
    if c + win + reach > len(a) or c - reach < 0:
        continue
    ref = b[c : c + win]
    seg = a[c - reach : c + win + reach]
    n = 1 << int(np.ceil(np.log2(len(seg) + len(ref))))
    corr = np.fft.irfft(np.fft.rfft(seg, n) * np.conj(np.fft.rfft(ref, n)), n)[: len(seg) - len(ref) + 1]
    lags.append((int(np.argmax(corr)) - reach) / SR * 1000)
lens = {s["codec_type"]: float(s.get("duration", 0)) for s in probe}
lag = float(np.median(lags)) if lags else float("nan")
print(f"audio lag {lag:+.1f} ms (at 25/50/75 %: {', '.join(f'{v:+.1f}' for v in lags)}), one frame = {frame_ms:.1f} ms")
print(f"stream lengths: video {lens.get('video', 0):.3f} s, audio {lens.get('audio', 0):.3f} s, source mix {len(b) / SR:.3f} s")
bad = abs(lag) > frame_ms / 2 or abs(lens.get("video", 0) - lens.get("audio", 0)) > frame_ms / 1000
print("off: re-mux the mix onto the video with ffmpeg (-c:v copy) and check again" if bad else "in sync")
sys.exit(1 if bad else 0)
