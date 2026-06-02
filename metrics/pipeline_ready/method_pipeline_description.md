# Method: Lightweight V2V Candidate Selection Pipeline

## Stage 1: Physics-Oriented I2V Generation

먼저 physics-oriented I2V stage를 통해 초기 비디오를 생성한다. 이 Stage-1 출력은 true physical ground truth가 아니라 physics-induced motion prior로 사용된다. 즉, 후속 refinement가 보존해야 할 동작 방향, 접촉 시점, 국소 반응, 궤적의 기준으로 Stage-1 dynamics를 활용한다.

## Stage 2: V2V Candidate Generation

Stage-1 비디오를 입력으로 사용하여 여러 V2V refinement 후보를 생성한다. 본 실험에서는 VEnhancer의 `noise_aug` 값을 달리하여 `venhancer_n30`, `venhancer_n50`, `venhancer_n70`, `venhancer_n100`, `venhancer_n200` 후보를 구성했다. 각 후보는 동일한 Stage-1 motion prior에서 출발하지만, refinement 강도에 따라 visual detail과 dynamics drift가 달라질 수 있다.

## Stage 3: Metric-Based Candidate Selection

각 후보는 visual gain-dynamics drift trade-off 관점에서 평가한다. Visual gain은 sharpness 증가로 측정하고, Stage-1 dynamics preservation은 `mean_flow_epe`와 `flow_mag_ratio`를 통해 간접적으로 측정한다. 선택 규칙은 Stage-1 baseline 대비 sharpness가 2배 이상인 후보를 먼저 고르고, 그중 `mean_flow_epe`가 가장 낮은 후보를 선택한다. 이 절차는 완벽한 dynamics preservation을 주장하지 않고, Stage-1 dynamics preservation을 제약으로 둔 후보 선택 문제로 formulation한다.

## Stage 4: Final Enhanced Output

선택된 후보 설정을 나머지 scene에 확장하여 최종 enhanced output을 생성한다. 본 실험에서는 scene01 sweep에서 선택된 `venhancer_n30`을 scene02와 scene03에 적용했다. 최종 출력은 더 높은 visual detail을 제공하지만, metrics와 qualitative review를 통해 Stage-1 dynamics와의 차이를 함께 보고한다. 따라서 본 방법은 lightweight refinement pipeline이며, visual improvement와 Stage-1 dynamics drift를 동시에 드러내는 선택 절차이다.
