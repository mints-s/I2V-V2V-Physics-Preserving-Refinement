# Frozen Image-to-Video Backbone의 시공간 품질 향상을 위한 동역학 보존 출력 정제 Head

## 1. 초록

본 논문은 physics-sensitive image-to-video(I2V) 생성에서 frozen I2V backbone의 출력을 보존하면서 시각적 품질을 개선하기 위한 trainable output refinement head를 제안한다. 기존 I2V 모델 전체를 다시 학습하는 대신, RealWonder Stage-1 출력을 physics-induced motion prior로 사용하고, 그 위에 비디오 공간 residual refinement module인 DyRefHead를 적용한다. DyRefHead는 Stage-1의 시간적 움직임 구조를 대체하기보다, 제한된 residual correction을 통해 출력 비디오의 시각적 품질을 보정하는 것을 목표로 한다.

학습에서는 VEnhancer n30 결과를 ground truth가 아닌 pseudo visual target으로 사용한다. 동시에 Stage-1 temporal delta와 first-frame identity를 보존하는 lightweight dynamics-aware objective를 사용하여, 시각적 개선이 Stage-1 dynamics prior에서 과도하게 벗어나지 않도록 제약한다. 본 연구는 optical flow를 학습 중 직접 계산하지 않고, video-space frame difference 기반의 경량 proxy를 사용한다.

3개 physics-sensitive I2V scene에 대한 256x256 평가에서 대표 결과인 DyRefHead v2는 Stage-1 baseline보다 sharpness proxy를 개선했다. Stage-1의 mean_sharpness는 279.5409이고 DyRefHead v2는 299.5439이다. 또한 DyRefHead v2는 VEnhancer n30보다 낮은 dynamics drift proxy를 보였다. VEnhancer n30의 mean_flow_epe와 flow_mag_ratio는 각각 0.2782, 3.4906인 반면, DyRefHead v2는 0.1883, 1.6971이다. 추가 ablation인 DyRefHead v3는 flow_mag_ratio를 1.5899로 더 안정화했지만 mean_sharpness가 287.8850으로 감소했다.

이 결과는 frozen I2V backbone 뒤에 trainable output refinement head를 붙이는 접근이 visual gain과 Stage-1 dynamics preservation 사이의 trade-off를 조절할 수 있음을 보여주는 proof-of-concept이다. 다만 Stage-1은 물리적 정답이 아니며, VEnhancer n30도 ground-truth video가 아니다. 따라서 본 논문은 true physical correctness나 perfect preservation을 주장하지 않는다.

## 2. 서론

Image-to-video 생성 모델은 입력 이미지로부터 시간적으로 일관된 장면 변화를 생성해야 한다. 특히 물체의 접촉, 이동, 변형, 관성적 움직임이 중요한 physics-sensitive scene에서는 단순히 선명한 프레임을 생성하는 것만으로 충분하지 않다. 비디오가 더 선명해지더라도 원래 생성된 움직임 구조가 크게 바뀌면, 사용자는 결과를 시각적으로는 개선되었지만 동역학적으로 불안정한 출력으로 인식할 수 있다.

기존의 off-the-shelf video enhancement 또는 video-to-video refinement 방법은 시각적 품질을 크게 개선할 수 있다. 본 연구에서 사용한 VEnhancer n30 역시 가장 높은 sharpness proxy를 보였다. 그러나 이러한 외부 refinement는 frozen I2V backbone이 만든 Stage-1 motion prior에서 더 크게 벗어날 수 있다. 실제로 VEnhancer n30은 mean_sharpness 364.3567을 기록했지만, mean_flow_epe 0.2782와 flow_mag_ratio 3.4906으로 가장 큰 dynamics drift proxy를 보였다.

본 연구는 이 문제를 해결하기 위한 작은 대안으로 DyRefHead를 제안한다. DyRefHead는 frozen I2V backbone의 출력 뒤에 붙는 trainable output refinement head이다. I2V backbone을 수정하거나 전체 모델을 다시 학습하지 않고, Stage-1 video를 입력으로 받아 같은 해상도의 residual correction을 예측한다. 이때 Stage-1은 physics-induced motion prior로 간주한다. 이는 물리적 ground truth가 아니라, frozen backbone이 이미 생성한 움직임 구조를 보존하기 위한 참조 신호이다.

본 논문의 기여는 세 가지다. 첫째, frozen I2V backbone과 trainable output refinement head를 결합한 video-space refinement 구조를 제시한다. 둘째, Stage-1 motion prior를 활용한 lightweight dynamics-aware objective를 설계한다. 셋째, visual gain과 dynamics drift를 함께 평가하여, output refinement head 설계에 trade-off가 존재함을 보인다.

## 3. 관련 연구

I2V 생성 연구는 입력 이미지의 장면 구조를 유지하면서 시간적 변화를 생성하는 방향으로 발전해 왔다. 최근 모델들은 대규모 비디오 데이터와 diffusion 또는 transformer 기반 구조를 활용하여 높은 시각적 품질을 달성하지만, 물리적 상호작용이 중요한 scene에서는 여전히 움직임 일관성과 물리적 해석 가능성이 문제가 된다.

