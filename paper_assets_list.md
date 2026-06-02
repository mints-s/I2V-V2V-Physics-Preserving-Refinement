# Paper Assets List

## Tables

1. `metrics/pipeline_ready/table_candidate_sweep.md`
   - Suggested placement: Section 4, after the Scene01 candidate sweep description.
   - Purpose: Show the candidate-level visual gain and dynamics drift metrics used to select `venhancer_n30`.
   - Caption suggestion: "Scene01 VEnhancer 후보 sweep 결과. Stage-1 baseline 대비 sharpness 2배 조건을 만족한 후보 중 `mean_flow_epe`가 가장 낮은 `venhancer_n30`을 선택했다."

2. `metrics/pipeline_ready/table_final_3scene.md`
   - Suggested placement: Section 4, after the 3-scene average result paragraph.
   - Purpose: Summarize the final comparison between `stage1_baseline` and selected `venhancer_n30`.
   - Caption suggestion: "3개 scene 평균 결과. `venhancer_n30`은 sharpness를 증가시켰지만 non-zero Stage-1 dynamics drift를 도입했다."

## Figures

1. `metrics/pipeline_ready/scene01_venhancer_fine_sweep_contact_sheet.jpg`
   - Suggested placement: Section 4, near the Scene01 candidate sweep discussion.
   - Purpose: Qualitative comparison across VEnhancer strengths for scene01.
   - Caption suggestion: "Scene01 VEnhancer fine sweep contact sheet. Refinement strength 변화에 따른 visual gain과 dynamics drift를 정성적으로 비교한다."

2. `metrics/pipeline_ready/scene01_stage1_vs_selected_contact_sheet.jpg`
   - Suggested placement: Section 4, qualitative review paragraph.
   - Purpose: Compare Stage-1 baseline and selected `venhancer_n30` for scene01.
   - Caption suggestion: "Scene01 Stage-1 baseline과 selected `venhancer_n30` 비교."

3. `metrics/pipeline_ready/scene02_stage1_vs_selected_contact_sheet.jpg`
   - Suggested placement: Section 4, qualitative review paragraph.
   - Purpose: Compare Stage-1 baseline and selected `venhancer_n30` for scene02.
   - Caption suggestion: "Scene02 Stage-1 baseline과 selected `venhancer_n30` 비교."

4. `metrics/pipeline_ready/scene03_stage1_vs_selected_contact_sheet.jpg`
   - Suggested placement: Section 4, qualitative review paragraph.
   - Purpose: Compare Stage-1 baseline and selected `venhancer_n30` for scene03.
   - Caption suggestion: "Scene03 Stage-1 baseline과 selected `venhancer_n30` 비교."

## Qualitative Review Form

1. `metrics/pipeline_ready/qualitative_review_template.csv`
   - Suggested use: External qualitative evaluation sheet.
   - Review fields: `action_meaning_preserved_1_5`, `trajectory_consistency_1_5`, `contact_timing_preserved_1_5`, `local_response_preserved_1_5`, `subject_stability_1_5`, `visual_gain_1_5`, `overall_judgment`, `notes`.
