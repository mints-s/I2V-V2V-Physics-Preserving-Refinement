# Reproducible Code Guide: I2V/V2V Physics-Preserving Refinement

이 문서는 이번 실험 코드를 GitHub에 공개 가능한 형태로 정리하기 위한 섹터별 가이드입니다. 목표는 다음 세 가지입니다.

1. 구현 가능함을 코드 단위로 보여준다.
2. 외부 사용자가 최소한의 수정으로 실험 흐름을 재현할 수 있게 한다.
3. 대용량 산출물, 외부 모델, 로컬 경로 의존성을 공개 저장소에서 분리한다.

현재 실험 루트는 다음 경로입니다.

```bash
cd /root/realwonder_test/i2v_v2v_physics
```

공개 저장소에 올릴 때는 이 디렉터리를 하나의 독립 프로젝트로 두거나, `RealWonder` 저장소 아래 `experiments/i2v_v2v_physics/` 같은 하위 디렉터리로 복사하는 방식을 권장합니다.

## 0. 실험 한 줄 요약

이 실험은 RealWonder가 만든 Stage-1 비디오를 `physics-induced motion prior`로 보고, V2V refinement가 시각 품질을 높이는 동안 Stage-1 dynamics를 얼마나 보존하는지 측정합니다.

중요한 전제:

- Stage-1 비디오는 실제 물리 ground truth가 아닙니다.
- 여기서 측정하는 것은 `true physical correctness`가 아니라 `Stage-1 dynamics preservation`입니다.
- VEnhancer sweep 결과는 trainable refinement head의 필요성을 보여주는 pilot evidence입니다.
- `model_head_prototype/`은 이 아이디어가 학습 가능한 PyTorch 모듈로 구현 가능함을 보여주는 최소 프로토타입입니다.

## 1. 공개용 디렉터리 구조

GitHub에는 아래처럼 정리하는 것을 권장합니다.

```text
i2v_v2v_physics/
├── README_EXPERIMENT.md
├── REPRODUCIBLE_CODE_GUIDE.md
├── NEXT_STEPS.md
├── configs/
│   ├── experiments.csv
│   ├── experiments_dyref_e10_128.csv
│   ├── experiments_dyref_v2_e20_256.csv
│   └── experiments_dyref_v3_256.csv
├── scripts/
│   ├── normalize_video.sh
│   ├── run_venhancer_param.sh
│   ├── run_metrics_batch.py
│   ├── flow_preservation_metric.py
│   ├── video_quality_proxy.py
│   ├── summarize_metrics.py
│   ├── make_contact_sheet.py
│   ├── select_tradeoff_candidate.py
│   └── smoke_test.sh
├── model_head_prototype/
│   ├── README.md
│   ├── dyref_head.py
│   ├── dyref_head_v2.py
│   ├── losses.py
│   ├── losses_v2.py
│   ├── video_dataset.py
│   ├── train_dyref_v2.py
│   ├── export_dyref_v2_outputs.py
│   ├── test_shapes.py
│   └── run_minimal_dyref_experiment.sh
├── metrics/
│   ├── summary_detail.csv
│   ├── summary_by_method.csv
│   └── selected_tradeoff_candidate.txt
└── docs_or_assets/
    └── optional_small_figures_or_contact_sheets
```

대용량 비디오와 checkpoint는 Git에 직접 포함하지 않는 것이 좋습니다. 대신 `outputs/`, `data/`, `checkpoints/`, `logs/`는 `.gitignore`에 넣고, 필요한 샘플만 release asset, Hugging Face, Google Drive, Zenodo 등으로 분리합니다.

권장 `.gitignore` 항목:

```gitignore
outputs/
data/
logs/
*.mp4
*.mov
*.avi
*.pt
*.pth
*.ckpt
metrics_snapshot_after_n30.tar.gz
model_head_prototype/checkpoints/
```

## 2. 섹터 A: Stage-1 생성 코드

역할:

- RealWonder를 사용해 초기 I2V 비디오를 생성합니다.
- 이 출력은 이후 모든 V2V refinement의 motion prior로 사용됩니다.

관련 코드:

```text
/root/realwonder_test/RealWonder/
├── infer_sim.py
├── case_simulation.py
├── simulation/
├── vidgen/
└── demo_web/
```