Video enhancement 및 video-to-video refinement 연구는 기존 비디오의 sharpness, texture, temporal consistency를 개선하는 데 초점을 둔다. 이러한 방법은 후처리 단계에서 강력한 시각적 개선을 제공할 수 있지만, 입력 비디오의 motion structure를 보존한다는 보장이 항상 있는 것은 아니다. 본 연구에서 VEnhancer n30은 pseudo visual target이자 off-the-shelf refinement baseline으로 사용된다. 그러나 VEnhancer n30은 ground truth가 아니며, 물리적으로 올바른 target으로 간주하지 않는다.

Frozen backbone adaptation 연구는 대규모 pretrained model을 고정한 채 작은 adapter나 head만 학습하여 특정 목적에 맞게 출력을 조정한다. DyRefHead도 이와 유사하게 frozen I2V backbone 뒤에 붙는 작은 output-side module이다. 차이점은 latent feature가 아니라 RGB video space에서 residual refinement를 수행하며, Stage-1 video 자체를 dynamics prior로 사용한다는 점이다.

Temporal consistency 및 motion preservation objective 역시 관련이 깊다. 본 연구는 학습 중 optical flow를 직접 계산하지 않고, Stage-1과 refined output의 frame-to-frame delta를 비교하는 lightweight proxy를 사용한다. 이는 full physical simulation이나 trajectory supervision이 아니라, Stage-1 dynamics preservation을 위한 실용적 제약이다.

## 4. 제안 방법

### 4.1 문제 정의

입력 이미지로부터 frozen I2V backbone이 Stage-1 video를 생성했다고 하자. 본 연구에서는 이 Stage-1 output을 다음과 같이 정의한다.

```text
X_stage1: physics-induced motion prior
```

Stage-1은 물리적 ground truth가 아니다. 대신 frozen backbone이 생성한 기본 motion trajectory와 temporal structure를 담은 reference video로 사용한다. DyRefHead의 목표는 Stage-1의 움직임 구조를 크게 훼손하지 않으면서 visual detail을 개선하는 것이다.

### 4.2 DyRefHead 구조

DyRefHead는 입력 video tensor `B, C, T, H, W`를 받아 같은 shape의 refined video를 출력한다. v2 구조는 3D convolution block을 사용하며, small batch training에 적합하도록 GroupNorm을 사용한다. 출력은 residual refinement 형태로 계산된다.

```text
Y = clamp(X_stage1 + residual_scale * R(X_stage1), 0, 1)
```

여기서 `R`은 DyRefHead가 예측한 residual이며, `residual_scale`은 보정 강도를 제한하는 계수이다. 본 실험에서는 `residual_scale=0.5`를 사용했다. 이 구조는 Stage-1을 완전히 대체하지 않고, Stage-1 위에 제한된 correction을 더하는 방식이다.

### 4.3 학습 목표

DyRefHead v2는 네 가지 손실을 사용한다.

```text
L = lambda_visual * L_visual
  + lambda_edge * L_edge
  + lambda_temporal_delta * L_temporal_delta
  + lambda_identity * L_identity
```

`L_visual`은 pseudo visual target인 VEnhancer n30과 refined output 사이의 L1 loss이다. `L_edge`는 spatial finite difference를 사용하여 x/y gradient 차이를 줄이는 detail-oriented loss이다. `L_temporal_delta`는 refined output과 Stage-1의 frame-to-frame delta 차이를 줄이는 lightweight dynamics preservation loss이다. `L_identity`는 첫 프레임이 Stage-1과 크게 달라지지 않도록 하는 first-frame identity loss이다.

DyRefHead v2의 loss weight는 다음과 같다.

```text
lambda_visual = 1.0
lambda_edge = 0.5
lambda_temporal_delta = 0.2
lambda_identity = 0.05
```

DyRefHead v3는 loss-weight ablation이다.

```text
lambda_visual = 1.0
lambda_edge = 0.75
lambda_temporal_delta = 0.15
lambda_identity = 0.05
```

v3는 edge/detail learning을 더 강화하고 temporal-delta 제약을 약화했을 때 visual gain과 dynamics drift가 어떻게 변하는지 확인하기 위해 설계했다.

## 5. 실험 설정

### 5.1 데이터

실험은 3개 scene에 대해 수행했다.

```text
scene01_seed0
scene02_seed0
scene03_seed0
```

입력은 RealWonder Stage-1 normalized video이고, pseudo visual target은 VEnhancer n30 normalized video이다. 모든 평가는 256x256, 16fps, 4초 길이로 정규화한 비디오에서 수행했다.

### 5.2 비교 방법

비교 방법은 네 가지다.

| method | role |
|---|---|
| stage1_baseline | frozen I2V backbone output / motion prior |
| venhancer_n30 | off-the-shelf pseudo-target / refinement baseline |
| dyref_head_v2_e20_256 | representative proposed result |
| dyref_head_v3_edge075_temp015_e20_256 | loss-weight ablation |

