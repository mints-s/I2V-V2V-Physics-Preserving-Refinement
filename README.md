# I2V-V2V Physics-Preserving Refinement

Image-to-Video 생성 영상의 품질 향상을 위한 동역학 보존 제약 기반 출력 정제 헤드 연구용 저장소. 
이 프로젝트는 고정된 I2V 백본이 생성한 기준 영상의 움직임 구조를 동역학 선행정보로 보고, 그 후단에 학습 가능한 출력 정제 헤드인 DyRefHead를 결합해 시각 품질 개선과 움직임 보존 사이의 상충관계를 분석한다.

## Overview

최근 Image-to-Video(I2V) 모델은 단일 이미지와 텍스트 조건으로 시간적 장면 변화를 생성할 수 있을 정도로 발전했습니다. 그러나 I2V 출력은 동작 단서를 포함하더라도 최종 영상의 선명도와 디테일이 충분하지 않을 수 있습니다. 별도 Video-to-Video(V2V) 정제 모델은 시각 품질을 높일 수 있지만, 강한 정제는 기준 영상의 움직임 구조를 바꿀 수 있다.

본 연구는 이 문제를 다루기 위해 다음 구조를 사용하고 있음.

- 기준 I2V 출력 `V0`를 실제 물리 정답이 아니라 동역학 선행정보로 사용
- `V0` 뒤에 학습 가능한 비디오 공간 출력 정제 헤드 `DyRefHead`를 결합
- VEnhancer n30 결과를 시각 품질 의사 목표로 활용
- 시간 변화량 보존과 첫 프레임 정체성 제약으로 움직임 이탈을 제한

## Method

DyRefHead는 기준 영상을 직접 대체하지 않고, 보정 잔차를 더하는 방식으로 정제 영상을 생성.

```text
V_hat = clip(V0 + alpha * R_theta(V0), 0, 1)
```

여기서 `R_theta(V0)`는 DyRefHead가 예측한 보정 잔차이며, 본 실험에서는 `alpha = 0.5`를 사용.

학습 손실은 시각 품질 의사 목표와 동역학 보존 제약을 함께 사용.

```text
L_visual = || V_hat - Vp ||_1
L_edge   = || grad_xy(V_hat) - grad_xy(Vp) ||_1
L_temp   = || delta_t(V_hat) - delta_t(V0) ||_1
L_id     = || V_hat_1 - V0_1 ||_1
```

`Vp`는 VEnhancer n30 결과이며, 정답 영상이 아닌 시각적 디테일 개선 방향을 제공하는 의사 목표.

DyRefHead v2의 기본 가중치는 다음과 같다.

```text
lambda_visual = 1.0
lambda_edge = 0.5
lambda_temporal_delta = 0.2
lambda_identity = 0.05
```

DyRefHead v3는 edge 가중치를 높이고 temporal 가중치를 낮춘 절제 실험이고, 이 설정은 시각 품질 개선과 움직임 크기 보존 사이의 상충관계를 확인하기 위해 사용하였다.

## Experimental Setup

| Item | Setting |
|---|---|
| Stage-1 source | RealWonder |
| Scenes | 3 scenes |
| Video format | 256 x 256, 16 fps, 4 seconds |
| Pseudo visual target | VEnhancer n30 |
| Representative model | DyRefHead v2 |
| Ablation | DyRefHead v3 |
| Epochs / batch size | 20 / 1 |
| Learning rate | 1e-4 |
| GPU | NVIDIA H200 NVL |
| Quality metric | VBench Imaging, VBench Motion Smoothness |
| Auxiliary dynamics metric | mean Flow EPE, Flow magnitude ratio |

Flow 기반 지표는 실제 물리 정합성을 직접 검증하는 지표가 아닌 기준 I2V 출력 대비 움직임 이탈 정도를 확인하기 위한 보조 지표.

## Results

| Method | VBench Imaging ↑ | VBench Motion Smoothness ↑ | mean Flow EPE ↓ | Flow magnitude ratio ≈ 1 |
|---|---:|---:|---:|---:|
| Stage-1 I2V output | 0.6187 | 0.9948 | 0.0000 | 1.0000 |
| VEnhancer n30 | 0.6587 | 0.9940 | 0.2782 | 3.4906 |
| DyRefHead v2 | 0.6242 | 0.9939 | 0.1883 | 1.6971 |
| DyRefHead v3 | 0.6222 | 0.9939 | 0.1901 | 1.5899 |

