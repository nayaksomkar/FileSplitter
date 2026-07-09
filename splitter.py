"""FFmpeg-based video splitting logic.

Splits a video into N equal-duration parts using stream copy (-c copy),
so no re-encoding happens — fast and lossless.

When max_part_size is None, the video is split into 2 equal halves.
"""

from __future__ import annotations

import math
import os
import subprocess
import time

from ffmpeg import run_ffmpeg

_WIDTH = 30


def _bar(filled: int, total: int) -> str:
    """Render a progress bar segment."""
    f = int(_WIDTH * filled / total) if total else 0
    return "█" * f + "░" * (_WIDTH - f)


def _fmt_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def _fmt_size(b: int) -> str:
    for u in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.1f} {u}"
        b //= 1024
    return f"{b:.1f} TB"


def get_duration(ffprobe: str, filepath: str) -> float:
    """Return the duration in seconds using ffprobe."""
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
    max_part_size: int | None = None,
    delete_after: bool = False,
) -> list[str]:
    """Split ``filepath`` into parts.

    If ``max_part_size`` is given, calculates parts needed to keep each
    under that size.  If None, splits into 2 equal halves.

    If ``delete_after`` is True, the original file is removed once all
    parts have been created successfully.

    Returns the list of created part file paths.
    """
    if max_part_size is not None:
        num_parts = max(1, math.ceil(file_size / max_part_size))
    else:
        num_parts = 2

    folder = os.path.dirname(filepath)
    base_name = os.path.basename(filepath)
    name, ext = os.path.splitext(base_name)

    print(f"  Part count: {num_parts}")
    print(f"  File size:  {_fmt_size(file_size)}")

    duration = get_duration(ffprobe, filepath)
    part_duration = duration / num_parts
    print(f"  Duration:   {_fmt_time(duration)}")
    print()

    parts: list[str] = []
    overall_start = time.time()

    for i in range(num_parts):
        start_time = i * part_duration
        out_file = os.path.join(folder, f"{name}_part{i + 1}{ext}")

        cmd = [
            ffmpeg,
            "-ss",
            str(start_time),
            "-i",
            filepath,
            "-t",
            str(part_duration),
            "-c",
            "copy",
            out_file,
        ]

        elapsed = time.time() - overall_start
        part_start = time.time()

        run_ffmpeg(cmd)

        part_elapsed = time.time() - part_start
        total_elapsed = time.time() - overall_start

        bar = _bar(i + 1, num_parts)
        pct = (i + 1) * 100 // num_parts
        eta = (total_elapsed / (i + 1)) * (num_parts - i - 1) if i < num_parts - 1 else 0

        size_str = _fmt_size(os.path.getsize(out_file)) if os.path.exists(out_file) else "?"
        print(f"\r  {bar} {pct:3d}%  Part {i+1:2d}/{num_parts}  {size_str:>8}  "
              f"⏱ {_fmt_time(total_elapsed)}  ETA {_fmt_time(eta)}  ", flush=True)

        parts.append(out_file)

    total_time = time.time() - overall_start
    print(f"\n  ✅ Split complete in {_fmt_time(total_time)}")
    print(f"     Output: {num_parts} part(s) in {folder}")

    if delete_after:
        os.remove(filepath)
        print(f"  🗑️  Deleted original: {base_name}")

    print()
    return parts