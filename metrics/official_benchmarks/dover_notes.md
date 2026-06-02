# DOVER Notes

- Repository: `/root/realwonder_test/benchmark_repos/DOVER`
- Commit: `f1ddc96215bc7fbcf8f315c65d47905f339c3419`
- Environment: `dover_eval`
- Output CSV: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/dover_results.csv`
- Raw outputs: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/dover_raw/`
- Weight: `/root/realwonder_test/benchmark_repos/DOVER/pretrained_weights/DOVER.pth`

## Install Commands

```bash
cd /root/realwonder_test/benchmark_repos
git clone https://github.com/VQAssessment/DOVER.git
conda create -n dover_eval python=3.10 -y
conda run -n dover_eval pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
conda run -n dover_eval pip install opencv-python decord matplotlib scipy tqdm timm einops wandb scikit-video thop==0.0.31-2005241907 onnx pyyaml pandas
conda run -n dover_eval pip install --no-deps -e /root/realwonder_test/benchmark_repos/DOVER
mkdir -p pretrained_weights
wget -nc https://github.com/QualityAssessment/DOVER/releases/download/v0.1.0/DOVER.pth -O pretrained_weights/DOVER.pth
```

## Evaluation Command

```bash
conda run -n dover_eval python evaluate_one_video.py -v <video_path> -f
```

## Status

- Succeeded: fused DOVER overall score for all 12 target videos.
- `dover_technical` and `dover_aesthetic` are left blank in `dover_results.csv` because the paper-ready run used DOVER's fused overall mode (`-f`), which gives a single normalized overall score.

## Caveats

The README dependency target is older (`torch~=1.13`). The isolated environment used PyTorch CUDA 12.1 wheels for compatibility with the current GPU stack. DOVER is a no-reference perceptual video quality metric, not a physics-correctness metric.
