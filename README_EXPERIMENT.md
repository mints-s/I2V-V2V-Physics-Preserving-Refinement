# I2V/V2V Physics Preservation Experiment

## 연구 목표

이 실험 scaffold는 두 단계 비디오 파이프라인을 가볍게 평가하기 위한 별도 프로젝트입니다.

1. Stage 1: RealWonder가 생성한 비디오를 physics-induced motion prior로 사용합니다.
2. Stage 2: 다른 저장소 또는 수동 작업으로 만든 V2V refinement 결과를 적용합니다.
3. Evaluation: Stage-1 비디오와 V2V-refined 비디오를 비교해 시각적 개선 이후 Stage-1 dynamics가 얼마나 보존되는지 측정합니다.

이 프로젝트는 `/root/realwonder_test/i2v_v2v_physics`에 위치하며, RealWonder 저장소는 외부 Stage-1 generator source로만 취급합니다.

## 디렉터리 구조

```text
i2v_v2v_physics/
├── data/scenes/
│   ├── scene01/
│   ├── scene02/
│   └── scene03/
├── outputs/
│   ├── stage1/
│   ├── v2v/
│   │   ├── vanilla/
│   │   └── flowguided/
│   └── normalized/
│       ├── stage1/
│       └── v2v/
│           ├── vanilla/
│           └── flowguided/
├── metrics/
├── scripts/
├── configs/
├── logs/
└── README_EXPERIMENT.md
```

## RealWonder 출력의 의미

RealWonder 출력은 이 실험에서 Stage-1 dynamics로 사용됩니다. 그러나 이것은 물리적 ground truth가 아닙니다. 즉, RealWonder의 움직임이 실제 물리 법칙을 정확히 만족한다고 가정하지 않습니다. 여기서 측정하는 것은 V2V refinement가 Stage-1에서 주어진 움직임 패턴을 얼마나 유지했는지이며, true physical correctness를 검증하는 것은 아닙니다.

## 환경 권장

평가 코드는 RealWonder 실행 환경과 분리된 `eval_video` 환경에서 실행하는 것을 권장합니다. RealWonder 환경은 Stage-1 생성용으로 그대로 두고, 이 프로젝트는 metrics 계산만 담당하게 분리합니다.

```bash
conda create -n eval_video python=3.10 -y
conda activate eval_video
pip install opencv-python numpy pandas matplotlib tqdm imageio imageio-ffmpeg scikit-image
```

## Smoke Test

동일한 Stage-1 비디오를 vanilla 및 flow-guided refined 결과로 복사해 전체 metric pipeline을 테스트합니다. Stage-1과 refined 비디오가 동일하면 flow EPE는 0에 가까워야 합니다.

```bash
bash scripts/smoke_test.sh
```

## 실제 비디오 배치 방법

RealWonder에서 생성한 Stage-1 비디오는 원본 보관용으로 다음 위치에 복사합니다. RealWonder 저장소 안의 파일은 이동하거나 수정하지 않습니다.

```text
outputs/stage1/realwonder/scene01_seed0.mp4
outputs/stage1/realwonder/scene02_seed0.mp4
outputs/stage1/realwonder/scene03_seed0.mp4
```

vanilla V2V 결과는 다음 위치에 둡니다.

```text
outputs/v2v/vanilla/scene01_seed0.mp4
outputs/v2v/vanilla/scene01_seed1.mp4
outputs/v2v/vanilla/scene02_seed0.mp4
outputs/v2v/vanilla/scene02_seed1.mp4
outputs/v2v/vanilla/scene03_seed0.mp4
outputs/v2v/vanilla/scene03_seed1.mp4
```

flow-guided V2V 결과는 다음 위치에 둡니다.

```text
outputs/v2v/flowguided/scene01_seed0.mp4
outputs/v2v/flowguided/scene01_seed1.mp4
outputs/v2v/flowguided/scene02_seed0.mp4
outputs/v2v/flowguided/scene02_seed1.mp4
outputs/v2v/flowguided/scene03_seed0.mp4
outputs/v2v/flowguided/scene03_seed1.mp4
```

입력 비디오의 fps, 해상도, 길이를 맞추려면 다음 스크립트를 사용합니다.

```bash
bash scripts/normalize_video.sh INPUT_VIDEO OUTPUT_VIDEO 16 512 512 4
```

정규화된 Stage-1 및 V2V 비디오는 metrics 입력으로 다음 위치에 둡니다.

```text
outputs/normalized/stage1/scene01_seed0.mp4
outputs/normalized/v2v/vanilla/scene01_seed0.mp4
outputs/normalized/v2v/flowguided/scene01_seed0.mp4
```

## Metrics 실행

`configs/experiments.csv`에 정의된 경로를 읽어서 존재하는 실험만 평가합니다. Stage-1 또는 refined 비디오가 없으면 해당 row는 건너뜁니다.

```bash
python scripts/run_metrics_batch.py
python scripts/summarize_metrics.py
```

결과는 `metrics/`에 저장됩니다.

```text
metrics/{scene}_seed{seed}_{method}_flow.csv
metrics/{scene}_seed{seed}_{method}_quality.csv
metrics/summary_detail.csv
metrics/summary_by_method.csv
```

## Metrics 해석

`mean_flow_epe`가 낮을수록 V2V-refined 비디오가 Stage-1 dynamics를 더 잘 보존했다는 뜻입니다.

`flow_mag_ratio`가 1에 가까울수록 motion magnitude가 Stage-1과 유사하게 유지되었다는 뜻입니다.

`mean_sharpness`가 높다는 사실만으로 더 좋은 비디오라고 판단할 수 없습니다. 과도한 sharpening artifact도 sharpness를 올릴 수 있습니다.

Flow preservation이 좋다는 것은 Stage-1 움직임이 보존되었다는 의미이지, true physical correctness를 의미하지 않습니다.

## 논문 프레이밍 제안

이 실험은 visual enhancement와 Stage-1 dynamics preservation 사이의 trade-off analysis로 프레이밍하는 것이 적절합니다. 즉, V2V refinement가 외형 품질을 개선하면서도 Stage-1에서 유도된 움직임을 얼마나 유지하는지 비교하는 평가입니다.
