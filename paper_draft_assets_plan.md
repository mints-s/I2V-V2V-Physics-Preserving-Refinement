# Paper Draft Assets Plan

이 문서는 `paper_draft_dyref_v1.md`에 figure/table asset을 어디에 삽입할지 정리한다.

## 1. Architecture Figure

삽입 위치:

```text
4. 제안 방법
  4.2 DyRefHead 구조 직후
```

내용:

- Frozen I2V backbone
- Stage-1 output as physics-induced motion prior
- DyRefHead residual video-space refinement
- VEnhancer n30 as pseudo visual target during training
- Loss branches:
  - visual L1
  - spatial gradient/detail
  - temporal-delta preservation
  - first-frame identity

권장 caption:

```text
DyRefHead pipeline overview. A frozen I2V backbone produces a Stage-1 video that is treated as a physics-induced motion prior. A trainable video-space residual refinement head predicts bounded RGB corrections, supervised by a pseudo visual target while constrained by lightweight Stage-1 dynamics preservation losses.
```

## 2. Main Result Table

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

표에 포함할 방법:

- `stage1_baseline`
- `venhancer_n30`
- `dyref_head_v2_e20_256`
- `dyref_head_v3_edge075_temp015_e20_256`

강조할 메시지:

- VEnhancer n30: highest sharpness, highest drift
- DyRefHead v2: balanced representative result
- DyRefHead v3: flow magnitude stabilization ablation

## 3. Scene Contact Sheet Figure

삽입 위치:

```text
6. 결과 및 분석
  6.2 VEnhancer n30 분석 이후 또는 6.3 DyRefHead v2 분석 이후
```

사용 파일:

```text
metrics/final_dyref_paper_ready/scene01_stage1_venhancer_v2_v3.jpg
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

권장 caption:

```text
Qualitative comparison across sampled timestamps. Stage-1 provides the motion prior, VEnhancer n30 provides stronger visual enhancement with larger dynamics drift, and DyRefHead variants demonstrate output-space refinement under Stage-1 dynamics-aware constraints.
```

## 4. v2/v3 Ablation Discussion

삽입 위치:

```text
6. 결과 및 분석
  6.4 DyRefHead v3 Ablation 분석
  6.5 Visual Gain-Dynamics Drift Trade-off
```

사용 파일:

```text
metrics/final_dyref_paper_ready/dyref_v2_v3_comparison.md
metrics/final_dyref_paper_ready/summary_detail.csv
```

핵심 비교:

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

해석:

- v3는 flow_mag_ratio를 v2보다 1에 가깝게 만든다.
- 하지만 sharpness는 v2보다 낮다.
- 이는 dynamics magnitude stabilization을 강화하는 것이 visual gain을 항상 높이지는 않음을 보여준다.
- 따라서 v3는 대표 방법이 아니라 ablation으로 배치한다.
