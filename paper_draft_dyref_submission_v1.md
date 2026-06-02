# Frozen Image-to-Video Backbone을 위한 동역학 보존 제약 기반 출력 정제 Head

## 1. 초록

최근 Image-to-Video(I2V) 모델은 입력 이미지로부터 시간적 장면 변화를 생성하지만, physics-sensitive scene에서는 시각 품질 향상과 기존 motion structure 보존 사이의 균형이 중요하다. 본 논문은 frozen I2V backbone의 Stage-1 출력을 physics-induced motion prior로 두고, 그 위에 trainable video-space output refinement head인 DyRefHead를 적용하는 proof-of-concept 구조를 제안한다. DyRefHead는 VEnhancer n30을 pseudo visual target으로 사용하되, temporal-delta 및 first-frame identity 기반의 lightweight dynamics-aware objective를 통해 Stage-1 dynamics prior에서 과도하게 벗어나지 않도록 학습된다. 3개 scene의 256x256 평가에서 DyRefHead v2는 Stage-1 대비 mean sharpness를 279.54에서 299.54로 향상시켰고, VEnhancer n30보다 낮은 mean Flow EPE(0.1883 vs. 0.2782)와 flow magnitude ratio(1.6971 vs. 3.4906)를 보였다. 추가 ablation인 v3는 motion magnitude 안정성은 높였지만 visual gain은 감소하였다. 이는 frozen I2V backbone 뒤의 output refinement head 설계에서 visual gain과 Stage-1 dynamics preservation 사이의 trade-off를 고려해야 함을 보여준다.

## 2. 서론

Image-to-video 생성 모델은 입력 이미지로부터 시간적으로 일관된 장면 변화를 생성해야 한다. 특히 접촉, 이동, 변형, 관성적 움직임이 중요한 physics-sensitive scene에서는 단순히 각 프레임을 선명하게 만드는 것만으로 충분하지 않다. 후처리나 video enhancement가 시각적 품질을 높이더라도, 원래 I2V backbone이 생성한 motion structure에서 크게 벗어나면 결과 비디오는 동역학적으로 불안정하게 보일 수 있다.

본 연구는 이 문제를 frozen I2V backbone의 출력부 정제 문제로 다룬다. RealWonder Stage-1 출력을 physics-induced motion prior로 두고, 전체 I2V 모델을 재학습하지 않은 채 그 뒤에 작은 trainable output refinement head를 붙인다. 제안하는 DyRefHead는 RGB video space에서 residual correction을 예측하며, Stage-1의 시간적 구조를 대체하기보다 제한적으로 보정한다.

본 논문에서 VEnhancer n30은 off-the-shelf refinement baseline이자 pseudo visual target으로 사용된다. VEnhancer n30은 강한 visual/detail gain을 제공하지만, Stage-1 dynamics prior에서 더 크게 벗어날 수 있다. 따라서 본 연구의 목적은 VEnhancer를 ground truth로 모사하는 것이 아니라, pseudo target을 활용하면서도 Stage-1 dynamics drift를 제한하는 output-side refinement 가능성을 확인하는 것이다.

본 논문의 기여는 세 가지다. 첫째, frozen I2V backbone과 trainable video-space output refinement head를 결합한 proof-of-concept 구조를 제안한다. 둘째, Stage-1 motion prior를 활용한 lightweight dynamics-aware objective를 설계한다. 셋째, visual gain과 dynamics drift proxy를 함께 평가하여, 출력 정제 head 설계에 trade-off가 존재함을 보인다.

## 3. 관련 연구

I2V 생성 연구는 입력 이미지의 장면 구조를 유지하면서 시간적 변화를 생성하는 방향으로 발전해 왔다. 최근 모델들은 높은 시각적 품질을 보이지만, physics-sensitive scene에서는 생성된 motion의 일관성과 보존 문제가 여전히 중요하다.

Video enhancement 및 video-to-video refinement 연구는 입력 비디오의 sharpness, texture, temporal consistency를 개선하는 데 초점을 둔다. 기존 video enhancement 연구가 입력 비디오의 시각 품질 및 temporal consistency를 주로 개선하는 반면, 본 연구는 I2V backbone이 생성한 Stage-1 dynamics prior를 보존해야 하는 출력부 정제 문제를 다룬다. 이 차이 때문에 본 연구에서는 단순 sharpness 개선뿐 아니라 Stage-1 대비 flow drift proxy를 함께 평가한다.

