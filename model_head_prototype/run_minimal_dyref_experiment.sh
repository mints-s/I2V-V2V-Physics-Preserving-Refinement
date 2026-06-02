#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

python model_head_prototype/train_dyref_overfit.py
python model_head_prototype/export_dyref_outputs.py

mkdir -p outputs/normalized/v2v/dyref_head
for scene in scene01_seed0 scene02_seed0 scene03_seed0; do
  bash scripts/normalize_video.sh \
    "outputs/v2v/dyref_head/${scene}.mp4" \
    "outputs/normalized/v2v/dyref_head/${scene}.mp4" \
    16 128 128 2
done

cat > configs/experiments_dyref.csv <<'CSV'
scene,seed,stage1_video,v2v_method,refined_video
scene01,0,outputs/normalized/stage1/scene01_seed0.mp4,stage1_baseline,outputs/normalized/stage1/scene01_seed0.mp4
scene01,0,outputs/normalized/stage1/scene01_seed0.mp4,venhancer_n30,outputs/normalized/v2v/venhancer_n30/scene01_seed0.mp4
scene01,0,outputs/normalized/stage1/scene01_seed0.mp4,dyref_head,outputs/normalized/v2v/dyref_head/scene01_seed0.mp4
scene02,0,outputs/normalized/stage1/scene02_seed0.mp4,stage1_baseline,outputs/normalized/stage1/scene02_seed0.mp4
scene02,0,outputs/normalized/stage1/scene02_seed0.mp4,venhancer_n30,outputs/normalized/v2v/venhancer_n30/scene02_seed0.mp4
scene02,0,outputs/normalized/stage1/scene02_seed0.mp4,dyref_head,outputs/normalized/v2v/dyref_head/scene02_seed0.mp4
scene03,0,outputs/normalized/stage1/scene03_seed0.mp4,stage1_baseline,outputs/normalized/stage1/scene03_seed0.mp4
scene03,0,outputs/normalized/stage1/scene03_seed0.mp4,venhancer_n30,outputs/normalized/v2v/venhancer_n30/scene03_seed0.mp4
scene03,0,outputs/normalized/stage1/scene03_seed0.mp4,dyref_head,outputs/normalized/v2v/dyref_head/scene03_seed0.mp4
CSV

python scripts/run_metrics_batch.py --config configs/experiments_dyref.csv

timestamp="$(date +%Y%m%d_%H%M%S)"
backup="configs/experiments_backup_before_dyref_${timestamp}.csv"
cp configs/experiments.csv "$backup"
restore_config() {
  cp "$backup" configs/experiments.csv
}
trap restore_config EXIT

cp configs/experiments_dyref.csv configs/experiments.csv
python scripts/summarize_metrics.py

mkdir -p metrics/dyref_head_experiment
cp configs/experiments_dyref.csv metrics/dyref_head_experiment/
cp metrics/summary_detail.csv metrics/dyref_head_experiment/summary_detail.csv
cp metrics/summary_by_method.csv metrics/dyref_head_experiment/summary_by_method.csv
cp metrics/*_dyref_head_flow.csv metrics/dyref_head_experiment/ 2>/dev/null || true
cp metrics/*_dyref_head_quality.csv metrics/dyref_head_experiment/ 2>/dev/null || true

echo "dyref_experiment_summary=metrics/dyref_head_experiment"
