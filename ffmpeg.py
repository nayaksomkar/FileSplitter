"""FFmpeg discovery and automatic installation helpers.

On first run the tool checks:
  1. System PATH for ffmpeg/ffprobe
  2. Local ./ffmpeg_auto/ folder
  3. Downloads FFmpeg automatically (Windows zip from gyan.dev)
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import urllib.request
import zipfile

# Official Windows static build used for the auto-installer.
FFMPEG_WINDOWS_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"


def ffmpeg_folder() -> str:
    """Return the directory where FFmpeg is stored/downloaded."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg_auto")


def find_system_ffmpeg() -> tuple[str | None, str | None]:
    """Return (ffmpeg, ffprobe) paths from the system PATH, if available."""
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")
    if ffmpeg and ffprobe:
        return ffmpeg, ffprobe
    return None, None


def local_ffmpeg_paths() -> tuple[str, str]:
    """Return the expected local FFmpeg binary paths inside the project."""
    folder = ffmpeg_folder()
    suffix = ".exe" if platform.system() == "Windows" else ""
    return (
        os.path.join(folder, "bin", f"ffmpeg{suffix}"),
        os.path.join(folder, "bin", f"ffprobe{suffix}"),
    )


def download_ffmpeg_windows(folder: str, url: str = FFMPEG_WINDOWS_URL) -> None:
    """Download and extract the Windows FFmpeg build into ``folder``."""
    os.makedirs(folder, exist_ok=True)
    zip_path = os.path.join(folder, "ffmpeg.zip")

    print("Downloading FFmpeg (100+ MB)...")
    urllib.request.urlretrieve(url, zip_path)
    print("Download complete. Extracting...")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(folder)

    # The zip extracts into a subfolder; move contents up one level
    extracted = None
    for name in os.listdir(folder):
        if name.startswith("ffmpeg") and os.path.isdir(os.path.join(folder, name)):
            extracted = os.path.join(folder, name)
            break

    if extracted:
        for item in os.listdir(extracted):
            shutil.move(os.path.join(extracted, item), os.path.join(folder, item))
        shutil.rmtree(extracted)

    os.remove(zip_path)
    print("FFmpeg ready.\n")


def ensure_ffmpeg(url: str = FFMPEG_WINDOWS_URL) -> tuple[str, str]:
    """Return (ffmpeg, ffprobe) paths, downloading FFmpeg if necessary."""
    # 1. Check system PATH
    system_ffmpeg, system_ffprobe = find_system_ffmpeg()
    if system_ffmpeg and system_ffprobe:
        return system_ffmpeg, system_ffprobe

    # 2. Check local auto-download folder
    ffmpeg_path, ffprobe_path = local_ffmpeg_paths()
    if os.path.exists(ffmpeg_path) and os.path.exists(ffprobe_path):
        return ffmpeg_path, ffprobe_path

    # 3. Download fresh copy
    print("FFmpeg not found. Downloading automatically...")
    download_ffmpeg_windows(ffmpeg_folder(), url)
    return ffmpeg_path, ffprobe_path


def run_ffmpeg(command: list[str], quiet: bool = True) -> int:
    """Run an FFmpeg/FFprobe command and return its exit code."""
    stdout = subprocess.DEVNULL if quiet else None
    stderr = subprocess.DEVNULL if quiet else subprocess.STDOUT
    result = subprocess.run(command, stdout=stdout, stderr=stderr)
    return result.returncode