# DyRefHead v2 e20 256x256 결과 보존 메모

DyRefHead v2는 Stage-1 대비 sharpness를 개선했다.

또한 VEnhancer n30과 비교했을 때 Flow EPE와 flow_mag_ratio를 모두 낮춰, Stage-1 dynamics prior에서의 drift를 더 작게 유지하는 경향을 보였다.

다만 visual/detail gain은 VEnhancer n30보다 아직 약하다. 따라서 다음 실험은 edge/detail learning을 더 강하게 주는 v3 loss-weight ablation으로 진행한다.

이 결과는 proof-of-concept 수준의 출력 보정 가능성을 보여주는 것이며, true physical correctness나 완전한 dynamics preservation을 주장하지 않는다.
