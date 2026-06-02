# Frozen I2V Backbone + DyRefHead 연구 진행 요약

이 문서는 현재까지 진행한 DyRefHead proof-of-concept 연구의 코드 구성, 실험 흐름, 주요 결과, 해석을 GitHub 공유용으로 정리한 것이다.

## 1. 연구 목표

본 연구의 목표는 frozen I2V backbone의 Stage-1 출력을 그대로 활용하면서, 그 뒤에 trainable output refinement head를 붙여 시각적 품질을 개선할 수 있는지 확인하는 것이다.

핵심 framing은 다음과 같다.

- Stage-1 video는 physics-induced motion prior로 사용한다.
- Stage-1 video는 physical ground truth가 아니다.
- VEnhancer n30 결과는 pseudo visual target으로 사용한다.
- VEnhancer n30 역시 ground-truth video가 아니다.
- DyRefHead는 frozen I2V backbone 뒤에 붙는 video-space output refinement head이다.
- 목표는 true physical correctness가 아니라, visual gain과 Stage-1 dynamics drift 사이의 trade-off를 확인하는 proof-of-concept이다.

## 2. 작업 디렉토리

프로젝트 경로:

```text
/root/realwonder_test/i2v_v2v_physics
```

주요 prototype 코드 경로:

```text
/root/realwonder_test/i2v_v2v_physics/model_head_prototype
```

RealWonder 원본 경로는 수정하지 않았다.

```text
/root/realwonder_test/RealWonder
```

## 3. 사용한 입력 데이터

기존에 생성되어 있던 normalized video pair를 사용했다.

Stage-1 입력:

```text
outputs/normalized/stage1/scene01_seed0.mp4
outputs/normalized/stage1/scene02_seed0.mp4
outputs/normalized/stage1/scene03_seed0.mp4
```

VEnhancer n30 pseudo visual target:

```text
outputs/normalized/v2v/venhancer_n30/scene01_seed0.mp4
outputs/normalized/v2v/venhancer_n30/scene02_seed0.mp4
outputs/normalized/v2v/venhancer_n30/scene03_seed0.mp4
```

총 3개 scene pair를 사용했다.

## 4. 코드 구성

### 4.1 Dataset

파일:

```text
model_head_prototype/video_dataset.py
```

역할:

- Stage-1 video와 VEnhancer n30 video를 pair로 로드한다.
- tensor shape은 `C, T, H, W`이다.
- pixel 값은 `0~1` 범위로 normalize한다.
- `train_size`, `max_frames` 옵션을 지원한다.
- `PairedVideoDataset` 클래스를 제공한다.

대표 출력 shape:

```text
sample_input_shape=(3, 32, 128, 128)
sample_target_shape=(3, 32, 128, 128)
batch_input_shape=(1, 3, 32, 128, 128)
```

### 4.2 DyRefHead v1

파일:

```text
model_head_prototype/dyref_head.py
model_head_prototype/losses.py
model_head_prototype/train_dyref_overfit.py
model_head_prototype/export_dyref_outputs.py
model_head_prototype/check_data_and_one_step.py
```

역할:

- 가장 초기 random tensor prototype을 실제 paired video overfit 실험으로 확장했다.
- 128x128, 32 frames 기준으로 Stage-1 input에서 VEnhancer n30 pseudo-target으로 학습했다.
- loss는 다음을 사용했다.
  - visual L1
  - temporal smoothness
  - first-frame identity

v1/e10은 dynamics drift는 VEnhancer보다 낮췄지만, Stage-1 대비 sharpness 개선에는 실패했다.

### 4.3 DyRefHead v2

파일:

```text
model_head_prototype/dyref_head_v2.py
model_head_prototype/losses_v2.py
model_head_prototype/train_dyref_v2.py
model_head_prototype/check_dyref_v2_one_step.py
model_head_prototype/export_dyref_v2_outputs.py
```

v2 변경점:

- 더 큰 3D convolution head 사용
- default channels: `48`
- default num_blocks: `6`
- GroupNorm 사용
- residual update:

