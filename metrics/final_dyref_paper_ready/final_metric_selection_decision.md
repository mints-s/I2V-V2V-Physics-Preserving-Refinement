# 최종 지표 선택 결정

## 1. DOVER 결정

DOVER Overall은 메인 표에서 제거한다. 이유는 DOVER가 no-reference overall video quality ranking 지표이며, 본 논문의 핵심 주장인 기준 I2V 출력 대비 동역학 보존을 직접 측정하지 않기 때문이다. 필요하다면 limitation 또는 supplementary에서 참고 지표로 언급할 수 있으나, 실패를 주장하는 근거로 사용하지 않는다.

## 2. VBench 결정

VBench Imaging은 시각 품질 지표로 유지한다. VBench Motion Smoothness는 시간적 매끄러움 확인을 위한 보조 지표로 유지한다. VBench Dynamic Degree는 refinement가 움직임을 과도하게 억제하는지 확인하기 위해 추가하려 했으나, 현재 환경에서 평가가 실패했으므로 이번 메인 표에는 포함하지 않는다. Trustworthiness는 별도 필요가 없는 한 추가하지 않는다.

## 3. Flow 지표 결정

Mean Flow EPE와 Flow Mag Ratio는 유지한다. 두 지표는 기준 영상 대비 동역학 이탈을 측정하기 위한 task-specific auxiliary metric으로 정의한다. Flow 기반 지표는 실제 물리 정합성이 아니라 기준 I2V 출력의 움직임 보존 관점에서만 해석한다.

## 4. VE-Bench 결정

VE-Bench QA는 공식 checkpoint 문제로 제외한다. 필요할 때만 checkpoint unavailable로 인해 제외했다고 간단히 언급한다.

## 5. 최종 메인 표 권장안

Preferred 구성은 VBench Imaging, Motion Smoothness, Dynamic Degree, Mean Flow EPE, Flow Mag Ratio이다. 단, Dynamic Degree가 현재 환경에서 실패했으므로 본 revision에서는 fallback 구성을 사용한다.

Fallback 구성:

- VBench Imaging
- VBench Motion Smoothness
- Mean Flow EPE
- Flow Mag Ratio