VEnhancer n30은 가장 높은 VBench Imaging 값을 보였지만, mean Flow EPE와 Flow magnitude ratio도 크게 증가했다.
이는 강한 V2V 정제가 시각 품질을 높이는 동시에 기준 I2V 출력의 움직임 구조에서 더 많이 벗어날 수 있음을 보여준다.

DyRefHead v2는 VEnhancer n30만큼 강한 시각 품질 향상을 달성하지는 못했지만, Stage-1 I2V 출력보다 VBench Imaging을 소폭 향상시키면서 VEnhancer n30보다 낮은 움직임 이탈 보조 지표를 보임. 
DyRefHead v3는 Flow magnitude ratio를 v2보다 더 1에 가깝게 만들었지만, VBench Imaging은 낮아짐.

## Repository Structure

```text
configs/
  Experiment CSV files for metric runs.

model_head_prototype/
  DyRefHead implementation, training scripts, export scripts, and dataset utilities.

scripts/
  Video normalization, metric computation, summarization, contact sheet generation, and benchmark helpers.

metrics/
  Experiment summaries, benchmark tables, paper-ready notes, and auxiliary metric outputs.
```

Large generated assets are intentionally excluded from Git tracking.

```text
outputs/
logs/
*.mp4
*.pt
*.pth
*.ckpt
*.tar.gz
```

## Quick Start

Install the basic evaluation dependencies in a Python environment.

```bash
pip install torch opencv-python numpy pandas imageio imageio-ffmpeg scikit-image tqdm
```

Train DyRefHead v2.

```bash
python model_head_prototype/train_dyref_v2.py \
  --epochs 20 \
  --train_size 256 \
  --max_frames 64 \
  --batch_size 1 \
  --lr 1e-4
```

Export DyRefHead v2 outputs.

```bash
python model_head_prototype/export_dyref_v2_outputs.py \
  --ckpt model_head_prototype/checkpoints/dyref_v2_e20_256.pt \
  --output_dir outputs/v2v/dyref_head_v2_e20_256
```

Run auxiliary metrics.

```bash
python scripts/run_metrics_batch.py --config configs/experiments_dyref_v2_e20_256.csv
python scripts/summarize_metrics.py
```

The metric scripts expect normalized Stage-1 and refined videos to exist at the paths specified in the selected config CSV.

## Reproducibility Notes

- The repository contains code and tabular experiment summaries.
- Generated videos and model checkpoints are not committed because they are large artifacts.
- VEnhancer n30 is used as a pseudo visual target, not as ground truth.
- Flow EPE and Flow magnitude ratio are auxiliary indicators of deviation from the Stage-1 motion pattern, not proof of physical correctness.
- The reported experiment is an initial validation on 3 scenes. Broader claims require more scenes, stronger physical benchmarks, and user preference evaluation.

## Main Files

```text
model_head_prototype/dyref_head_v2.py
model_head_prototype/losses_v2.py
model_head_prototype/train_dyref_v2.py
model_head_prototype/export_dyref_v2_outputs.py
model_head_prototype/video_dataset.py
scripts/run_metrics_batch.py
scripts/summarize_metrics.py
scripts/flow_preservation_metric.py
scripts/video_quality_proxy.py
```

## References

1. W. Liu et al., "RealWonder: Real-Time Physical Action-Conditioned Video Generation," arXiv:2603.05449, 2026.
2. J. He et al., "VEnhancer: Generative Space-Time Enhancement for Video Generation," arXiv:2407.07667, 2024.
3. Z. Huang et al., "VBench: Comprehensive Benchmark Suite for Video Generative Models," CVPR, 2024.
4. S. Baker et al., "A Database and Evaluation Methodology for Optical Flow," IJCV, 2011.
5. G. Farneback, "Two-Frame Motion Estimation Based on Polynomial Expansion," Image Analysis, 2003.