```text
output = clamp(input + residual_scale * residual, 0, 1)
```

기본 `residual_scale=0.5`.

v2 loss:

```text
visual_l1_loss
spatial_gradient_loss
temporal_delta_preservation_loss
identity_first_frame_loss
```

기본 loss weight:

```text
lambda_visual = 1.0
lambda_edge = 0.5
lambda_temporal_delta = 0.2
lambda_identity = 0.05
```

`temporal_delta_preservation_loss`는 optical flow를 직접 계산하지 않고, Stage-1과 refined output의 frame-to-frame delta를 비교하는 lightweight dynamics preservation proxy이다.

### 4.4 DyRefHead v3

v3는 구조 변경이 아니라 loss-weight ablation이다.

사용 weight:

```text
lambda_visual = 1.0
lambda_edge = 0.75
lambda_temporal_delta = 0.15
lambda_identity = 0.05
```

목표:

- edge/detail learning을 더 강하게 주면 visual gain이 더 올라가는지 확인
- 동시에 dynamics drift가 VEnhancer n30보다 낮게 유지되는지 확인

## 5. 실험 실행 요약

### 5.1 One-step check

v1 one-step:

```bash
conda run -n realwonder python model_head_prototype/check_data_and_one_step.py
```

결과:

```text
dataset_size=3
batch_input_shape=(1, 3, 32, 128, 128)
batch_target_shape=(1, 3, 32, 128, 128)
backward_ok=True
```

v2 one-step:

```bash
conda run -n realwonder python model_head_prototype/check_dyref_v2_one_step.py
```

결과:

```text
dataset_size=3
input_shape=(1, 3, 64, 256, 256)
target_shape=(1, 3, 64, 256, 256)
output_shape=(1, 3, 64, 256, 256)
backward_ok=True
cuda_peak_allocated ~= 30.989 GB
```

### 5.2 v1/e10 128x128

학습:

```bash
conda run -n realwonder python model_head_prototype/train_dyref_overfit.py \
  --epochs 10 \
  --train_size 128 \
  --max_frames 32 \
  --lr 1e-4 \
  --batch_size 1 \
  --out_ckpt model_head_prototype/checkpoints/dyref_overfit_e10.pt \
  --log_csv model_head_prototype/logs/train_dyref_overfit_e10.csv
```

결과:

```text
initial loss_total = 0.0273867
final loss_total   = 0.0204521
NaN 없음
```

해석:

- loss는 감소했다.
- VEnhancer n30보다 flow drift는 낮았지만 Stage-1 대비 sharpness를 개선하지 못했다.
- 이 결과가 v2 실험의 동기가 되었다.

### 5.3 v2/e20 256x256

학습:

```bash
conda run -n realwonder python model_head_prototype/train_dyref_v2.py \
  --epochs 20 \
  --train_size 256 \
  --max_frames 64 \
  --lr 1e-4 \
  --batch_size 1 \
  --channels 48 \
  --num_blocks 6 \
  --residual_scale 0.5 \
  --out_ckpt model_head_prototype/checkpoints/dyref_v2_e20_256.pt \
  --log_csv model_head_prototype/logs/train_dyref_v2_e20_256.csv
```

결과:

```text
initial loss_total = 0.047640
final loss_total   = 0.031279
initial loss_edge  = 0.025075
final loss_edge    = 0.023898
NaN 없음
cuda_peak_allocated ~= 30.995 GB
```

export:

```bash
conda run -n realwonder python model_head_prototype/export_dyref_v2_outputs.py \
  --ckpt model_head_prototype/checkpoints/dyref_v2_e20_256.pt \
  --train_size 256 \
  --max_frames 64 \
  --output_dir outputs/v2v/dyref_head_v2_e20_256 \
  --fps 16
```

출력:

```text
outputs/v2v/dyref_head_v2_e20_256/scene01_seed0.mp4
outputs/v2v/dyref_head_v2_e20_256/scene02_seed0.mp4
outputs/v2v/dyref_head_v2_e20_256/scene03_seed0.mp4
```

