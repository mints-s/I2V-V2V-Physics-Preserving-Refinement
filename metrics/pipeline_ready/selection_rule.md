# 선택 규칙

본 실험에서 Stage-1 출력은 물리적 정답이 아니라, physics-induced motion prior로 취급한다. 즉, Stage-1 비디오는 후속 V2V refinement가 보존해야 할 Stage-1 dynamics의 기준 역할을 하지만, true physical ground truth로 간주하지 않는다.

각 Stage-1 I2V 비디오에 대해 서로 다른 VEnhancer `noise_aug` 값을 사용하여 여러 V2V 후보를 생성한다. 후보들은 시각적 개선 정도와 Stage-1 dynamics drift를 함께 평가한다.

평가 지표는 다음과 같다.

- visual gain: sharpness 증가
- dynamics drift: `mean_flow_epe`
- motion magnitude drift: `|flow_mag_ratio - 1|`

선택 규칙은 다음과 같다.

1. Stage-1 baseline 대비 mean sharpness가 최소 2배 이상인 후보만 선택 가능 후보로 둔다.
2. 이 조건을 만족하는 후보들 중 `mean_flow_epe`가 가장 낮은 후보를 선택한다.
3. 동률이 발생하면 `flow_mag_ratio`가 1에 더 가까운 후보를 선호한다.

이 규칙은 true physical correctness를 보장하지 않는다. 본 방법은 Stage-1 dynamics preservation을 제약으로 둔 lightweight V2V 후보 선택 절차이며, visual gain-dynamics drift trade-off를 명시적으로 드러내는 데 목적이 있다.