Frozen backbone adaptation 연구는 대규모 pretrained model을 고정한 채 작은 adapter나 head만 학습하여 특정 목적에 맞게 출력을 조정한다. DyRefHead도 이와 유사하지만, latent feature가 아니라 RGB video space에서 residual refinement를 수행한다. 또한 Stage-1 비디오 자체를 physics-induced motion prior로 사용한다는 점에서 일반적인 video post-processing과 구별된다.

Temporal consistency 및 motion preservation objective도 본 연구와 관련된다. 다만 본 연구는 학습 중 optical flow를 직접 계산하지 않고, Stage-1과 refined output의 frame-to-frame delta를 비교하는 lightweight proxy를 사용한다. 이는 full physical simulation이나 trajectory supervision이 아니라 Stage-1 dynamics preservation을 위한 실용적 제약이다.

## 4. 제안 방법

### 4.1 문제 정의

Frozen I2V backbone이 생성한 Stage-1 video를 `X_stage1`이라 하자. 본 연구는 `X_stage1`을 physical ground truth가 아니라 physics-induced motion prior로 간주한다. 목표는 Stage-1의 motion structure를 과도하게 변경하지 않으면서, pseudo visual target이 제공하는 visual/detail cue를 일부 학습하는 것이다.

### 4.2 DyRefHead 구조

DyRefHead는 `B, C, T, H, W` 형태의 video tensor를 입력받아 같은 shape의 refined video를 출력한다. v2 구조는 3D convolution block과 GroupNorm을 사용하며, small batch training에서도 동작하도록 설계했다. 출력은 다음 residual refinement로 계산된다.

```text
Y = clamp(X_stage1 + residual_scale * R(X_stage1), 0, 1)
```

여기서 `R`은 DyRefHead가 예측한 residual이고, `residual_scale`은 보정 강도를 제한하는 계수이다. 본 실험에서는 `residual_scale=0.5`를 사용했다. 이 구조는 Stage-1을 대체하지 않고 Stage-1 위에 제한된 correction을 더한다.

### 4.3 학습 목표

DyRefHead는 VEnhancer n30을 pseudo visual target으로 사용한다. 동시에 Stage-1 dynamics prior에서의 drift를 제한하기 위해 temporal-delta preservation과 first-frame identity를 적용한다. 전체 손실은 다음과 같다.

```text
L = lambda_visual * L_visual
  + lambda_edge * L_edge
  + lambda_temporal_delta * L_temporal_delta
  + lambda_identity * L_identity
```

`L_visual`은 pseudo visual target과 refined output 사이의 L1 loss이다. `L_edge`는 spatial finite difference 기반 gradient loss이다. `L_temporal_delta`는 refined output과 Stage-1의 frame-to-frame delta 차이를 줄인다. `L_identity`는 첫 프레임이 Stage-1에서 크게 벗어나지 않도록 한다.

대표 결과인 DyRefHead v2는 `lambda_visual=1.0`, `lambda_edge=0.5`, `lambda_temporal_delta=0.2`, `lambda_identity=0.05`를 사용한다. Ablation인 v3는 edge/detail weight를 0.75로 높이고 temporal-delta weight를 0.15로 낮춰 visual gain과 motion magnitude stability의 변화를 확인한다.

## 5. 실험 설정

실험은 `scene01_seed0`, `scene02_seed0`, `scene03_seed0`의 3개 scene에서 수행했다. 입력은 RealWonder Stage-1 normalized video이고, pseudo visual target은 VEnhancer n30 normalized video이다. 모든 평가는 256x256, 16fps, 4초 길이로 정규화한 비디오에서 수행했다.

비교 방법은 네 가지다. `stage1_baseline`은 frozen I2V backbone output이자 motion prior이다. `venhancer_n30`은 off-the-shelf pseudo-target 및 refinement baseline이다. `dyref_head_v2_e20_256`은 대표 proposed result이며, `dyref_head_v3_edge075_temp015_e20_256`은 loss-weight ablation이다.

