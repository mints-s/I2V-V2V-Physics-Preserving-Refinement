#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 INPUT_MP4 OUTPUT_MP4 [PROMPT] [NOISE_AUG] [TARGET_FPS] [STEPS]" >&2
  exit 2
fi

INPUT_MP4="$1"
OUTPUT_MP4="$2"
PROMPT="${3:-a high quality video}"
NOISE_AUG="${4:-100}"
TARGET_FPS="${5:-24}"
STEPS="${6:-15}"

VENHANCER_ROOT="${VENHANCER_ROOT:-/root/realwonder_test/v2v_repos/VEnhancer}"
VENHANCER_PYTHON="${VENHANCER_PYTHON:-/root/miniconda3/envs/venhancer/bin/python}"

if [ ! -f "$INPUT_MP4" ]; then
  echo "Input video not found: $INPUT_MP4" >&2
  exit 1
fi

if [ ! -d "$VENHANCER_ROOT" ]; then
  echo "VEnhancer repo not found: $VENHANCER_ROOT" >&2
  exit 1
fi

ABS_INPUT="$(realpath "$INPUT_MP4")"
ABS_OUTPUT="$(realpath -m "$OUTPUT_MP4")"
OUTPUT_DIR="$(dirname "$ABS_OUTPUT")"
mkdir -p "$OUTPUT_DIR"

TMP_DIR="$OUTPUT_DIR/.tmp_venhancer_$(date +%Y%m%d_%H%M%S)_$$"
mkdir -p "$TMP_DIR"

cd "$VENHANCER_ROOT"
"$VENHANCER_PYTHON" enhance_a_video.py \
  --version v2 \
  --up_scale 1 \
  --target_fps "$TARGET_FPS" \
  --noise_aug "$NOISE_AUG" \
  --solver_mode fast \
  --steps "$STEPS" \
  --input_path "$ABS_INPUT" \
  --prompt "$PROMPT" \
  --save_dir "$TMP_DIR"

GENERATED_MP4="$(find "$TMP_DIR" -maxdepth 1 -type f -name '*.mp4' | sort | tail -n 1)"
if [ -z "$GENERATED_MP4" ]; then
  echo "No generated mp4 found in: $TMP_DIR" >&2
  exit 1
fi

cp "$GENERATED_MP4" "$ABS_OUTPUT"
echo "Wrote VEnhancer output: $ABS_OUTPUT"

if command -v ffprobe >/dev/null 2>&1; then
  ffprobe -v error -show_entries stream=width,height,r_frame_rate,duration -of default=noprint_wrappers=1 "$ABS_OUTPUT" || true
fi
