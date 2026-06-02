# 평가 프로토콜

본 평가는 I2V 출력 refinement에서 시각 품질 개선과 기준 영상 대비 동역학 보존 사이의 trade-off를 확인하는 데 초점을 둔다. DOVER Overall도 측정하였으나, 본 논문의 핵심 분석 축인 기준 영상 대비 동역학 보존을 직접 측정하지 않으므로 메인 표에서는 제외하였다. DOVER는 일반적인 no-reference video quality ranking 지표로 해석할 수 있으나, 본 실험의 주된 비교 대상인 기준 I2V 출력 대비 움직임 이탈을 직접 설명하지는 않는다.

VBench Imaging은 출력 영상의 시각 품질을 평가하기 위해 사용하였다. VBench Motion Smoothness는 시간적 매끄러움 확인을 위한 보조 지표로 사용하였다. VBench Dynamic Degree는 refinement가 움직임을 과도하게 억제하는지 확인하기 위한 후보 지표로 평가를 시도하였으나, 현재 환경에서는 RAFT 체크포인트 압축 해제에 필요한 `unzip` 실행 파일이 없어 완료되지 않았다. 따라서 본 revision의 메인 표에는 포함하지 않는다.

Mean Flow EPE와 Flow Mag Ratio는 기준 영상 대비 동역학 이탈을 보기 위한 task-specific auxiliary metric으로 유지하였다. Mean Flow EPE는 기준 I2V 출력의 optical flow와 refinement 결과의 optical flow 간 차이를 나타내며, Flow Mag Ratio는 기준 영상 대비 움직임 크기가 얼마나 증폭되거나 감소했는지를 나타낸다. Flow Mag Ratio는 1에 가까울수록 기준 영상의 움직임 크기와 유사한 것으로 해석한다.

VE-Bench QA는 공식 checkpoint를 사용할 수 없어 사용하지 않았다. 본 평가는 실제 물리 정합성을 직접 주장하지 않으며, Flow 기반 지표도 물리 정확성이 아니라 기준 영상의 동역학 보존 관점에서만 해석한다.
