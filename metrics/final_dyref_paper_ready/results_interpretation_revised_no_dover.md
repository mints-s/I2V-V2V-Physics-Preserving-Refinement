# 결과 해석

VBench Dynamic Degree는 평가를 시도했지만 현재 환경에서 완료되지 않았다. 실패 원인은 VBench가 RAFT checkpoint archive를 내려받은 뒤 압축 해제를 위해 호출하는 `unzip` 실행 파일이 없었기 때문이다. 따라서 현재 논문 본문에서는 VBench Imaging과 Motion Smoothness, 그리고 flow 기반 보조 지표를 사용한다.

VEnhancer n30은 VBench Imaging에서 가장 높은 값을 보이며 시각 품질 측면의 개선폭이 가장 크다. 그러나 Mean Flow EPE와 Flow Mag Ratio가 가장 크게 증가하여, 기준 I2V 출력 대비 움직임 이탈도 가장 크게 나타난다.

DyRefHead v2는 VEnhancer n30보다 시각 품질 개선폭은 작지만, 기준 영상 대비 동역학 이탈을 더 낮게 유지하였다. refined method만 비교하면 DyRefHead v2는 가장 낮은 Mean Flow EPE를 보인다.

Motion Smoothness 값의 차이는 매우 작으므로 과도하게 해석하지 않는다. 현재의 시간적 보존 해석은 주로 Mean Flow EPE와 Flow Mag Ratio에 근거한다.

DyRefHead v3는 ablation으로 해석한다. v3는 DyRefHead v2보다 Flow Mag Ratio가 1에 더 가까워 움직임 크기 보존 측면에서는 더 안정적이지만, VBench Imaging은 v2보다 낮다. 이 결과는 DyRefHead가 보편적으로 우월하다는 결론이 아니라, 시각 품질 개선과 기준 영상 대비 동역학 보존 사이의 trade-off를 조절할 수 있음을 보여준다.
