#!/usr/bin/env bash
# Loop seam check: PSNR of the last frame against the first, and the audio jump across the wrap.
#   bash seam.sh <video>
# Pass: PSNR >= 40 dB (grain and sub-pixel motion only); audio jump close to a typical sample step.
set -euo pipefail
video=$1
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
n=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$video")
ffmpeg -v error -y -i "$video" -vf "select=eq(n\,0)" -frames:v 1 "$tmp/first.png"
ffmpeg -v error -y -i "$video" -vf "select=eq(n\,$((n - 1)))" -frames:v 1 "$tmp/last.png"
psnr=$(ffmpeg -hide_banner -i "$tmp/first.png" -i "$tmp/last.png" -lavfi psnr -f null - 2>&1 | grep -o "average:[0-9.inf]*" | cut -d: -f2)
echo "frames $n  first-vs-last PSNR ${psnr} dB"
if ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$video" | grep -q .; then
	ffmpeg -v error -i "$video" -vn -ac 1 -ar 48000 -f f32le - | python3 -c "
import sys, numpy as np
x = np.frombuffer(sys.stdin.buffer.read(), np.float32)
w = 480
step = float(np.median(np.abs(np.diff(x))))
print(f'audio {len(x) / 48000:.3f}s  seam jump {abs(x[-1] - x[0]):.4f}  typical step {step:.4f}  rms end {np.sqrt(np.mean(x[-w:]**2)):.4f} start {np.sqrt(np.mean(x[:w]**2)):.4f}')
"
fi