실험 프로젝트에서 참조하는 Stage-1 산출물 위치:

```text
outputs/stage1/realwonder/scene01_seed0.mp4
outputs/stage1/realwonder/scene02_seed0.mp4
outputs/stage1/realwonder/scene03_seed0.mp4
```

공개 시 정리 방식:

- RealWonder 전체 소스가 별도 upstream repo라면 submodule 또는 설치 안내로 분리합니다.
- 이번 실험 저장소에는 Stage-1 생성 명령, 입력 scene 설명, 최종 Stage-1 비디오 링크만 둡니다.
- RealWonder 내부 checkpoint나 대용량 생성 결과는 Git에 포함하지 않습니다.

재현 절차 예시:

```bash
# RealWonder repo에서 Stage-1 생성 후, 결과를 실험 폴더로 복사
mkdir -p outputs/stage1/realwonder
cp /path/to/realwonder_scene01_seed0.mp4 outputs/stage1/realwonder/scene01_seed0.mp4
cp /path/to/realwonder_scene02_seed0.mp4 outputs/stage1/realwonder/scene02_seed0.mp4
cp /path/to/realwonder_scene03_seed0.mp4 outputs/stage1/realwonder/scene03_seed0.mp4
```

## 3. 섹터 B: V2V Refinement Sweep

역할:

- Stage-1 비디오에 VEnhancer 또는 다른 V2V refinement를 적용합니다.
- `noise_aug` 같은 VEnhancer parameter를 바꾸며 visual quality와 motion drift의 trade-off를 봅니다.

관련 코드:

```text
scripts/run_venhancer_param.sh
scripts/run_venhancer_vanilla.sh
```

현재 사용한 외부 repo:

```text
/root/realwonder_test/v2v_repos/VEnhancer
```

VEnhancer 실행 예시:

```bash
VENHANCER_ROOT=/root/realwonder_test/v2v_repos/VEnhancer \
VENHANCER_PYTHON=/root/miniconda3/envs/venhancer/bin/python \
bash scripts/run_venhancer_param.sh \
  outputs/normalized/stage1/scene01_seed0.mp4 \
  outputs/v2v/venhancer_n30/scene01_seed0.mp4 \
  "a high quality physically plausible video with stable motion" \
  30 24 15
```

출력 규칙:

```text
outputs/v2v/venhancer_n30/scene01_seed0.mp4
outputs/v2v/venhancer_n50/scene01_seed0.mp4
outputs/v2v/venhancer_n100/scene01_seed0.mp4
outputs/v2v/venhancer_n200/scene01_seed0.mp4
```

공개 시 정리 방식:

- `scripts/run_venhancer_param.sh`는 포함합니다.
- VEnhancer 원본 repo는 submodule, install guide, citation으로 분리합니다.
- 생성된 `.mp4`는 Git에 직접 올리지 말고 외부 asset 링크로 제공합니다.

## 4. 섹터 C: Video Normalization

역할:

- Stage-1과 refined 비디오의 fps, 해상도, 길이를 동일하게 맞춥니다.
- metric 비교 전에 반드시 실행해야 합니다.

관련 코드:

```text
scripts/normalize_video.sh
```

재현 명령:

```bash
bash scripts/normalize_video.sh \
  outputs/stage1/realwonder/scene01_seed0.mp4 \
  outputs/normalized/stage1/scene01_seed0.mp4 \
  16 512 512 4

bash scripts/normalize_video.sh \
  outputs/v2v/venhancer_n30/scene01_seed0.mp4 \
  outputs/normalized/v2v/venhancer_n30/scene01_seed0.mp4 \
  16 512 512 4
```

출력 규칙:

```text
outputs/normalized/stage1/{scene}_seed{seed}.mp4
outputs/normalized/v2v/{method}/{scene}_seed{seed}.mp4
```

재현성 메모:

- 현재 metric config는 normalized video를 기준으로 동작합니다.
- `16 512 512 4`는 `fps width height duration_seconds` 순서입니다.
- 모든 비교 대상은 같은 normalization rule을 적용해야 합니다.

## 5. 섹터 D: Metric Pipeline

역할:

- Stage-1과 refined 비디오의 optical-flow 기반 dynamics drift를 측정합니다.
- refined 비디오의 sharpness/frame-difference proxy를 계산합니다.
- scene, seed, method별 결과를 요약합니다.

