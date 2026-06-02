# 최종 초록 후보

본 연구는 physics-sensitive image-to-video 생성에서 frozen I2V backbone의 출력을 보존하면서 시각적 품질을 개선하기 위한 trainable output refinement head를 제안한다. 기존 I2V 모델 전체를 재학습하는 대신, RealWonder Stage-1 출력을 physics-induced motion prior로 사용하고, 그 위에 비디오 공간 residual refinement module인 DyRefHead를 적용한다. 학습 시 VEnhancer n30 결과는 ground truth가 아니라 pseudo visual target으로 사용하며, Stage-1의 temporal dynamics를 보존하기 위한 lightweight temporal-delta objective를 함께 적용한다.

실험에서는 Stage-1 baseline, VEnhancer n30, DyRefHead v2, DyRefHead v3 ablation을 256x256 해상도에서 비교한다. 대표 결과인 DyRefHead v2는 Stage-1보다 sharpness를 개선하면서, VEnhancer n30보다 낮은 flow drift proxy를 보인다. 추가 ablation인 v3는 flow magnitude ratio를 더 안정화하지만 visual gain이 감소하여, output refinement head 설계에 visual gain-dynamics drift trade-off가 있음을 보여준다.

본 결과는 frozen I2V backbone과 dynamics-aware output refinement head 조합의 proof-of-concept를 제시한다. 다만 Stage-1은 물리적 정답이 아니며, 본 연구는 true physical correctness나 완전한 dynamics preservation을 주장하지 않는다.
