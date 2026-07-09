"""Command-line interface for FileSplitter.

Usage:
    filesplitter [folder] [--config CONFIG] [--min-size MIN_SIZE]
                 [--max-part-size MAX_SIZE] [--exts EXTS ...]
"""

from __future__ import annotations

import argparse
import os
import sys

from config import load_config, resolve_settings
from discovery import MIN_SPLIT_SIZE, discover_large_videos
from ffmpeg import ensure_ffmpeg
from splitter import split_video


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
    args = parse_args(argv)

    # Load config from file (CLI --config overrides the default path)
    config = load_config(args.config)
    # Merge config.json values with CLI args (CLI args take precedence)
    settings = resolve_settings(config, args)

    # Determine the target folder
    folder = settings.get("folder") or os.getcwd()
    if not os.path.isdir(folder):
        print(f"Error: folder not found: {folder}", file=sys.stderr)
        return 1

    # Normalize video extensions to lowercase set for fast lookup
    video_exts = (
        set(e.lower() for e in settings["video_exts"])
        if settings.get("video_exts")
        else None
    )

    # Ensure FFmpeg is available (auto-download if missing)
    ffmpeg, ffprobe = ensure_ffmpeg(url=settings.get("ffmpeg_url"))

    # Scan for videos larger than the threshold
    large_videos = discover_large_videos(
        folder,
        min_size=settings.get("min_size") or MIN_SPLIT_SIZE,
        video_exts=video_exts,
    )

    if not large_videos:
        print("No videos above the size threshold found in this folder.")
        return 0

    # Split each large video into parts
    for path, size in large_videos:
        split_video(
            ffmpeg,
            ffprobe,
            path,
            size,
            max_part_size=settings.get("max_part_size"),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())