# DyRefHead e10 128x128 결과 보존 메모

DyRefHead e10은 VEnhancer n30 대비 flow drift를 줄이는 방향의 결과를 보였지만, Stage-1 대비 sharpness 개선에는 실패했다.

이 결과는 기존 50 epoch 설정을 그대로 늘리는 것보다, edge/detail loss와 temporal-delta preservation을 추가한 DyRefHead v2 실험이 필요하다는 근거로 사용한다.

VEnhancer n30은 pseudo visual target이며 ground truth가 아니다. Stage-1은 physics-induced motion prior로 취급하며, true physical correctness를 주장하지 않는다.
