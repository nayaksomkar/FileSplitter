"""Video discovery helpers.

Scans a directory for video files above a configurable size threshold.
"""

from __future__ import annotations

import os

# Default extensions treated as video files
VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm"}

# 1.90 GB: files larger than this are candidates for splitting.
MIN_SPLIT_SIZE = int(1.9 * 1024 * 1024 * 1024)
# 1.80 GB: maximum size of each produced part.
MAX_PART_SIZE = int(1.8 * 1024 * 1024 * 1024)


def discover_large_videos(
    folder: str,
    min_size: int = MIN_SPLIT_SIZE,
    video_exts: set[str] | None = None,
) -> list[tuple[str, int]]:
    """Return a list of ``(path, size)`` for videos larger than ``min_size``."""
    if video_exts is None:
        video_exts = VIDEO_EXTS

    found: list[tuple[str, int]] = []
    for entry in os.listdir(folder):
        full_path = os.path.join(folder, entry)
        ext = os.path.splitext(entry)[1].lower()
        if os.path.isfile(full_path) and ext in video_exts:
            size = os.path.getsize(full_path)
            if size > min_size:
                found.append((full_path, size))
    return found