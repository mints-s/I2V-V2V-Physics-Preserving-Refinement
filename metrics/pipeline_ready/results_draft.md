# Results Draft

Scene01 candidate sweep 결과, V2V refinement가 강해질수록 전반적으로 visual detail proxy인 sharpness가 크게 증가했다. 그러나 refinement 강도가 커질수록 Stage-1 dynamics drift도 증가하는 경향을 보였다. 예를 들어 `venhancer_n30`은 `mean_flow_epe=0.4123`, `flow_mag_ratio=3.3165`였고, `venhancer_n200`은 `mean_flow_epe=0.5711`, `flow_mag_ratio=7.6986`으로 더 큰 drift를 보였다.

정의된 선택 규칙에 따라 Stage-1 baseline 대비 sharpness가 2배 이상인 후보를 먼저 선택 가능 후보로 두었다. Scene01에서는 모든 VEnhancer 후보가 이 조건을 만족했으며, 그중 `mean_flow_epe`가 가장 낮은 `venhancer_n30`이 best trade-off candidate among tested VEnhancer strengths로 선택되었다.

선택된 `venhancer_n30`을 scene02와 scene03에 확장한 결과, 3개 scene 평균 sharpness는 Stage-1 baseline의 `198.99`에서 `559.55`로 증가했다. 이는 V2V refinement가 visual detail을 실질적으로 개선함을 보여준다.

동시에 `venhancer_n30`은 non-zero drift를 도입했다. 3개 scene 평균 `mean_flow_epe`는 `0.2796`이었고, `flow_mag_ratio`는 `4.6502`였다. 따라서 refinement 결과가 Stage-1 dynamics와 완전히 동일하다고 볼 수는 없다.

결과적으로 제안하는 pipeline은 visual detail을 개선하면서도 Stage-1 dynamics preservation과의 trade-off를 명시적으로 노출하고 제어한다. 본 결과는 true physical correctness를 보장한다는 주장이 아니라, physics-induced motion prior를 기준으로 V2V 후보를 선택하는 lightweight refinement pipeline의 가능성을 보여준다.
