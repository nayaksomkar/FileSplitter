"""FFmpeg-based video splitting logic.

Splits a video into N equal-duration parts using stream copy (-c copy),
so no re-encoding happens — fast and lossless.
"""

from __future__ import annotations

import math
import os
import subprocess

from ffmpeg import run_ffmpeg
from discovery import MAX_PART_SIZE


def get_duration(ffprobe: str, filepath: str) -> float:
    """Return the duration of ``filepath`` in seconds using ffprobe."""
    result = subprocess.run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filepath,
        ],
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def split_video(
    ffmpeg: str,
    ffprobe: str,
    filepath: str,
    file_size: int,
    max_part_size: int = MAX_PART_SIZE,
) -> list[str]:
    """Split ``filepath`` into parts no larger than ``max_part_size``.

    Calculates the number of parts needed, then uses ffmpeg -ss/-t -c copy
    to extract each segment. Original file is left untouched.

    Returns the list of created part file paths.
    """
    num_parts = max(1, math.ceil(file_size / max_part_size))

    folder = os.path.dirname(filepath)
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)

    print(f"Splitting {base_name} into {num_parts} part(s)...")
    duration = get_duration(ffprobe, filepath)
    part_duration = duration / num_parts

    parts: list[str] = []
    for i in range(num_parts):
        start_time = i * part_duration
        out_file = os.path.join(folder, f"{name}_part{i + 1}{ext}")

        # FFmpeg command: fast seek (-ss before -i), copy all streams
        cmd = [
            ffmpeg,
            "-ss",
            str(start_time),
            "-i",
            filepath,
            "-t",
            str(part_duration),
            "-c",
            "copy",  # stream copy — no re-encode, lossless
            out_file,
        ]

        print(f"Creating part {i + 1}...")
        run_ffmpeg(cmd)
        parts.append(out_file)
        print(f"Saved: {out_file}")

    print("Done!\n")
    return parts