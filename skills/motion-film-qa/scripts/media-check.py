#!/usr/bin/env python3
"""Check an ffmpeg-skill probe against the approved clock and delivery dimensions."""

import argparse
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


def positive(value, name):
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive finite number")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError(f"{name} must be a positive finite number")
    return number


def dimension(value, name):
    number = positive(value, name)
    if not number.is_integer() or int(number) % 2:
        raise ValueError(f"{name} must be a positive even integer")
    return int(number)


def verify(clock, probe, width=None, height=None):
    fps = positive(clock["fps"], "clock.fps")
    seconds = positive(clock["seconds"], "clock.seconds")
    frames = math.floor(seconds * fps + 0.5)
    if frames < 1:
        raise ValueError("clock must contain at least one frame")
    if (width is None) != (height is None):
        raise ValueError("--width and --height must be supplied together")
    width = dimension(clock["width"] if width is None else width, "width")
    height = dimension(clock["height"] if height is None else height, "height")
    expected = {"fps": fps, "seconds": frames / fps, "frames": frames,
                "width": width, "height": height}
    errors, notes = [], []
    if probe.get("dry_run") or probe.get("status") == "failed":
        raise ValueError("a real successful probe is required")
    video = probe.get("video")
    if not isinstance(video, dict):
        raise ValueError("probe has no video stream")
    if positive(probe["size_bytes"], "probe.size_bytes") < 1:
        raise ValueError("probe describes an empty file")
    if video.get("width") != width or video.get("height") != height:
        errors.append(f"dimensions must be {width}x{height}")
    rate = video.get("avg_frame_rate") or video.get("r_frame_rate") or video.get("fps")
    actual_fps = float(Fraction(str(rate)))
    positive(actual_fps, "video.fps")
    if abs(actual_fps - fps) > 0.001:
        errors.append(f"fps {actual_fps:g} does not match clock {fps:g}")
    if video.get("variable_frame_rate_suspected"):
        errors.append("output is suspected variable frame rate")
    duration = positive(video.get("duration") or probe.get("duration"), "video.duration")
    if abs(duration - expected["seconds"]) > 1 / fps + 0.000001:
        errors.append(f"duration {duration:g}s does not match clock {expected['seconds']:g}s")
    count = video.get("nb_frames")
    if count is not None:
        if positive(count, "video.nb_frames") != frames:
            errors.append(f"frame count {count} does not match clock {frames}")
    else:
        notes.append("container reports no frame count; duration checked, exact count not verified")
    start = video.get("start_time")
    if start is not None:
        start = float(start)
        if not math.isfinite(start) or abs(start) > 0.5 / fps + 0.000001:
            errors.append(f"video starts at {start:g}s, not frame zero")
    else:
        notes.append("video start offset not reported; verify with A/V QA")
    if video.get("rotation", 0) not in (0, None):
        errors.append("unexpected rotation metadata")
    return {"ok": not errors, "expected": expected,
            "actual": {"fps": actual_fps, "seconds": duration, "frames": count,
                       "width": video.get("width"), "height": video.get("height")},
            "frame_count_verified": count is not None and count == frames,
            "errors": errors, "notes": notes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clock", type=Path)
    parser.add_argument("probe", type=Path)
    parser.add_argument("--width", type=int)
    parser.add_argument("--height", type=int)
    args = parser.parse_args()
    try:
        result = verify(json.loads(args.clock.read_text()),
                        json.loads(args.probe.read_text()), args.width, args.height)
    except (OSError, ValueError, KeyError, TypeError, AttributeError, ZeroDivisionError, OverflowError) as error:
        print(json.dumps({"ok": False, "errors": [str(error)]}))
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
