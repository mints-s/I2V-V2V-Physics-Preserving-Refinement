# 논문 구성안

## 1. 서론

- Physics-sensitive I2V 생성에서 시각적 품질 개선과 동역학 유지가 동시에 중요하다는 문제 제기
- Off-the-shelf V2V enhancer는 시각적 품질을 높일 수 있지만 Stage-1 dynamics에서 벗어날 수 있음
- Frozen I2V backbone 뒤에 trainable output refinement head를 붙이는 접근 제안
- 본 연구의 범위는 proof-of-concept이며 physical ground truth를 주장하지 않음

## 2. 관련 연구

- Image-to-video generation과 physics-aware video generation
- Video enhancement 및 post-processing 기반 V2V refinement
- Frozen backbone adaptation, residual adapters, output-space refinement
- Temporal consistency 및 motion preservation objective

## 3. 제안 방법

- Frozen I2V backbone의 Stage-1 출력을 physics-induced motion prior로 정의
- DyRefHead 구조: 3D convolution 기반 residual video-space refinement head
- Pseudo visual target: VEnhancer n30
- Objective:
  - visual L1 loss
  - spatial gradient/detail loss
  - temporal-delta preservation loss
  - first-frame identity loss
- Optical flow를 학습 중 계산하지 않는 lightweight dynamics proxy 설명

## 4. 실험 설정

- 입력: Stage-1 normalized videos
- pseudo target: VEnhancer n30 normalized videos
- 학습 장면: scene01/02/03
- 대표 모델: DyRefHead v2 e20 256
- ablation: DyRefHead v3 edge075 temp015 e20 256
- 평가:
  - mean sharpness
  - mean flow EPE
  - flow magnitude ratio
  - contact sheet qualitative comparison

## 5. 결과 및 분석

- Stage-1 baseline, VEnhancer n30, DyRefHead v2, DyRefHead v3 비교
- v2가 Stage-1보다 sharpness를 개선하고 VEnhancer보다 drift proxy를 낮춤
- v3는 flow magnitude stability는 개선하지만 visual gain은 감소
- visual gain-dynamics drift trade-off 분석
- limitation:
  - pseudo-target supervision
  - small three-scene proof-of-concept
  - no claim of true physical correctness

## 6. 결론

- Frozen I2V backbone + trainable output refinement head의 가능성 요약
- Stage-1 dynamics prior를 유지하면서 visual refinement를 학습하는 방향 제시
- 향후 과제:
  - 더 큰 scene set
  - 더 강한 perceptual/detail loss
  - explicit flow or trajectory preservation objective
  - human/physics-sensitive qualitative evaluation
