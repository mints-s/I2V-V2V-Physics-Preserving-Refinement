# 물리 기반 Image-to-Video 생성 결과의 동역학 보존형 V2V 정제를 위한 후보 선택 전략

## 1. 초록

본 논문은 물리 지향 Image-to-Video(I2V) 생성 결과를 후속 Video-to-Video(V2V) 정제로 개선할 때, 시각적 품질 향상과 동역학 변화 사이의 균형을 선택하기 위한 경량 후보 선택 파이프라인을 제안한다. Stage-1 I2V 출력은 실제 물리 정답(physical ground truth)이 아니라, 후속 정제가 참고해야 할 physics-induced motion prior로 취급한다. 따라서 본 연구의 목표는 true physical correctness를 보장하는 것이 아니라, Stage-1 dynamics preservation 제약 아래에서 visual gain을 얻는 것이다.

제안 방법은 동일한 Stage-1 비디오에서 여러 V2V refinement 후보를 생성하고, sharpness 기반 visual gain과 optical-flow 기반 dynamics drift를 함께 측정한다. 선택 규칙은 Stage-1 baseline 대비 sharpness가 최소 2배 이상인 후보 중 `mean_flow_epe`가 가장 낮은 후보를 선택하는 것이다. Scene01 후보 sweep에서 `venhancer_n30`이 이 규칙에 따라 선택되었으며, 이를 3개 scene에 확장한 결과 평균 sharpness는 Stage-1 baseline의 `198.99`에서 `559.55`로 증가했다. 동시에 `venhancer_n30`은 평균 `mean_flow_epe=0.2796`, `flow_mag_ratio=4.6502`를 보여 non-zero Stage-1 dynamics drift를 도입했다. 이 결과는 제안한 절차가 visual gain-dynamics drift trade-off를 명시적으로 드러내고 후보 선택을 지원함을 보여주지만, 물리적 정확성의 보장을 의미하지는 않는다.

## 2. 서론

물리적 상호작용을 포함하는 I2V 생성에서는 물체의 이동 방향, 접촉 시점, 국소 반응, 궤적의 일관성이 중요하다. 그러나 초기 I2V 출력은 시각적 디테일이나 선명도 측면에서 부족할 수 있으며, 이를 개선하기 위해 V2V refinement를 적용할 수 있다. 문제는 V2V refinement가 외형 품질을 향상시키는 동시에 Stage-1에서 형성된 motion pattern을 변경할 수 있다는 점이다.

본 연구는 이 문제를 true physical correctness 검증 문제가 아니라 Stage-1 dynamics preservation을 제약으로 둔 후보 선택 문제로 다룬다. Stage-1 I2V 출력은 물리적 정답이 아니라 physics-induced motion prior이며, 후속 V2V 결과는 이 prior와의 차이를 함께 보고해야 한다. 따라서 핵심 질문은 “어떤 V2V 후보가 충분한 visual gain을 제공하면서 Stage-1 dynamics drift를 상대적으로 작게 유지하는가”이다.

이를 위해 본 논문은 visual gain-dynamics drift trade-off를 수치화하는 경량 파이프라인을 제안한다. 이 파이프라인은 논문 수준의 물리 검증을 대체하지 않으며, 제한된 후보군 안에서 정제 강도를 선택하기 위한 실험적 절차로 사용된다.

## 3. 제안 방법

제안 방법은 네 단계로 구성된다.

첫째, physics-oriented I2V stage를 통해 초기 비디오를 생성한다. 이 Stage-1 출력은 true physical ground truth가 아니라 physics-induced motion prior로 사용된다. 즉, 후속 refinement가 보존해야 할 동작 방향, 접촉 시점, 국소 반응, 궤적의 기준으로 Stage-1 dynamics를 활용한다.

둘째, 동일한 Stage-1 비디오를 입력으로 여러 V2V refinement 후보를 생성한다. 본 실험에서는 VEnhancer의 `noise_aug` 값을 달리하여 `venhancer_n30`, `venhancer_n50`, `venhancer_n70`, `venhancer_n100`, `venhancer_n200` 후보를 구성했다. 각 후보는 같은 Stage-1 motion prior에서 출발하지만, refinement 강도에 따라 visual detail과 dynamics drift가 달라질 수 있다.

셋째, 각 후보를 visual gain-dynamics drift trade-off 관점에서 평가한다. Visual gain은 mean sharpness 증가로 측정한다. Stage-1 dynamics preservation은 `mean_flow_epe`와 `flow_mag_ratio`를 통해 간접적으로 측정한다. `mean_flow_epe`는 Stage-1과 후보 결과 사이의 optical flow 차이를 나타내며, `flow_mag_ratio`는 motion magnitude가 Stage-1 대비 얼마나 달라졌는지를 보여준다.