관련 코드:

```text
scripts/run_metrics_batch.py
scripts/flow_preservation_metric.py
scripts/video_quality_proxy.py
scripts/summarize_metrics.py
configs/experiments.csv
```

환경:

```bash
conda create -n eval_video python=3.10 -y
conda activate eval_video
pip install opencv-python numpy pandas matplotlib tqdm imageio imageio-ffmpeg scikit-image
```

Smoke test:

```bash
bash scripts/smoke_test.sh
```

실험 batch 실행:

```bash
python scripts/run_metrics_batch.py --config configs/experiments.csv
python scripts/summarize_metrics.py
```

출력:

```text
metrics/{scene}_seed{seed}_{method}_flow.csv
metrics/{scene}_seed{seed}_{method}_quality.csv
metrics/summary_detail.csv
metrics/summary_by_method.csv
```

현재 `configs/experiments.csv`는 `stage1_baseline`과 `venhancer_n30` 비교를 포함합니다.

```csv
scene,seed,stage1_video,v2v_method,refined_video
scene01,0,outputs/normalized/stage1/scene01_seed0.mp4,stage1_baseline,outputs/normalized/stage1/scene01_seed0.mp4
scene01,0,outputs/normalized/stage1/scene01_seed0.mp4,venhancer_n30,outputs/normalized/v2v/venhancer_n30/scene01_seed0.mp4
scene02,0,outputs/normalized/stage1/scene02_seed0.mp4,stage1_baseline,outputs/normalized/stage1/scene02_seed0.mp4
scene02,0,outputs/normalized/stage1/scene02_seed0.mp4,venhancer_n30,outputs/normalized/v2v/venhancer_n30/scene02_seed0.mp4
scene03,0,outputs/normalized/stage1/scene03_seed0.mp4,stage1_baseline,outputs/normalized/stage1/scene03_seed0.mp4
scene03,0,outputs/normalized/stage1/scene03_seed0.mp4,venhancer_n30,outputs/normalized/v2v/venhancer_n30/scene03_seed0.mp4
```

Metric 해석:

- `mean_flow_epe`: 낮을수록 Stage-1 dynamics 보존이 좋습니다.
- `median_flow_epe`: outlier에 덜 민감한 flow drift입니다.
- `flow_mag_ratio`: 1에 가까울수록 motion magnitude가 Stage-1과 유사합니다.
- `mean_sharpness`: 높을수록 detail proxy가 커지지만 artifact도 함께 커질 수 있습니다.
- `mean_frame_diff`: frame-to-frame 변화량 proxy입니다.

현재 요약 결과:

| method | mean_flow_epe_mean | flow_mag_ratio_mean | mean_sharpness_mean | mean_frame_diff_mean |
|---|---:|---:|---:|---:|
| stage1_baseline | 0.0000 | 1.0000 | 198.99 | 1.4273 |
| venhancer_n30 | 0.2796 | 4.6502 | 559.55 | 1.6787 |

해석:

- VEnhancer n30은 sharpness proxy를 크게 올립니다.
- 동시에 optical-flow 기준 Stage-1 dynamics에서 drift가 생깁니다.
- 이 trade-off가 dynamics-preserving refinement head의 필요성을 뒷받침합니다.

## 6. 섹터 E: Qualitative Review와 Contact Sheet

역할:

- 숫자 metric만으로 설명하기 어려운 visual artifact, motion drift, temporal inconsistency를 시각적으로 확인합니다.

관련 코드:

```text
scripts/make_contact_sheet.py
scripts/select_tradeoff_candidate.py
metrics/selected_tradeoff_candidate.txt
qualitative_review/
```

Contact sheet 예시 산출물:

```text
metrics/scene01_stage1_vs_selected_contact_sheet.jpg
metrics/scene01_venhancer_sweep_contact_sheet.jpg
metrics/scene01_venhancer_fine_sweep_contact_sheet.jpg
```

공개 시 정리 방식:

- 논문/README에 들어갈 작은 contact sheet만 `assets/` 또는 `docs/assets/`에 포함합니다.
- 원본 비디오는 외부 링크로 분리합니다.
- qualitative review는 표 형태로 `qualitative_review/README.md`를 두면 좋습니다.

