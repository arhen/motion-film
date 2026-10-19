#!/usr/bin/env bash
# Audio QA without listening: integrated loudness, loudness range, true peak, plus spectrogram and waveform PNGs.
#   bash audio-report.sh <mix.wav|video.mp4> [outdir] [more files to measure…]
set -euo pipefail
src=$1
out=${2:-.}
shift $(( $# > 1 ? 2 : 1 ))
mkdir -p "$out"
name=$(basename "${src%.*}")

measure() {
	ffmpeg -hide_banner -nostats -i "$1" -af ebur128=peak=true -f null - 2>&1 |
		awk '/Summary:/{s=1} s && /I:|LRA:|Peak:/{gsub(/^ +/,""); printf "%s  ", $0} END{print ""}'
}

printf "%-40s " "$(basename "$src")"
measure "$src"
for f in "$@"; do
	printf "%-40s " "$(basename "$f")"
	measure "$f"
done
ffmpeg -v error -y -i "$src" -lavfi "showspectrumpic=s=1800x500:legend=1:scale=log:fscale=log:color=intensity" "$out/$name-spectrum.png"
ffmpeg -v error -y -i "$src" -lavfi "showwavespic=s=1800x240:colors=#888888" "$out/$name-wave.png"
echo "wrote $out/$name-spectrum.png $out/$name-wave.png"