넷째, 정의된 규칙에 따라 후보를 선택한다. 선택 가능 후보는 Stage-1 baseline 대비 mean sharpness가 최소 2배 이상인 결과로 제한한다. 그중 `mean_flow_epe`가 가장 낮은 후보를 선택하며, 동률이 발생하면 `flow_mag_ratio`가 1에 더 가까운 후보를 선호한다. 이 절차는 완벽한 dynamics preservation을 주장하지 않고, Stage-1 dynamics preservation을 제약으로 둔 lightweight V2V candidate selection으로 formulation된다.

## 4. 실험 및 결과

실험은 `scene01_seed0`, `scene02_seed0`, `scene03_seed0` 세 개 scene에서 수행했다. 후보 선택은 scene01 fine sweep에서 먼저 수행하고, 선택된 설정을 scene02와 scene03에 확장했다. 정량 평가는 Stage-1 baseline과 V2V 후보 사이의 sharpness, `mean_flow_epe`, `flow_mag_ratio`, `mean_frame_diff`를 기준으로 수행했다.

Scene01 후보 sweep에서 Stage-1 baseline의 mean sharpness는 `172.2546`이었다. 모든 VEnhancer 후보는 Stage-1 baseline 대비 sharpness 2배 조건을 만족했다. 이 중 `venhancer_n30`은 `mean_sharpness=642.81`, `sharpness_gain_ratio=3.73`, `mean_flow_epe=0.4123`, `flow_mag_ratio=3.3165`를 보였고, sharpness 조건을 만족한 후보 중 가장 낮은 `mean_flow_epe`를 기록했다. 이에 따라 `venhancer_n30`을 정의된 규칙 아래의 selected trade-off candidate로 선택했다.

후보 강도가 커질수록 visual detail proxy인 sharpness는 전반적으로 증가했지만, Stage-1 dynamics drift도 함께 증가하는 경향이 나타났다. 예를 들어 `venhancer_n200`은 `mean_flow_epe=0.5711`, `flow_mag_ratio=7.6986`을 보여 `venhancer_n30`보다 더 큰 dynamics drift와 motion magnitude drift를 보였다. 따라서 가장 높은 sharpness만을 기준으로 선택하는 것은 Stage-1 dynamics preservation 관점에서 적절하지 않을 수 있다.

선택된 `venhancer_n30`을 scene02와 scene03에 확장한 3-scene 평균 결과에서, Stage-1 baseline의 mean sharpness는 `198.99`였고 `venhancer_n30`의 mean sharpness는 `559.55`였다. 이는 V2V refinement가 visual/detail proxy를 실질적으로 개선했음을 보여준다. 그러나 `venhancer_n30`의 평균 `mean_flow_epe`는 `0.2796`, `flow_mag_ratio`는 `4.6502`로 나타났다. 따라서 `venhancer_n30`은 Stage-1 dynamics를 완벽하게 보존한 결과가 아니며, non-zero Stage-1 dynamics drift를 도입한다.

정성 평가를 위해 scene별 Stage-1 baseline과 selected output을 비교하는 contact sheet를 생성했다. 또한 scene01에 대해서는 VEnhancer fine sweep contact sheet를 제공하여 후보 강도 변화에 따른 visual gain과 dynamics drift를 함께 검토할 수 있도록 했다. 정성 평가 항목은 action meaning preservation, trajectory consistency, contact timing preservation, local response preservation, subject stability, visual gain을 포함한다.

결과적으로 본 실험은 V2V refinement가 시각적 디테일을 크게 개선할 수 있지만, Stage-1 dynamics와의 차이도 함께 발생시킨다는 점을 보여준다. `venhancer_n30`은 물리적으로 정확한 결과라는 의미에서 선택된 것이 아니라, 정의된 sharpness 조건과 `mean_flow_epe` 기준 아래에서 선택된 trade-off candidate이다.

## 5. 결론

본 논문은 물리 지향 I2V 출력에 V2V refinement를 적용할 때 사용할 수 있는 경량 후보 선택 전략을 제안했다. Stage-1 I2V 출력은 physical ground truth가 아니라 physics-induced motion prior로 취급했으며, 제안 방법은 true physical correctness를 보장하는 대신 Stage-1 dynamics preservation 제약 아래에서 visual gain을 얻는 것을 목표로 했다.

실험 결과, `venhancer_n30`은 Stage-1 baseline 대비 sharpness를 크게 향상시켜 3-scene 평균 `198.99`에서 `559.55`로 증가시켰다. 동시에 평균 `mean_flow_epe=0.2796`, `flow_mag_ratio=4.6502`를 보여 Stage-1 dynamics drift가 존재함을 확인했다. 따라서 본 결과는 V2V refinement의 물리적 정확성을 증명하는 것이 아니라, visual gain-dynamics drift trade-off를 명시적으로 측정하고 후보를 선택하는 절차의 유용성을 보여준다.

향후 작업으로는 더 많은 scene에 대한 평가, 독립 연구자 기반 정성 평가, 그리고 deterministic interpolation baseline과의 비교가 필요하다. 또한 Stage-1 dynamics preservation을 더 직접적으로 측정할 수 있는 task-specific metric을 추가하면 후보 선택의 신뢰도를 높일 수 있다.
