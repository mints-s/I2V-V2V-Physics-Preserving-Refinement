# 표 X. VBench 기반 시각·시간 품질 지표와 기준 영상 대비 동역학 이탈 보조 지표 비교

VBench Imaging은 출력 영상의 시각 품질을 평가하고, VBench Motion Smoothness는 시간적 매끄러움 확인을 위한 보조 지표로 사용하였다. Mean Flow EPE와 Flow 크기 비율은 기준 I2V 출력 대비 움직임 이탈을 측정하기 위한 보조 지표이다. Flow 기반 지표는 실제 물리 정합성이 아니라 기준 영상의 동역학 보존 관점에서 해석한다.

| Method | VBench Imaging ↑ | VBench Motion Smoothness ↑ | Mean Flow EPE ↓ | Flow Mag Ratio ≈1 |
|---|---:|---:|---:|---:|
| 기준 I2V 출력 | 0.6187 | 0.9948 | 0.0000 | 1.0000 |
| VEnhancer n30 | **0.6587** | 0.9940 | 0.2782 | 3.4906 |
| DyRefHead v2 | 0.6242 | 0.9939 | **0.1883** | 1.6971 |
| DyRefHead v3 | 0.6222 | 0.9939 | 0.1901 | **1.5899** |

기준 I2V 출력은 자기 자신과 비교되므로 Flow EPE=0, Flow 크기 비율=1이다.
