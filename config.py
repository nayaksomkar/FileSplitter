"""Configuration loading and merging for FileSplitter.

Loads settings from config.json (searched in: exe folder, _MEIPASS, CWD).
CLI arguments override config.json values.
"""

from __future__ import annotations

import json
import os
import sys

# Filename expected next to the executable / in CWD
DEFAULT_CONFIG_NAME = "config.json"


def _gb_to_bytes(gb: float) -> int:
    """Convert gigabytes to bytes."""
    return int(gb * 1024 * 1024 * 1024)


def _config_search_paths(path: str | None) -> list[str]:
    """Resolve candidate locations for the config file.

    When running as a PyInstaller bundle the config.json should live
    next to the executable.  Otherwise fall back to the current directory.
    """
    if path:
        return [path]

    base_dirs: list[str] = []
    if getattr(sys, "frozen", False):
        # PyInstaller: look next to the exe first
        base_dirs.append(os.path.dirname(sys.executable))
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            base_dirs.append(meipass)
    base_dirs.append(os.getcwd())

    return [os.path.join(d, DEFAULT_CONFIG_NAME) for d in base_dirs]


def load_config(path: str | None = None) -> dict:
    """Load configuration from a JSON file. Returns {} when none is found."""
    for candidate in _config_search_paths(path):
        if candidate and os.path.exists(candidate):
            with open(candidate, "r", encoding="utf-8") as fh:
                return json.load(fh)
    return {}


def resolve_settings(config: dict, args: object) -> dict:
    """Merge config.json values with CLI args (CLI args win)."""
    settings: dict = {
        "folder": config.get("folder"),
        "min_size": config.get("min_size"),
        "max_part_size": config.get("max_part_size"),
        "video_exts": config.get("video_exts"),
        "ffmpeg_url": config.get("ffmpeg_url"),
        "quiet": config.get("quiet", True),
    }

    # Support human-friendly GB notation in config.json
    if config.get("min_size_gb") is not None:
        settings["min_size"] = _gb_to_bytes(config["min_size_gb"])
    if config.get("max_part_size_gb") is not None:
        settings["max_part_size"] = _gb_to_bytes(config["max_part_size_gb"])

    # CLI overrides (args from argparse)
    if getattr(args, "folder", None):
        settings["folder"] = args.folder
    if getattr(args, "min_size", None) is not None:
        settings["min_size"] = args.min_size
    if getattr(args, "max_part_size", None) is not None:
        settings["max_part_size"] = args.max_part_size
    if getattr(args, "exts", None):
        settings["video_exts"] = args.exts
    if getattr(args, "config", None):
        settings["_config_path"] = args.config

    return settings