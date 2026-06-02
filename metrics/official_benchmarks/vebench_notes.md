# VE-Bench Notes

- Repository: `/root/realwonder_test/benchmark_repos/VE-Bench`
- Commit: `692faa944e6215c1a032cdd350c2d15d48a15156`
- Environment: `vebench_eval`
- Output CSV: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vebench_results.csv`

## Inspected Official Instructions

The README provides two paths:

```bash
pip install vebench
```

and local inference with checkpoints placed in `ckpts`:

```bash
python -m infer.py --single_test --src_path <src> --dst_path <dst> --prompt <prompt>
```

The code loads the following local checkpoint files from `ckpts`:

- `e-bench-dover_head_videoQA_0_eval_n_finetuned.pth`
- `e-bench-uniformer-src-edit_head_videoQA_3_eval_s_finetuned.pth`
- `e-bench-blip_head_videoQA_9_eval_s_finetuned.pth`
- `k400+k710_uniformerv2_b16_8x224.pth`
- `model_large.pth`

## Status

VE-Bench was not run. The official checkpoints are provided through a Google Drive folder in the README and were not present under `/root/realwonder_test/benchmark_repos/VE-Bench/ckpts`. Because the task explicitly says to stop benchmarks requiring unavailable model weights or manual access, this benchmark is recorded as `failed_missing_official_checkpoints`.

## Caveat

VE-Bench QA is designed for text-driven video editing evaluation. Even if run later, it should be used only as an auxiliary source-refined relation metric, not as a main physical correctness benchmark.