### 5.4 v3/e20 256x256

학습:

```bash
conda run -n realwonder python model_head_prototype/train_dyref_v2.py \
  --epochs 20 \
  --train_size 256 \
  --max_frames 64 \
  --lr 1e-4 \
  --batch_size 1 \
  --channels 48 \
  --num_blocks 6 \
  --residual_scale 0.5 \
  --lambda_visual 1.0 \
  --lambda_edge 0.75 \
  --lambda_temporal_delta 0.15 \
  --lambda_identity 0.05 \
  --out_ckpt model_head_prototype/checkpoints/dyref_v3_edge075_temp015_e20_256.pt \
  --log_csv model_head_prototype/logs/train_dyref_v3_edge075_temp015_e20_256.csv
```

결과:

```text
initial loss_total = 0.053712
final loss_total   = 0.035942
initial loss_edge  = 0.025069
final loss_edge    = 0.023669
NaN 없음
cuda_peak_allocated ~= 30.995 GB
```

export:

```bash
conda run -n realwonder python model_head_prototype/export_dyref_v2_outputs.py \
  --ckpt model_head_prototype/checkpoints/dyref_v3_edge075_temp015_e20_256.pt \
  --train_size 256 \
  --max_frames 64 \
  --output_dir outputs/v2v/dyref_head_v3_edge075_temp015_e20_256 \
  --fps 16 \
  --channels 48 \
  --num_blocks 6 \
  --residual_scale 0.5
```

출력:

```text
outputs/v2v/dyref_head_v3_edge075_temp015_e20_256/scene01_seed0.mp4
outputs/v2v/dyref_head_v3_edge075_temp015_e20_256/scene02_seed0.mp4
outputs/v2v/dyref_head_v3_edge075_temp015_e20_256/scene03_seed0.mp4
```

## 6. 평가 구성

평가는 모두 256x256, 16fps, 4초 normalized video 기준으로 수행했다.

사용 config:

```text
configs/experiments_dyref_v3_256.csv
```

평가 대상 method:

```text
stage1_baseline
venhancer_n30
dyref_head_v2_e20_256
dyref_head_v3_edge075_temp015_e20_256
```

평가 metric:

- `mean_sharpness`
- `mean_flow_epe`
- `flow_mag_ratio`
- `mean_frame_diff`

결과 저장:

```text
metrics/dyref_head_v3_edge075_temp015_e20_256/summary_by_method.csv
metrics/dyref_head_v3_edge075_temp015_e20_256/summary_detail.csv
```

최종 paper-ready 복사본:

```text
metrics/final_dyref_paper_ready/
```

## 7. 핵심 정량 결과

256x256 평가의 method 평균값은 다음과 같다.

| method | mean_flow_epe | flow_mag_ratio | mean_sharpness |
|---|---:|---:|---:|
| stage1_baseline | 0.0000 | 1.0000 | 279.5409 |
| venhancer_n30 | 0.2782 | 3.4906 | 364.3567 |
| dyref_head_v2_e20_256 | 0.1883 | 1.6971 | 299.5439 |
| dyref_head_v3_edge075_temp015_e20_256 | 0.1901 | 1.5899 | 287.8850 |

## 8. 결과 해석

### 8.1 Stage-1 baseline

Stage-1 baseline은 frozen I2V backbone output이며, 본 연구에서 motion prior로 사용했다.

```text
mean_flow_epe=0.0000
flow_mag_ratio=1.0000
mean_sharpness=279.5409
```

Stage-1은 자기 자신과 비교되므로 flow drift proxy가 0이다.

### 8.2 VEnhancer n30

VEnhancer n30은 가장 높은 sharpness를 보였다.

```text
mean_sharpness=364.3567
```

하지만 Stage-1 대비 drift proxy도 가장 컸다.

```text
mean_flow_epe=0.2782
flow_mag_ratio=3.4906
```

