# 결과 해석

DyRefHead v2는 Stage-1 baseline보다 mean sharpness를 개선했다. 256x256 평가에서 Stage-1의 mean_sharpness는 279.5409이고, DyRefHead v2는 299.5439이다. 이는 frozen I2V backbone 출력 위에 작은 trainable output refinement head를 붙이는 방식이 일정 수준의 visual gain을 줄 수 있음을 보여준다.

동시에 DyRefHead v2는 VEnhancer n30보다 flow drift proxy를 낮췄다. VEnhancer n30의 mean_flow_epe는 0.2782, flow_mag_ratio는 3.4906인 반면, DyRefHead v2는 각각 0.1883과 1.6971이다. 이는 DyRefHead v2가 VEnhancer n30만큼 강한 시각적 보정을 만들지는 못하지만, Stage-1 dynamics prior에서 덜 벗어나는 방향의 보정을 학습했음을 시사한다.

DyRefHead v3 ablation은 더 강한 edge/detail loss와 더 약한 temporal-delta weight를 사용했다. 결과적으로 v3의 flow_mag_ratio는 1.5899로 v2의 1.6971보다 1에 더 가까워졌지만, mean_sharpness는 287.8850으로 v2보다 낮아졌다. 이는 dynamics magnitude stabilization을 강화하는 방향이 항상 visual gain을 높이지는 않는다는 점을 보여준다.

따라서 DyRefHead 계열의 output refinement head 설계에는 visual gain-dynamics preservation trade-off가 존재한다. 대표 결과로는 sharpness 개선과 drift 감소가 함께 관찰된 v2가 더 균형 잡힌 선택이다.

이 결과는 physics-sensitive I2V scene에서의 proof-of-concept로 해석해야 한다. Stage-1은 physical ground truth가 아니며, VEnhancer n30도 ground truth가 아니다. 본 실험은 true physical correctness나 perfect preservation을 주장하지 않는다.
