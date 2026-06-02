# Contribution Definition

## One-Sentence Main Claim

This work proposes an output-side refinement structure for frozen I2V backbones that explicitly considers the trade-off between visual quality improvement and Stage-1 dynamics preservation.

## Final Contributions

### Contribution 1: Frozen I2V Backbone + Lightweight Output Refinement Head

본 연구는 frozen I2V backbone의 출력을 직접 수정하는 lightweight output refinement head 구조를 제안한다. 이 구조는 backbone 전체를 재학습하거나 고해상도 I2V framework를 새로 설계하는 대신, output-side adaptation으로 시공간 품질을 개선하는 방향을 취한다.

### Contribution 2: Dynamics-Preserving Refinement Objective

본 연구는 Stage-1 optical flow와 motion prior를 이용한 dynamics-preserving refinement objective를 정의한다. 이 objective는 output refinement head가 visual quality를 개선하면서도 Stage-1 dynamics preservation을 고려하도록 유도한다.

### Contribution 3: Visual Gain vs Stage-1 Dynamics Drift Evaluation

본 연구는 physics-sensitive I2V scenes에서 visual gain과 Stage-1 dynamics drift를 함께 평가하는 분석 프레임을 제시한다. 기존 VEnhancer strength sweep은 output-head strength ablation evidence로 재해석되며, refinement 강도와 dynamics drift 사이의 trade-off를 보여주는 pilot evidence로 사용된다.

## What This Paper Does NOT Claim

- True physical correctness를 보장한다고 주장하지 않는다.
- Stage-1 dynamics를 완벽하게 보존한다고 주장하지 않는다.
- Generated video enhancement 자체를 최초로 제안한다고 주장하지 않는다.
- Frozen backbone + adapter 구조 자체를 최초로 제안한다고 주장하지 않는다.
- 현재 pilot 결과만으로 완전한 trainable head가 이미 구현 및 검증되었다고 주장하지 않는다.

## Reviewer-Safe Contribution Wording

- "We propose a lightweight output refinement head for frozen I2V backbones under a Stage-1 dynamics preservation constraint."
- "The Stage-1 I2V output is treated as a physics-induced motion prior rather than physical ground truth."
- "Pilot VEnhancer strength sweep results motivate the need for a dynamics-preserving refinement objective."
- "We evaluate visual gain and dynamics drift jointly instead of reporting visual quality alone."

## Unsafe Contribution Wording to Avoid

- "We guarantee physical correctness."
- "Our method perfectly preserves physics."
- "We are the first to enhance generated videos."
- "This is globally optimal refinement."
- "This is simply video upscaling."
- "The VEnhancer sweep alone proves the proposed head."
