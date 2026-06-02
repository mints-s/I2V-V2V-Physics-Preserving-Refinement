# NEXT STEPS

## Current status

Experiment folder:
`/root/realwonder_test/i2v_v2v_physics`

RealWonder repo:
`/root/realwonder_test/RealWonder`

VEnhancer repo:
`/root/realwonder_test/v2v_repos/VEnhancer`

Do not modify RealWonder source files.

## Completed

- Experiment scaffold created.
- Smoke test passed.
- RealWonder Stage-1 videos copied and normalized.
- Scene01 VEnhancer strength sweep completed.
- VEnhancer n50, n100, n200 succeeded.
- Best trade-off so far: `venhancer_n50`.

## Scene01 results

| method | mean_flow_epe | flow_mag_ratio | mean_sharpness | mean_frame_diff |
|---|---:|---:|---:|---:|
| stage1_baseline | 0.0000 | 1.0000 | 172.25 | 1.5912 |
| venhancer_n50 | 0.4244 | 3.7275 | 666.82 | 2.0271 |
| venhancer_n100 | 0.4754 | 5.6352 | 687.41 | 1.9586 |
| venhancer_n200 | 0.5711 | 7.6986 | 607.16 | 2.0761 |

Interpretation:
VEnhancer improves visual/detail proxy but changes Stage-1 dynamics.
n50 is the least damaging among tested VEnhancer settings.

## Next task

Run VEnhancer n50 on:

- `scene02_seed0`
- `scene03_seed0`

Then normalize outputs and rerun metrics.

## Commands to continue

```bash
cd /root/realwonder_test/i2v_v2v_physics

VENHANCER_PYTHON=/root/miniconda3/envs/venhancer/bin/python \
bash scripts/run_venhancer_param.sh \
  outputs/normalized/stage1/scene02_seed0.mp4 \
  outputs/v2v/venhancer_n50/scene02_seed0.mp4 \
  "a high quality physically plausible video with stable motion" \
  50 24 15

VENHANCER_PYTHON=/root/miniconda3/envs/venhancer/bin/python \
bash scripts/run_venhancer_param.sh \
  outputs/normalized/stage1/scene03_seed0.mp4 \
  outputs/v2v/venhancer_n50/scene03_seed0.mp4 \
  "a high quality physically plausible video with stable motion" \
  50 24 15

conda run -n eval_video bash scripts/normalize_video.sh \
  outputs/v2v/venhancer_n50/scene02_seed0.mp4 \
  outputs/normalized/v2v/venhancer_n50/scene02_seed0.mp4 \
  16 512 512 4

conda run -n eval_video bash scripts/normalize_video.sh \
  outputs/v2v/venhancer_n50/scene03_seed0.mp4 \
  outputs/normalized/v2v/venhancer_n50/scene03_seed0.mp4 \
  16 512 512 4
```

Update `configs/experiments.csv` to include Stage-1 baseline and `venhancer_n50` for scene01, scene02, and scene03, then run:

```bash
conda run -n eval_video python scripts/run_metrics_batch.py
conda run -n eval_video python scripts/summarize_metrics.py
cat metrics/summary_detail.csv
cat metrics/summary_by_method.csv
```

## Pause update

Scene02 VEnhancer n50 generation and normalization completed.

Completed files:
- outputs/v2v/venhancer_n50/scene02_seed0.mp4
- outputs/normalized/v2v/venhancer_n50/scene02_seed0.mp4

Next task:
1. Run VEnhancer n50 for scene03.
2. Normalize scene03 output.
3. Update configs/experiments.csv for scene01/02/03 stage1_baseline + venhancer_n50.
4. Run:
   conda run -n eval_video python scripts/run_metrics_batch.py
   conda run -n eval_video python scripts/summarize_metrics.py
5. Create/inspect contact sheets.
6. Then perform physical plausibility qualitative evaluation.

Reminder:
Stage-1 video is Stage-1 dynamics / physics-induced motion prior, not physical ground truth.
