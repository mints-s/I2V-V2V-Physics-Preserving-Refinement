#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: bash scripts/normalize_video.sh INPUT_VIDEO OUTPUT_VIDEO FPS WIDTH HEIGHT DURATION"
  echo "Defaults: FPS=16 WIDTH=512 HEIGHT=512 DURATION=4"
  exit 1
fi

INPUT_VIDEO="$1"
OUTPUT_VIDEO="$2"
FPS="${3:-16}"
WIDTH="${4:-512}"
HEIGHT="${5:-512}"
DURATION="${6:-4}"

mkdir -p "$(dirname "$OUTPUT_VIDEO")"

ffmpeg -y \
  -i "$INPUT_VIDEO" \
  -vf "fps=${FPS},scale=${WIDTH}:${HEIGHT}:force_original_aspect_ratio=decrease,pad=${WIDTH}:${HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1" \
  -t "$DURATION" \
  -an \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "$OUTPUT_VIDEO"
