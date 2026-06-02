#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 2 ]; then
  echo "Usage: $0 INPUT_VIDEO OUTPUT_VIDEO [PROMPT]" >&2
  exit 2
fi

INPUT_VIDEO="$1"
OUTPUT_VIDEO="$2"
PROMPT="${3:-a high quality video}"

EXPERIMENT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENHANCER_ROOT="${VENHANCER_ROOT:-/root/realwonder_test/v2v_repos/VEnhancer}"
VENHANCER_PYTHON="${VENHANCER_PYTHON:-python}"
MODEL_PATH_ARG=()

if [ -n "${VENHANCER_MODEL_PATH:-}" ]; then
  MODEL_PATH_ARG=(--model_path "$VENHANCER_MODEL_PATH")
fi

if [ ! -f "$INPUT_VIDEO" ]; then
  echo "Input video not found: $INPUT_VIDEO" >&2
  exit 1
fi

if [ ! -d "$VENHANCER_ROOT" ]; then
  echo "VEnhancer repo not found: $VENHANCER_ROOT" >&2
  exit 1
fi

ABS_INPUT="$(realpath "$INPUT_VIDEO")"
ABS_OUTPUT="$(realpath -m "$OUTPUT_VIDEO")"
OUT_DIR="$(dirname "$ABS_OUTPUT")"
mkdir -p "$OUT_DIR"
EXPECTED_RAW="$OUT_DIR/$(basename "${INPUT_VIDEO%.*}").mp4"

cd "$VENHANCER_ROOT"
"$VENHANCER_PYTHON" enhance_a_video.py \
  --version "${VENHANCER_VERSION:-v2}" \
  --up_scale "${VENHANCER_UP_SCALE:-1}" \
  --target_fps "${VENHANCER_TARGET_FPS:-24}" \
  --noise_aug "${VENHANCER_NOISE_AUG:-200}" \
  --solver_mode "${VENHANCER_SOLVER_MODE:-fast}" \
  --steps "${VENHANCER_STEPS:-15}" \
  --input_path "$ABS_INPUT" \
  --prompt "$PROMPT" \
  --save_dir "$OUT_DIR" \
  "${MODEL_PATH_ARG[@]}"

if [ "$EXPECTED_RAW" != "$ABS_OUTPUT" ]; then
  cp "$EXPECTED_RAW" "$ABS_OUTPUT"
fi

echo "Wrote VEnhancer vanilla output: $ABS_OUTPUT"
