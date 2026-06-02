# Final 3-Scene Summary

| method | mean_sharpness | mean_flow_epe | flow_mag_ratio | mean_frame_diff | interpretation |
|---|---:|---:|---:|---:|---|
| stage1_baseline | 198.99 | 0.0000 | 1.0000 | 1.4273 | Stage-1 dynamics / physics-induced motion prior 기준 |
| venhancer_n30 | 559.55 | 0.2796 | 4.6502 | 1.6787 | sharpness가 크게 증가했지만, non-zero dynamics drift와 motion magnitude drift도 발생 |

요약: `venhancer_n30`은 3개 scene 평균에서 sharpness를 `198.99`에서 `559.55`로 증가시켰다. 동시에 `mean_flow_epe=0.2796`, `flow_mag_ratio=4.6502`로 Stage-1 dynamics와 완전히 동일하지 않음을 명시적으로 보여준다.
