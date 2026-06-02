# Scene01 Candidate Sweep

Stage-1 baseline sharpness: `172.2546`

| method | mean_sharpness | sharpness_gain_ratio | mean_flow_epe | flow_mag_ratio | \|flow_mag_ratio - 1\| | selected_or_not | reason |
|---|---:|---:|---:|---:|---:|---|---|
| stage1_baseline | 172.25 | 1.00 | 0.0000 | 1.0000 | 0.0000 | no | 기준 Stage-1 dynamics / physics-induced motion prior |
| venhancer_n30 | 642.81 | 3.73 | 0.4123 | 3.3165 | 2.3165 | selected | sharpness 2배 조건을 만족한 후보 중 mean_flow_epe가 가장 낮음 |
| venhancer_n50 | 666.82 | 3.87 | 0.4244 | 3.7275 | 2.7275 | no | visual gain은 더 크지만 n30보다 dynamics drift가 큼 |
| venhancer_n70 | 694.93 | 4.03 | 0.4449 | 4.3517 | 3.3517 | no | sharpness는 가장 높지만 n30보다 dynamics drift가 큼 |
| venhancer_n100 | 687.41 | 3.99 | 0.4754 | 5.6352 | 4.6352 | no | dynamics drift와 motion magnitude drift가 증가 |
| venhancer_n200 | 607.16 | 3.52 | 0.5711 | 7.6986 | 6.6986 | no | tested 후보 중 mean_flow_epe와 motion magnitude drift가 가장 큼 |

결론: scene01 fine sweep에서는 모든 VEnhancer 후보가 Stage-1 baseline 대비 sharpness 2배 조건을 만족했다. 이 중 `venhancer_n30`이 가장 낮은 `mean_flow_epe`를 보여, tested VEnhancer strengths 중 best trade-off candidate로 선택되었다.
