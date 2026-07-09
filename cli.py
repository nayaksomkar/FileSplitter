"""Command-line interface for FileSplitter.

Usage:
    filesplitter [folder] [--config CONFIG] [--min-size MIN_SIZE]
                 [--max-part-size MAX_SIZE] [--exts EXTS ...]
"""

from __future__ import annotations

import argparse
import os
import sys
import time

from config import load_config, resolve_settings
from discovery import MIN_SPLIT_SIZE, discover_large_videos
from ffmpeg import ensure_ffmpeg
from splitter import split_video


def fmt_size(bytes_val: int) -> str:
    """Format bytes into human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if bytes_val < 1024:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.2f} PB"


def fmt_time(seconds: float) -> str:
    """Format seconds into mm:ss."""
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def progress_bar(current: int, total: int, bar_width: int = 30) -> str:
    """Render a text progress bar with percentage."""
    if total == 0:
        return "[Error: total is zero]"
    fraction = current / total
    filled = int(bar_width * fraction)
    bar = "█" * filled + "░" * (bar_width - filled)
    pct = fraction * 100
    return f"|{bar}| {pct:5.1f}%"


def print_header(title: str) -> None:
    """Print a section header with decorative border."""
    width = 60
    print("╔" + "═" * (width - 2) + "╗")
    padding = (width - 2 - len(title)) // 2
    print("║" + " " * padding + title + " " * (width - 2 - len(title) - padding) + "║")
    print("╚" + "═" * (width - 2) + "╝")


def print_step(step: int, total: int, message: str) -> None:
    """Print a step indicator."""
    print(f"  └─ [{step}/{total}] {message}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="filesplitter",
        description="Split large video files into smaller parts using FFmpeg.",
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Folder containing videos to split (default: from config or CWD).",
    )
    parser.add_argument(
        "--config",
        default=None,
        help="Path to a config.json file (default: ./config.json if present).",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=None,
        help="Minimum file size in bytes to consider for splitting.",
    )
    parser.add_argument(
        "--max-part-size",
        type=int,
        default=None,
        help="Maximum size in bytes of each produced part.",
    )
    parser.add_argument(
        "--exts",
        nargs="+",
        default=None,
        help="Space-separated list of video extensions, e.g. .mp4 .mkv",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Entry point: load config, find large videos, split them."""
    overall_start = time.time()

    print_header("FileSplitter v0.1.0")

    args = parse_args(argv)
    config = load_config(args.config)
    settings = resolve_settings(config, args)

    folder = settings.get("folder") or os.getcwd()
    if not os.path.isdir(folder):
        print(f"\n  ✗ Error: folder not found: {folder}")
        return 1

    print(f"\n  📁 Folder: {folder}")
    print(f"  📐 Min size: {fmt_size(settings.get('min_size') or 0)}")
    if settings.get("max_part_size"):
        print(f"  ✂️  Max part: {fmt_size(settings['max_part_size'])}")
    else:
        print(f"  ✂️  Split: 2 equal halves")
    if settings.get("quiet"):
        print(f"  🔇 Quiet mode: on")
    if settings.get("delete_after"):
        print(f"  ⚠️  Delete originals: YES")
    print()

    video_exts = (
        set(e.lower() for e in settings["video_exts"])
        if settings.get("video_exts")
        else None
    )

    print("  🔍 Checking for FFmpeg...", end=" ", flush=True)
    ffmpeg, ffprobe = ensure_ffmpeg(url=settings.get("ffmpeg_url"))
    print("✓")

    print("  📡 Scanning for large videos...", end=" ", flush=True)
    large_videos = discover_large_videos(
        folder,
        min_size=settings.get("min_size") or 0,
        video_exts=video_exts,
    )
    print(f"found {len(large_videos)} file(s)\n")

    if not large_videos:
        print("  ✓ No videos to split.")
        elapsed = time.time() - overall_start
        print(f"\n  ⏱  Total time: {fmt_time(elapsed)}")
        return 0

    total_files = len(large_videos)
    for file_idx, (path, size) in enumerate(large_videos, 1):
        base_name = os.path.basename(path)
        print_header(f"File {file_idx}/{total_files}: {base_name}")
        print(f"  Size: {fmt_size(size)}")

        split_video(
            ffmpeg,
            ffprobe,
            path,
            size,
            max_part_size=settings.get("max_part_size"),
            delete_after=settings.get("delete_after", False),
        )

    elapsed = time.time() - overall_start
    print_header("Complete")
    print(f"\n  ✅ All done! Time elapsed: {fmt_time(elapsed)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())