권장 review table:

```markdown
| scene | method | visual detail | motion preservation | artifact | note |
|---|---|---:|---:|---|---|
| scene01 | stage1_baseline | low | high | none | reference prior |
| scene01 | venhancer_n30 | high | medium | detail flicker | better texture, motion drift |
```

## 7. 섹터 F: DyRef Model Head Prototype

역할:

- 단순한 post-processing 실험을 넘어서, 학습 가능한 dynamics-preserving refinement head를 구현할 수 있음을 보여줍니다.
- Frozen I2V backbone output `V0` 위에 residual head `H_ref`를 붙여 `V_hat = V0 + H_ref(V0)` 형태로 refinement합니다.

관련 코드:

```text
model_head_prototype/
├── dyref_head.py
├── dyref_head_v2.py
├── losses.py
├── losses_v2.py
├── video_dataset.py
├── train_dyref_v2.py
├── export_dyref_v2_outputs.py
├── check_dyref_v2_one_step.py
├── test_shapes.py
└── run_minimal_dyref_experiment.sh
```

핵심 수식:

```text
V_hat = V0 + H_ref(V0)

L_total = L_visual
        + lambda_flow * L_flow
        + lambda_temp * L_temporal
        + lambda_id * L_identity
```

최소 shape test:

```bash
cd model_head_prototype
python test_shapes.py
```

최소 학습/내보내기 흐름:

```bash
cd model_head_prototype
bash run_minimal_dyref_experiment.sh
```

공개 시 정리 방식:

- `model_head_prototype/*.py`는 반드시 포함합니다.
- `model_head_prototype/checkpoints/*.pt`는 Git에 올리지 않습니다.
- checkpoint를 공유해야 한다면 release asset 또는 external model hub 링크를 사용합니다.
- README에는 이 코드가 full production model이 아니라 proof-of-implementation prototype임을 명시합니다.

## 8. 섹터 G: Experiment Configs

역할:

- 같은 metric pipeline으로 서로 다른 method, resolution, model version을 비교할 수 있게 합니다.

관련 파일:

```text
configs/experiments.csv
configs/experiments_dyref_e10_128.csv
configs/experiments_dyref_v2_e20_256.csv
configs/experiments_dyref_v3_256.csv
```

권장 naming:

```text
stage1_baseline
vanilla
flowguided
venhancer_n30
venhancer_n50
venhancer_n100
dyref_head_e10
dyref_head_v2_e20_256
dyref_head_v3_edge075_temp015_e20_256
```

새 method를 추가하는 방법:

```csv
scene,seed,stage1_video,v2v_method,refined_video
scene01,0,outputs/normalized/stage1/scene01_seed0.mp4,new_method,outputs/normalized/v2v/new_method/scene01_seed0.mp4
```

실행:

```bash
python scripts/run_metrics_batch.py --config configs/experiments_new_method.csv
python scripts/summarize_metrics.py
```

주의:

- `summarize_metrics.py`는 기본적으로 `configs/experiments.csv`에 있는 method만 요약합니다.
- 다른 config를 기준으로 요약하려면 공개 전 `summarize_metrics.py`에 `--config` 인자를 추가하거나, 평가할 config를 `configs/experiments.csv`로 복사해 사용합니다.

## 9. End-to-End Reproduction

외부 사용자가 따라 할 수 있는 최소 재현 순서는 아래와 같습니다.

```bash
# 1. 환경 생성
conda create -n eval_video python=3.10 -y
conda activate eval_video
pip install opencv-python numpy pandas matplotlib tqdm imageio imageio-ffmpeg scikit-image

# 2. 실험 루트로 이동
cd i2v_v2v_physics

# 3. Stage-1와 V2V 결과 비디오 배치
mkdir -p outputs/stage1/realwonder
mkdir -p outputs/v2v/venhancer_n30

# 4. 같은 format으로 normalize
bash scripts/normalize_video.sh outputs/stage1/realwonder/scene01_seed0.mp4 outputs/normalized/stage1/scene01_seed0.mp4 16 512 512 4
bash scripts/normalize_video.sh outputs/v2v/venhancer_n30/scene01_seed0.mp4 outputs/normalized/v2v/venhancer_n30/scene01_seed0.mp4 16 512 512 4

# 5. config 확인 후 metric 실행
python scripts/run_metrics_batch.py --config configs/experiments.csv
python scripts/summarize_metrics.py

# 6. 결과 확인
cat metrics/summary_detail.csv
cat metrics/summary_by_method.csv
```

