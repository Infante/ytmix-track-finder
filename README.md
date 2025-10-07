Nice! Here's a polished version with better formatting and clarity:

```markdown
# YouTube Mix Track Finder

Find all the tracks in your favorite YouTube DJ mixes and sets.

## Installation

```bash
pip install git+https://github.com/Infante/ytmix-track-finder.git
```

## Requirements

**FFmpeg must be installed:**

- **macOS:** `brew install ffmpeg`
- **Ubuntu/Debian:** `sudo apt install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org)

## Usage

```bash
yt-mix https://www.youtube.com/watch?v=VIDEO_ID
```

## How It Works

1. Downloads audio from YouTube video
2. Splits audio into overlapping chunks (every 30 seconds by default)
3. Identifies each chunk using Shazam
4. Deduplicates consecutive matches
5. Outputs a clean tracklist with timestamps

## Updating

```bash
pip install --upgrade --force-reinstall git+https://github.com/Infante/ytmix-track-finder.git
```

## Uninstall

```bash
pip uninstall ytmix-track-finder
```

## License

MIT
