| Method | VBench Imaging ↑ | VBench Motion Smoothness ↑ | Mean Flow EPE ↓ | Flow Mag Ratio ≈1 |
|---|---:|---:|---:|---:|
| 기준 I2V 출력 | 0.6187 | 0.9948 | 0.0000 | 1.0000 |
| VEnhancer n30 | **0.6587** | 0.9940 | 0.2782 | 3.4906 |
| DyRefHead v2 | 0.6242 | 0.9939 | **0.1883** | 1.6971 |
| DyRefHead v3 | 0.6222 | 0.9939 | 0.1901 | **1.5899** |

기준 I2V 출력은 자기 자신과 비교되므로 Flow EPE=0, Flow 크기 비율=1이다. 따라서 Flow 기반 비교에서는 refined method 간의 상대적 이탈을 함께 해석한다.
