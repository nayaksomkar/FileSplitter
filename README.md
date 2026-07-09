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

**Step 2** — Open `config.json` in any text editor and set the folder that has your videos:

```json
{
  "folder": "C:/Users/You/Videos",
  "min_size_gb": 1.90,
  "max_part_size_gb": 1.80
}
```

- Set `"folder"` to the path where your big video files are
- Or use `"."` if you put the exe in the same folder as the videos

**Step 3** — Run it:
- **Windows:** double-click `filesplitter.exe`
- **Linux/macOS:** open a terminal and run `./filesplitter`

FFmpeg downloads automatically on first run. That's it.

---

## Config reference

| Field | Default | What it does |
|---|---|---|
| `folder` | `"."` | Path to folder with videos (`"."` = same folder as exe) |
| `min_size_gb` | `1.90` | Only split files **bigger** than this (GB) |
| `max_part_size_gb` | `1.80` | Max size of each output part (GB) |
| `video_exts` | `.mp4 .mkv .mov .avi .flv .wmv .webm` | Which file types to scan |
| `quiet` | `true` | `false` = show full FFmpeg output |

---

## What happens

- Scans the folder for videos larger than `min_size_gb`
- Splits each into `_part1`, `_part2`, etc. (no re-encoding, 100% quality)
- Original files are **not** deleted

---

## Build from source

```bash
uv sync
uv run pyinstaller --onefile --name filesplitter cli.py
```

## License

MIT