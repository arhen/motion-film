"""Word-sync table: expected word onsets (clock placement + TTS timestamps) vs speech-to-text of the final mix.

    node ../motion-film-voice/scripts/stt.mjs out/film.mp4 --json out/qa/stt.json
    python3 sync.py clock.json vo/film out/qa/stt.json out/film.mp4 > out/qa/sync.md

Δ = heard - expected. A median |Δ| at or below 0.15 s is in sync.
"""

import json
import re
import sys
from pathlib import Path

clock_path, vo_dir, stt_path, media = sys.argv[1:5]
clock = json.loads(Path(clock_path).read_text())
beat = 60 / clock["bpm"] if "bpm" in clock else None
offset = clock.get("beatOffset", 0.0)


def start(entry, words):
    anchor = offset + entry["beat"] * beat if "beat" in entry else entry.get("at", 0)
    return anchor - words[entry["alignWord"]]["start"] if "alignWord" in entry else anchor


expected = []
for entry in clock["vo"]:
    words = json.loads((Path(vo_dir) / f"{entry['id']}.json").read_text())["words"]
    s = start(entry, words)
    expected += [(w["w"], s + w["start"]) for w in words]


def norm(s):
    return re.sub(r"[^\w]", "", s.lower())


stt = json.loads(Path(stt_path).read_text())[media]
heard = stt["words"]
lines = [f"# Word sync: `{media}`", "", f"Transcript: {stt['text'].strip()}", "", "| Word | Expected (s) | Heard (s) | Δ (s) |", "| --- | --- | --- | --- |"]
j, deltas = 0, []
for w, t0 in expected:
    match = next((k for k in range(j, min(j + 4, len(heard))) if norm(heard[k]["w"])[:4] == norm(w)[:4]), None)
    if match is None:
        lines.append(f"| {w} | {t0:.2f} | missing | |")
        continue
    h = heard[match]["start"]
    deltas.append(h - t0)
    lines.append(f"| {w} | {t0:.2f} | {h:.2f} | {h - t0:+.2f} |")
    j = match + 1
mags = sorted(abs(d) for d in deltas) or [float("nan")]
lines += ["", f"{len(deltas)}/{len(expected)} words heard; median |Δ| {mags[len(mags) // 2]:.2f} s, max |Δ| {mags[-1]:.2f} s."]
print("\n".join(lines))
