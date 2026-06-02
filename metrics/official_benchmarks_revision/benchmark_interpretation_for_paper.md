# 논문용 공식 벤치마크 해석

## 실행 상태

- VBench는 `imaging_quality`와 `motion_smoothness`를 정상 실행했다.
- DOVER는 fused overall no-reference quality score를 12개 target video 전체에 대해 정상 실행했다.
- VE-Bench QA는 실행하지 못했다. 공식 README가 Google Drive checkpoint 폴더를 요구하며, 필요한 checkpoint가 `/root/realwonder_test/benchmark_repos/VE-Bench/ckpts`에 없었다. 따라서 `failed_missing_official_checkpoints`로 기록했다.
- Flow EPE와 Flow Mag Ratio는 기존 결과를 복사해 보존했으며, 새 generation이나 training은 수행하지 않았다.

## 각 지표의 의미

- VBench Imaging: 생성 비디오의 imaging quality를 측정하는 공식/인정 벤치마크 지표이다.
- VBench Motion Smoothness: temporal/motion smoothness를 측정하는 VBench 지표이다.
- DOVER Overall: no-reference video quality score이며, 입력 비디오만으로 지각적 품질을 평가한다.
- VE-Bench QA: source-refined relation quality에 가까운 보조 지표로 볼 수 있으나, 원래 text-driven video editing 평가용이므로 본 논문의 주 지표로 해석하면 안 된다.
- Flow EPE / Flow Mag Ratio: task-specific Stage-1 dynamics preservation proxy이다. 물리적 정확성 자체를 증명하는 지표가 아니다.

## 주요 결과 해석

DyRefHead v2는 Stage-1 대비 VBench Imaging에서 소폭 상승했다. 다만 DOVER Overall은 Stage-1보다 낮아졌으므로, 공식 품질 지표 전반에서 일관된 향상을 보였다고 쓰면 안 된다. Motion Smoothness는 모든 방법이 0.994 근처로 매우 비슷하며, 차이를 강하게 해석하기 어렵다.

VEnhancer n30은 VBench Imaging에서 가장 높은 값을 보였다. 반면 Stage-1 dynamics preservation proxy에서는 Mean Flow EPE가 0.2782로 DyRefHead v2의 0.1883보다 크고, Flow Mag Ratio도 3.4906으로 1에서 크게 벗어난다. 따라서 VEnhancer는 시각 품질 지표에서는 강하지만 Stage-1 motion/dynamics와의 편차가 커지는 trade-off로 해석하는 것이 안전하다.

DyRefHead v2는 VEnhancer n30보다 Mean Flow EPE가 낮고 Flow Mag Ratio가 1에 더 가까워, Stage-1 dynamics preservation proxy 관점에서는 drift가 작다고 말할 수 있다. 다만 이는 optical-flow 기반 proxy이며 true physical correctness를 의미하지 않는다.

## 안전한 논문 문장

- "Official video quality metrics are used to complement task-specific Stage-1 dynamics preservation proxies."
- "DyRefHead improves the Stage-1 dynamics preservation proxy relative to VEnhancer while retaining competitive video quality scores."
- "VEnhancer achieves the strongest VBench Imaging score but shows larger deviation from the Stage-1 motion proxy."
- "Flow-based metrics are used as Stage-1 dynamics preservation proxies, not as direct evidence of physical correctness."

## 피해야 할 문장

- "Flow EPE proves physical correctness."
- "VE-Bench proves physics preservation."
- "DyRefHead is universally better than VEnhancer."
- "DyRefHead perfectly preserves dynamics."