따라서 VEnhancer n30은 pseudo visual target으로는 유용하지만, Stage-1 dynamics preservation 측면에서는 drift가 크다.

### 8.3 DyRefHead v2

v2는 대표 제안 결과로 선택했다.

```text
mean_sharpness=299.5439
mean_flow_epe=0.1883
flow_mag_ratio=1.6971
```

해석:

- Stage-1보다 sharpness가 개선됐다.
- VEnhancer n30보다 flow EPE가 낮다.
- VEnhancer n30보다 flow_mag_ratio가 1에 가깝다.
- visual gain과 dynamics drift 사이에서 가장 균형 잡힌 결과다.

### 8.4 DyRefHead v3

v3는 loss-weight ablation이다.

```text
mean_sharpness=287.8850
mean_flow_epe=0.1901
flow_mag_ratio=1.5899
```

해석:

- Stage-1보다 sharpness는 높다.
- VEnhancer n30보다 flow drift proxy는 낮다.
- v2보다 flow_mag_ratio는 더 안정적이다.
- 하지만 v2보다 sharpness가 낮고 mean_flow_epe도 약간 높다.

따라서 v3는 대표 방법이라기보다, dynamics magnitude stabilization을 강화하면 visual gain이 약해질 수 있음을 보여주는 ablation으로 보는 것이 적절하다.

## 9. 대표 결과 선택

대표 proposed result:

```text
dyref_head_v2_e20_256
```

이유:

- Stage-1 대비 sharpness 개선을 보인다.
- VEnhancer n30 대비 flow drift proxy를 줄인다.
- v3보다 visual gain이 높다.
- VEnhancer n30보다 dynamics drift가 낮은 상태에서 적절한 visual improvement를 제공한다.

Ablation:

```text
dyref_head_v3_edge075_temp015_e20_256
```

이유:

- v3는 flow_mag_ratio 측면에서는 v2보다 안정적이다.
- 하지만 sharpness가 v2보다 낮다.
- 이 결과는 visual gain-dynamics drift trade-off를 보여주는 ablation으로 적합하다.

## 10. Paper-ready 산출물

최종 정리 폴더:

```text
metrics/final_dyref_paper_ready/
```

포함 파일:

```text
abstract_final_candidate.md
claim_safety_final.md
contribution_final.md
dyref_head_v2.py
dyref_v2_v3_comparison.md
figure_caption_candidates.md
losses_v2.py
paper_outline_final.md
results_interpretation.md
scene01_stage1_venhancer_v2_v3.jpg
scene02_stage1_venhancer_v2_v3.jpg
scene03_stage1_venhancer_v2_v3.jpg
summary_by_method.csv
summary_detail.csv
table_main_results.md
train_dyref_v2.py
```

## 11. Claim Safety

사용 가능한 표현:

- frozen I2V backbone
- trainable output refinement head
- physics-induced motion prior
- Stage-1 dynamics preservation
- pseudo visual target
- lightweight dynamics proxy
- visual gain-dynamics drift trade-off
- proof-of-concept

피해야 할 표현:

- physical ground truth
- true physical correctness
- perfect preservation
- globally optimal
- complete model
- guaranteed physics

본 연구는 true physical correctness를 보장하는 모델이 아니라, Stage-1 dynamics prior를 활용한 output-space refinement의 가능성을 보여주는 proof-of-concept이다.

## 12. 다음 단계 제안

현재 기준에서는 바로 50 epoch를 늘리는 것보다, v2를 대표 결과로 삼아 paper-ready proof-of-concept를 정리하는 것이 적절하다.

추가 실험을 한다면 다음 중 하나가 합리적이다.

1. v2 weight를 유지하고 scene 수를 늘려 robustness 확인
2. perceptual/detail proxy를 추가해 VEnhancer와의 visual gap 축소
3. temporal-delta loss를 유지한 채 더 명시적인 trajectory/flow cache 기반 preservation loss 추가
4. qualitative human review template 작성

단, 현재 결과만으로 true physical correctness나 완전한 dynamics preservation을 주장해서는 안 된다.