### 5.3 평가 지표

본 연구는 visual gain과 dynamics drift를 함께 본다.

Visual gain proxy로는 mean sharpness를 사용한다. Dynamics drift proxy로는 Stage-1 대비 flow preservation metric에서 계산한 mean Flow EPE와 flow magnitude ratio를 사용한다. 이 지표들은 Stage-1 dynamics preservation을 측정하기 위한 proxy이며, true physical correctness를 측정하는 지표가 아니다.

## 6. 결과 및 분석

### 6.1 정량 결과

| method | role | mean_sharpness | mean_flow_epe | flow_mag_ratio |
|---|---|---:|---:|---:|
| stage1_baseline | frozen I2V backbone output / motion prior | 279.5409 | 0.0000 | 1.0000 |
| venhancer_n30 | off-the-shelf pseudo-target | 364.3567 | 0.2782 | 3.4906 |
| dyref_head_v2_e20_256 | proposed representative head | 299.5439 | 0.1883 | 1.6971 |
| dyref_head_v3_edge075_temp015_e20_256 | loss ablation | 287.8850 | 0.1901 | 1.5899 |

### 6.2 VEnhancer n30 분석

VEnhancer n30은 가장 큰 visual/detail proxy 개선을 보였다. mean_sharpness는 364.3567로 모든 방법 중 가장 높다. 그러나 dynamics drift proxy도 가장 크다. mean_flow_epe는 0.2782이고 flow_mag_ratio는 3.4906이다. 이는 VEnhancer n30이 pseudo visual target으로는 유용하지만, Stage-1 dynamics prior에서 더 크게 벗어날 수 있음을 보여준다.

### 6.3 DyRefHead v2 분석

DyRefHead v2는 Stage-1 baseline보다 sharpness를 개선했다. Stage-1의 mean_sharpness는 279.5409이고, v2는 299.5439이다. 동시에 VEnhancer n30보다 낮은 dynamics drift proxy를 보였다. v2의 mean_flow_epe는 0.1883, flow_mag_ratio는 1.6971로, VEnhancer n30의 0.2782와 3.4906보다 낮다.

따라서 v2는 VEnhancer n30만큼 강한 visual gain을 보이지는 않지만, Stage-1 dynamics prior에서 덜 벗어나면서 visual quality를 개선하는 균형 잡힌 결과를 제공한다. 본 논문에서는 DyRefHead v2를 대표 proposed result로 사용한다.

### 6.4 DyRefHead v3 Ablation 분석

DyRefHead v3는 edge/detail loss를 강화하고 temporal-delta weight를 낮춘 ablation이다. v3의 flow_mag_ratio는 1.5899로 v2의 1.6971보다 1에 더 가깝다. 이는 dynamics magnitude stability 측면에서는 v3가 더 안정적인 방향으로 작동했음을 시사한다.

그러나 v3의 mean_sharpness는 287.8850으로 v2의 299.5439보다 낮다. mean_flow_epe도 0.1901로 v2의 0.1883보다 약간 높다. 따라서 v3는 dynamics magnitude ratio를 개선했지만 visual gain을 약화시킨 ablation으로 해석하는 것이 적절하다.

### 6.5 Visual Gain-Dynamics Drift Trade-off

전체 결과는 output refinement head 설계에 visual gain-dynamics drift trade-off가 있음을 보여준다. VEnhancer n30은 가장 강한 visual gain을 제공하지만 가장 큰 drift를 보인다. DyRefHead v2는 visual gain과 drift 감소 사이에서 균형을 보인다. DyRefHead v3는 flow magnitude ratio를 더 안정화하지만 visual gain은 낮아진다.

이 결과는 frozen I2V backbone 뒤에 trainable output refinement head를 붙이는 접근의 가능성을 지지한다. 그러나 이는 Stage-1 dynamics preservation proxy 기준의 결과이며, true physical correctness를 보장하지 않는다.

## 7. 결론

본 논문은 frozen I2V backbone의 Stage-1 output을 physics-induced motion prior로 사용하고, 그 위에 trainable video-space output refinement head인 DyRefHead를 적용하는 proof-of-concept를 제시했다. 대표 결과인 DyRefHead v2는 Stage-1 baseline보다 sharpness를 개선하면서, VEnhancer n30보다 낮은 dynamics drift proxy를 보였다.

DyRefHead v3 ablation은 dynamics magnitude stabilization을 더 강화할 수 있지만, visual gain이 약화될 수 있음을 보여주었다. 이는 output refinement head 설계에서 visual gain과 dynamics drift 사이의 균형이 중요하다는 점을 시사한다.

본 연구는 작은 3-scene 실험에 기반한 초기 proof-of-concept이다. Stage-1은 physical ground truth가 아니고, VEnhancer n30도 ground-truth video가 아니다. 따라서 본 논문은 true physical correctness, perfect preservation, globally optimal refinement를 주장하지 않는다. 향후 연구에서는 더 많은 scene, human/perceptual evaluation, 명시적 flow 또는 trajectory preservation objective, latent-space integration과의 비교가 필요하다.
