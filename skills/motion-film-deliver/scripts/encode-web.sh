#!/usr/bin/env bash
# Web encodes for a page: h264 mp4 (+faststart) and VP9 webm at <width>, poster at <poster width>.
# Height follows the master's aspect ratio (16:9, 9:16, 1:1, 4:5 all work).
#   bash encode-web.sh <master.mp4> <poster.jpg> <out dir> <name> [width=1600] [poster width=1280]
#   vertical: bash encode-web.sh out/<id>-9x16.mp4 out/<id>-9x16-poster.jpg <dir> <id>-9x16 720 720
set -euo pipefail
src=$1
poster=$2
dst=$3
name=$4
w=${5:-1600}
pw=${6:-1280}
COLOR="-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv"
TAG="setparams=colorspace=bt709:color_primaries=bt709:color_trc=bt709:range=tv"
mkdir -p "$dst"
ffmpeg -v error -y -i "$src" -vf "scale=$w:-2:flags=lanczos,$TAG" -c:v libx264 -preset slow -crf 26 -profile:v high -pix_fmt yuv420p $COLOR -movflags +faststart -c:a aac -b:a 96k "$dst/$name.mp4"
ffmpeg -v error -y -i "$src" -vf "scale=$w:-2:flags=lanczos,$TAG" -c:v libvpx-vp9 -b:v 0 -crf 36 -row-mt 1 -deadline good -cpu-used 2 -pix_fmt yuv420p $COLOR -c:a libopus -b:a 96k "$dst/$name.webm"
ffmpeg -v error -y -i "$poster" -vf "scale=$pw:-2:flags=lanczos" -q:v 3 "$dst/$name-poster.jpg"
ls -la "$dst/$name.mp4" "$dst/$name.webm" "$dst/$name-poster.jpg"
