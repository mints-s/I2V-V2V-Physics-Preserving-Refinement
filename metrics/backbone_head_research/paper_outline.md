# Paper Outline

## 1. 서론

- I2V 모델은 입력 이미지와 프롬프트로부터 시간적 동역학을 생성한다.
- Stage-1 출력은 품질 한계가 있을 수 있으며 output refinement가 필요하다.
- 그러나 refinement는 I2V-generated motion prior를 변경할 수 있다.
- 본 연구는 frozen I2V backbone + dynamics-preserving output refinement head를 제안한다.

## 2. 관련 연구

- V2V / video enhancement.
- Video super-resolution and temporal consistency.
- High-resolution I2V generation.
- Frozen backbone / adapter-based video restoration.
- 본 연구의 차별점: output refinement for frozen I2V backbones under Stage-1 dynamics preservation.

## 3. 제안 구조

- DyRef-I2V: Dynamics-preserving Refinement Head for Frozen I2V Backbones.
- Frozen I2V backbone `F`.
- Stage-1 video `V0` 또는 latent `z0`.
- Dynamics extractor `E_dyn`.
- Output refinement head `H_ref`.
- Video-space head를 우선 구현하고 latent-space head는 future work로 둔다.

## 4. 출력 정제 목적 함수

- `L_total = L_visual + lambda_flow L_flow + lambda_temp L_temporal + lambda_id L_identity`.
- `L_flow`는 Stage-1 optical flow 또는 motion prior를 보존한다.
- Optional terms: `L_traj`, `L_mask`.
- 목적은 true physical correctness가 아니라 Stage-1 dynamics preservation이다.

## 5. 파일럿 실험 및 분석

- RealWonder Stage-1 outputs.
- VEnhancer strength sweep as output-head strength ablation evidence.
- 3-scene average: Stage-1 sharpness `198.99`, `venhancer_n30` sharpness `559.55`.
- `venhancer_n30` drift: `mean_flow_epe=0.2796`, `flow_mag_ratio=4.6502`.
- Interpretation: visual gain exists, but dynamics drift is non-zero.

## 6. 한계 및 향후 구현

- 현재는 trainable output head가 완성된 상태가 아니다.
- Existing VEnhancer results are pilot evidence.
- 다음 단계는 video-space DyRefHead training.
- Latent-space head는 더 강하지만 모델 내부 접근이 필요하다.
- 더 많은 physics-sensitive scenes와 정성 평가가 필요하다.

## 7. 결론

- 본 연구는 단순 upscaling이나 external post-processing이 아니라 frozen I2V backbone의 output-side adaptation을 목표로 한다.
- Stage-1 dynamics preservation을 고려한 output refinement head가 핵심 방향이다.
- Pilot results motivate the need for dynamics-preserving refinement objective.
