# FileSplitter

A video file splitter. Scans a folder for large video files and cuts each into smaller parts using FFmpeg (stream copy — fast, lossless, no re-encoding). Original files are untouched.

---

## Download & run

**Step 1** — Create a folder somewhere on your computer and put these 3 files in it:

```
YourFolder/
├── filesplitter      ← the program (download this)
├── config.json       ← your settings
└── README.md         ← this file (keep for reference)
```

**Step 2** — Open `config.json` in any text editor and change `"folder"` to your video path:

```json
{
  "folder": ".",
  "min_size_gb": 1.90,
  "max_part_size_gb": 1.80,
  "video_exts": [".mp4", ".mkv", ".mov", ".avi", ".flv", ".wmv", ".webm"],
  "ffmpeg_url": "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip",
  "quiet": true,
  "delete_after": false
}
```

- Set `"folder"` to your video path (e.g. `"C:/Users/You/Videos"`) or leave `"."` if the exe is in the same folder as the videos

**Step 3** — Run it:
- **Windows:** double-click `filesplitter.exe`
- **Linux/macOS:** open a terminal and run `./filesplitter`

FFmpeg downloads automatically on first run. That's it.

---

## Config reference

| Field | Default | What it does |
|---|---|---|
| `folder` | `"."` | Path to folder with videos (`"."` = same folder as exe) |
| `min_size_gb` | `1.90` | Skip files smaller than this (GB). Only process videos **bigger** than this |
| `max_part_size_gb` | `1.80` | Max size per output part (GB). Set to `null` or remove to split into 2 equal halves |
| `video_exts` | `.mp4 .mkv .mov .avi .flv .wmv .webm` | Which file types to scan |
| `quiet` | `true` | `false` = show full FFmpeg output |
| `delete_after` | `false` | `true` = delete the original video file after splitting. **Use with caution — files cannot be recovered** |

---

```
╔══════════════════════════════════════════════════════════╗
║                   FileSplitter v0.1.0                    ║
╚══════════════════════════════════════════════════════════╝

  📁 Folder: /home/user/Videos
  📐 Min size: 1.90 GB
  ✂️  Max part: 1.00 GB
  🔇 Quiet mode: on

  🔍 Checking for FFmpeg... ✓
  📡 Scanning for large videos... found 1 file(s)

╔══════════════════════════════════════════════════════════╗
║         File 1/1: video.mp4                              ║
╚══════════════════════════════════════════════════════════╝
  Size: 5.55 GB
  Part count: 6
  Duration:   39:33

  ██████████████████████████████ 100%  Part 6/6  928.0 MB  ⏱ 02:32  ETA 00:00

  ✅ Split complete in 02:32
  🗑️  Deleted original: video.mp4

╔══════════════════════════════════════════════════════════╗
║                         Complete                         ║
╚══════════════════════════════════════════════════════════╝

  ✅ All done! Time elapsed: 02:33
```

## What happens

- Scans the folder for videos larger than `min_size_gb`
- Splits each into `_part1`, `_part2`, etc. (no re-encoding, 100% quality)
  - Calculates the **minimum number of parts** needed so each part stays under `max_part_size`
  - Example: 5.6 GB file → `ceil(5.6 / 1.8)` = **4 parts** at ~1.4 GB each
- Original files are **not deleted** by default
- Set `"delete_after": true` to remove the original after splitting completes  
  - Shows: `🗑️  Deleted original: video.mp4`

---

## Build from source

```bash
uv sync
uv run pyinstaller --onefile --name filesplitter cli.py
```

## License

MIT