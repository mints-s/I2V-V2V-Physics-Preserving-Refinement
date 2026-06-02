#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python scripts/create_dummy_video.py --out outputs/stage1/scene01_seed0.mp4
cp outputs/stage1/scene01_seed0.mp4 outputs/v2v/vanilla/scene01_seed0.mp4
cp outputs/stage1/scene01_seed0.mp4 outputs/v2v/flowguided/scene01_seed0.mp4

python scripts/flow_preservation_metric.py \
  --stage1 outputs/stage1/scene01_seed0.mp4 \
  --refined outputs/v2v/vanilla/scene01_seed0.mp4 \
  --out metrics/scene01_seed0_vanilla_flow.csv

python scripts/video_quality_proxy.py \
  --video outputs/v2v/vanilla/scene01_seed0.mp4 \
  --out metrics/scene01_seed0_vanilla_quality.csv

python scripts/flow_preservation_metric.py \
  --stage1 outputs/stage1/scene01_seed0.mp4 \
  --refined outputs/v2v/flowguided/scene01_seed0.mp4 \
  --out metrics/scene01_seed0_flowguided_flow.csv

python scripts/video_quality_proxy.py \
  --video outputs/v2v/flowguided/scene01_seed0.mp4 \
  --out metrics/scene01_seed0_flowguided_quality.csv

python scripts/summarize_metrics.py

echo "Smoke test complete. Identical Stage-1/refined videos should have flow EPE close to 0."