전체 재현에는 Stage-1 생성용 RealWonder, V2V refinement용 VEnhancer, 그리고 각 모델 checkpoint가 필요합니다. GitHub 본문에는 install guide와 asset 링크를 명시하고, 대용량 파일은 저장소 밖에서 제공합니다.

## 10. GitHub 공개 전 체크리스트

코드 정리:

- [ ] `README_EXPERIMENT.md`를 프로젝트 첫 화면용 README로 다듬기
- [ ] `REPRODUCIBLE_CODE_GUIDE.md`를 README에서 링크하기
- [ ] 모든 absolute local path를 환경변수 또는 relative path로 바꾸기
- [ ] `configs/experiments.csv`가 실제 공개 샘플과 일치하는지 확인하기
- [ ] `scripts/smoke_test.sh`가 fresh clone에서 통과하는지 확인하기

데이터/산출물 정리:

- [ ] `.mp4`, checkpoint, log, tarball을 Git에서 제외하기
- [ ] 공개 가능한 작은 contact sheet만 `assets/`에 포함하기
- [ ] 원본/생성 비디오 다운로드 링크를 README에 넣기
- [ ] Stage-1, V2V, metric result의 라이선스와 출처 명시하기

재현성:

- [ ] conda environment 또는 `requirements.txt` 추가하기
- [ ] VEnhancer, RealWonder dependency 설치 절차를 분리해 쓰기
- [ ] `smoke_test.sh` 실행 결과를 README에 기록하기
- [ ] `summary_by_method.csv`의 주요 숫자를 README 표로 복사하기

논문/프로젝트 설명:

- [ ] Stage-1은 physical ground truth가 아니라 motion prior임을 명시하기
- [ ] flow metric의 한계와 qualitative review 필요성을 명시하기
- [ ] VEnhancer sweep은 pilot evidence이고 DyRef head는 trainable prototype임을 구분하기
- [ ] future work에 true physics validation, human study, larger scene set을 추가하기

## 11. 추천 README 구성

GitHub 첫 화면 README는 아래 순서가 가장 읽기 쉽습니다.

```markdown
# Dynamics-Preserving Video Refinement for I2V Outputs

## Overview
## Key Idea
## Repository Structure
## Quick Start
## Reproduce Metrics
## Model Head Prototype
## Current Results
## Limitations
## Citation and Acknowledgements
```

`Current Results`에는 아래 표를 넣으면 이번 실험의 메시지가 바로 보입니다.

| method | dynamics drift lower is better | motion magnitude ratio | detail proxy higher is better |
|---|---:|---:|---:|
| stage1_baseline | 0.0000 | 1.0000 | 198.99 |
| venhancer_n30 | 0.2796 | 4.6502 | 559.55 |

짧은 해석:

> V2V enhancement improves visual detail proxies but changes the Stage-1 motion prior. This motivates a trainable residual refinement head with explicit dynamics-preserving losses.

## 12. 현재 구현 가능성을 보여주는 핵심 파일

GitHub에서 가장 먼저 보여줘야 할 파일은 아래입니다.

```text
README_EXPERIMENT.md
REPRODUCIBLE_CODE_GUIDE.md
scripts/run_metrics_batch.py
scripts/flow_preservation_metric.py
scripts/video_quality_proxy.py
scripts/summarize_metrics.py
scripts/run_venhancer_param.sh
model_head_prototype/dyref_head_v2.py
model_head_prototype/losses_v2.py
model_head_prototype/train_dyref_v2.py
model_head_prototype/export_dyref_v2_outputs.py
configs/experiments.csv
metrics/summary_by_method.csv
```

이 조합이면 외부 독자가 다음을 확인할 수 있습니다.

- Stage-1 prior와 V2V refinement를 분리해서 평가한다.
- flow preservation과 visual proxy를 자동 계산한다.
- pilot sweep 결과에서 trade-off가 관찰된다.
- 같은 문제를 해결하기 위한 trainable DyRef head prototype이 구현되어 있다.
