#!/usr/bin/env bash
# Delivery probe: codecs, size, duration, fps, integrated loudness and true peak for each file.
#   bash probe.sh out/film.mp4 out/film-1080.webm …
set -euo pipefail
for f in "$@"; do
	echo "$f"
	v=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate -of csv=p=0 "$f")
	a=$(ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,bit_rate -of csv=p=0 "$f")
	d=$(ffprobe -v error -show_entries format=duration,size -of csv=p=0 "$f")
	echo "  video ${v:-none}  audio ${a:-none}" | tr ',' ' '
	echo "$d" | awk -F, '{printf "  duration %.3f s  size %.1f MB\n", $1, $2 / 1048576}'
	c=$(ffprobe -v error -select_streams v:0 -show_entries stream=color_space,color_primaries,color_transfer,color_range -of default=nw=1 "$f" | tr '\n' ' ')
	case "$c" in
	*color_space=bt709*color_transfer=bt709*color_primaries=bt709*) echo "  colour $c" ;;
	*) echo "  colour ${c:-untagged} << not fully BT.709: encode with encode-web.sh, or players may shift the colours" ;;
	esac
	if ffprobe -v error -select_streams a:0 -show_entries stream=codec_name -of csv=p=0 "$f" | grep -q .; then
		printf "  "
		ffmpeg -hide_banner -nostats -i "$f" -af ebur128=peak=true -f null - 2>&1 |
			awk '/Summary:/{s=1} s && /I:|Peak:/{gsub(/^ +/,""); printf "%s  ", $0} END{print ""}'
	fi
done
