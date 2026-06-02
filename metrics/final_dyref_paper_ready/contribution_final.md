# 최종 기여 정리

## 1. Frozen I2V Backbone + Trainable Output Refinement Head

본 연구는 기존 I2V 모델 전체를 다시 학습하지 않고, frozen I2V backbone의 Stage-1 출력 뒤에 작은 trainable output refinement head를 붙이는 방향을 제안한다. DyRefHead는 RGB video space에서 residual refinement를 수행하며, backbone이 생성한 기본 시간 흐름을 대체하기보다 보정하는 역할을 한다.

## 2. Stage-1 Motion Prior를 활용한 Dynamics-Aware Objective

Stage-1 비디오는 물리적 ground truth가 아니라 physics-induced motion prior로 사용한다. DyRefHead 학습에서는 VEnhancer n30을 pseudo visual target으로 두되, Stage-1의 temporal delta와 first-frame identity를 함께 제약하여 시각적 개선이 Stage-1 dynamics에서 과도하게 벗어나지 않도록 한다.

## 3. Physics-Sensitive I2V Scene에서 Visual Gain과 Dynamics Drift의 동시 평가

본 연구는 sharpness 기반 visual gain proxy와 flow preservation 기반 dynamics drift proxy를 함께 보고한다. 이를 통해 단순히 더 선명한 결과가 항상 더 적절한 것은 아니며, output refinement head 설계에는 visual gain-dynamics drift trade-off가 존재함을 보인다.

이 기여는 proof-of-concept 수준이며 true physical correctness나 perfect preservation을 주장하지 않는다.