평가는 visual gain proxy와 dynamics drift proxy를 함께 사용한다. Visual gain은 mean sharpness로 측정한다. Dynamics drift는 Stage-1 대비 mean Flow EPE와 flow magnitude ratio로 측정한다. 이 flow 기반 지표는 Stage-1 dynamics preservation proxy이며, physical correctness 자체를 측정하지 않는다.

## 6. 결과 및 분석

### 6.1 정량 결과

| method | role | mean_sharpness | mean_flow_epe | flow_mag_ratio |
|---|---|---:|---:|---:|
| stage1_baseline | frozen I2V backbone output / motion prior | 279.5409 | 0.0000 | 1.0000 |
| venhancer_n30 | off-the-shelf pseudo-target | 364.3567 | 0.2782 | 3.4906 |
| dyref_head_v2_e20_256 | proposed representative head | 299.5439 | 0.1883 | 1.6971 |
| dyref_head_v3_edge075_temp015_e20_256 | loss ablation | 287.8850 | 0.1901 | 1.5899 |

VEnhancer n30은 가장 높은 sharpness를 보였다. 그러나 mean Flow EPE와 flow magnitude ratio도 가장 높아, Stage-1 dynamics prior에서 가장 크게 벗어나는 경향을 보였다. 이는 off-the-shelf enhancement가 visual/detail gain에는 유리하지만, physics-sensitive I2V 결과에서는 dynamics drift를 함께 고려해야 함을 보여준다.

### 6.2 DyRefHead v2 대표 결과

DyRefHead v2는 Stage-1 대비 mean sharpness를 279.5409에서 299.5439로 개선했다. 동시에 VEnhancer n30보다 낮은 mean Flow EPE(0.1883 vs. 0.2782)와 flow magnitude ratio(1.6971 vs. 3.4906)를 보였다. 즉, v2는 VEnhancer n30만큼 강한 visual gain을 만들지는 못하지만, Stage-1 dynamics prior에서 덜 벗어나면서 시각적 품질을 개선하는 균형 잡힌 결과를 제공한다.

이 결과는 frozen I2V backbone 뒤에 trainable output refinement head를 붙이는 접근이 가능함을 보여준다. 다만 이는 Stage-1 preservation proxy 기준의 결과이며 true physical correctness를 의미하지 않는다.

### 6.3 v2/v3 Ablation

DyRefHead v3는 edge/detail loss를 강화하고 temporal-delta weight를 낮춘 ablation이다. v3의 flow magnitude ratio는 1.5899로 v2의 1.6971보다 1에 더 가깝다. 그러나 v3의 mean sharpness는 287.8850으로 v2의 299.5439보다 낮고, mean Flow EPE도 0.1901로 v2의 0.1883보다 약간 높다.

따라서 v3는 dynamics magnitude stability를 강화할 수 있지만 visual gain이 약해지는 사례로 해석된다. 이는 DyRefHead 설계에서 visual gain과 dynamics drift 사이의 trade-off가 존재함을 보여준다. 본 논문에서는 v2를 대표 방법으로, v3를 loss-weight ablation으로 사용한다.

## 7. 결론

본 논문은 frozen I2V backbone의 Stage-1 output을 physics-induced motion prior로 사용하고, 그 위에 trainable video-space output refinement head인 DyRefHead를 적용하는 proof-of-concept를 제시했다. 대표 결과인 DyRefHead v2는 Stage-1 baseline보다 sharpness를 개선하면서, VEnhancer n30보다 낮은 dynamics drift proxy를 보였다. DyRefHead v3 ablation은 flow magnitude ratio를 더 안정화할 수 있지만 visual gain이 약화될 수 있음을 보여주었다.

본 연구의 한계도 명확하다. 실험은 3개 scene에 기반하며, VEnhancer n30은 ground truth가 아닌 pseudo visual target이다. Flow metric은 Stage-1 dynamics preservation proxy일 뿐 physical correctness를 측정하지 않는다. 또한 DyRefHead는 현재 RGB video-space proof-of-concept이며 latent-space integration이나 full perceptual/human evaluation은 향후 과제로 남아 있다. 따라서 본 논문은 true physical correctness, perfect preservation, globally optimal refinement를 주장하지 않는다.
