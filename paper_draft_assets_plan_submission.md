# Submission Assets Plan

제출용 2~3쪽 버전에서는 그림과 표를 최소화하여 핵심 메시지를 선명하게 전달한다.

## Figure 1. Architecture Figure

삽입 위치:

```text
4. 제안 방법
  4.2 DyRefHead 구조 직후
```

포함 요소:

- Frozen I2V backbone
- Stage-1 output as physics-induced motion prior
- DyRefHead residual video-space output refinement
- VEnhancer n30 as pseudo visual target during training
- Lightweight dynamics-aware losses:
  - temporal-delta preservation
  - first-frame identity
  - visual/detail losses

Caption 후보:

```text
Frozen I2V backbone 뒤에 DyRefHead를 결합한 출력부 정제 구조. Stage-1 output은 physics-induced motion prior로 사용되며, DyRefHead는 pseudo visual target과 Stage-1 dynamics preservation objective를 함께 사용해 제한된 residual correction을 학습한다.
```

## Table 1. Main Result Table

삽입 위치:

```text
6. 결과 및 분석
  6.1 정량 결과
```

사용 파일:

```text
metrics/final_dyref_paper_ready/table_main_results.md
metrics/final_dyref_paper_ready/summary_by_method.csv
```

포함 방법:

- `stage1_baseline`
- `venhancer_n30`
- `dyref_head_v2_e20_256`
- `dyref_head_v3_edge075_temp015_e20_256`

강조 메시지:

- VEnhancer n30: highest visual/detail proxy, highest drift
- DyRefHead v2: representative balanced result
- DyRefHead v3: ablation showing stronger magnitude stabilization but weaker visual gain

## Figure 2. Representative Contact Sheet

삽입 위치:

```text
6. 결과 및 분석
  6.2 DyRefHead v2 대표 결과 이후
```

본문에는 대표 scene 1개만 삽입한다.

권장 대표 파일:

```text
metrics/final_dyref_paper_ready/scene01_stage1_venhancer_v2_v3.jpg
```

보조자료 또는 appendix 후보:

```text
metrics/final_dyref_paper_ready/scene02_stage1_venhancer_v2_v3.jpg
metrics/final_dyref_paper_ready/scene03_stage1_venhancer_v2_v3.jpg
```

Figure 구성:

- Rows:
  - stage1_baseline
  - venhancer_n30
  - dyref_head_v2_e20_256
  - dyref_head_v3_edge075_temp015_e20_256
- Columns:
  - 0.5s
  - 1.5s
  - 2.5s
  - 3.5s

Caption 후보:

```text
대표 scene contact sheet. VEnhancer n30은 강한 시각적 보정을 제공하지만 Stage-1 dynamics drift가 크며, DyRefHead v2는 더 제한된 visual gain을 보이지만 Stage-1 dynamics prior에서 덜 벗어나는 균형적 출력을 제공한다. v3는 dynamics magnitude 안정화 ablation으로 사용된다.
```

## v2/v3 Ablation Discussion

삽입 위치:

```text
6. 결과 및 분석
  6.3 v2/v3 Ablation
```

핵심 수치:

```text
v2:
  mean_sharpness=299.5439
  mean_flow_epe=0.1883
  flow_mag_ratio=1.6971

v3:
  mean_sharpness=287.8850
  mean_flow_epe=0.1901
  flow_mag_ratio=1.5899
```

핵심 문장:

```text
v3는 flow magnitude ratio를 v2보다 1에 가깝게 만들지만, sharpness가 낮아진다. 이는 dynamics magnitude stabilization을 강화하는 것이 visual gain을 항상 높이지는 않음을 보여준다.
```

## Limitations Placement

제출용 본문에서는 별도 limitation 섹션을 길게 두지 않고 결론 마지막 문단에 압축 삽입한다.

포함해야 할 항목:

- only 3 scenes
- VEnhancer n30 is pseudo-target, not ground truth
- flow metrics measure Stage-1 dynamics preservation, not physical correctness
- DyRefHead is video-space proof-of-concept, not latent-space integration
- full perceptual/human evaluation remains future work
