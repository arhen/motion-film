#!/usr/bin/env bash
# Frames from the rendered file (not from stills) at percentages or seconds, plus a labelled sheet.
#   bash frames.sh <video> <outdir> 0% 25% 50% 75% 100% 12.4 12.5 12.6
# Writes <outdir>/<name>-f<frame>.jpg and <outdir>/<name>-sheet.jpg (needs grid.py next to this script).
set -euo pipefail
video=$1
out=$2
shift 2
here=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$out"
name=$(basename "${video%.*}")
fps=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of csv=p=0 "$video" | awk -F/ '{printf "%.6f", $1/($2?$2:1)}')
frames=$(ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$video")
files=()
for spec in "$@"; do
	if [[ $spec == *% ]]; then
		n=$(python3 -c "print(round(($frames - 1) * ${spec%\%} / 100))")
	else
		n=$(python3 -c "print(min($frames - 1, round($spec * $fps)))")
	fi
	file=$(printf "%s/%s-f%04d.jpg" "$out" "$name" "$n")
	ffmpeg -v error -y -i "$video" -vf "select=eq(n\,$n)" -frames:v 1 -q:v 3 "$file"
	files+=("$file")
done
python3 "$here/grid.py" "$out/$name-sheet.jpg" --cols 4 --w 640 --fps "$fps" "${files[@]}"
