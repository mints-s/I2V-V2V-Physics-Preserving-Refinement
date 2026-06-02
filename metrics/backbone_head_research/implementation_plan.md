# Implementation Plan

## Level 1: No Training, Current Evidence

### Scope

Use the existing RealWonder Stage-1 outputs and VEnhancer strength sweep as output-head behavior analysis. Treat `n30`, `n50`, `n70`, `n100`, and `n200` as refinement strength ablation evidence rather than the final proposed model.

### Required Data

- Existing Stage-1 videos.
- Existing VEnhancer outputs.
- Existing metrics and contact sheets.

### Required Compute

No heavy generation or training is required. Only document analysis, metric reuse, and optional lightweight plotting are needed.

### Risk

The evidence is motivational rather than a complete model demonstration. Reviewers may ask for a trainable head implementation.

### Expected Contribution Strength

Suitable for a short paper, workshop paper, or proposal-style submission if framed carefully as pilot evidence for a new output-side architecture.

## Level 2: Trainable Video-Space Head

### Scope

Freeze the I2V backbone. Train `DyRefHead` on Stage-1 videos and pseudo-targets. Use a dynamics-preserving refinement objective such as:

```text
L_visual + lambda_flow L_flow + lambda_temp L_temporal
```

Compare the trained head against off-the-shelf VEnhancer and other enhancement baselines.

### Required Data

- Stage-1 I2V outputs from multiple physics-sensitive scenes.
- Pseudo-HR targets, enhanced targets, or paired higher-quality references.
- Precomputed optical flow for Stage-1 outputs and refined outputs.
- Optional masks or centroid trajectories.

### Required Compute

Moderate GPU compute for training a small 3D convolutional video-space head. No full I2V backbone training is required.

### Risk

Pseudo-target quality may bias the head toward generic enhancement. Flow loss may over-constrain refinement and reduce visual gain. A small dataset may lead to weak generalization.

### Expected Contribution Strength

Strongest practical next step. This can turn the current concept into a real model paper by demonstrating a trainable output refinement head with explicit Stage-1 dynamics preservation.

## Level 3: Latent-Space Head

### Scope

Insert the refinement head before VAE decoding or another final output stage. The head modifies latent features while respecting dynamics features extracted from Stage-1 latent or video-space motion.

### Required Data

- Access to I2V backbone latent tensors or decoder inputs.
- Stage-1 video outputs for flow/motion supervision.
- Training targets or pseudo-targets.

### Required Compute

Higher compute and engineering effort than Level 2. Requires model-internal access and compatibility with the I2V backbone decoder.

### Risk

Latent interface may be unstable or unavailable. Errors in latent modification can degrade generation quality. Integration with frozen backbone internals may be difficult.

### Expected Contribution Strength

Potentially high if successful, but best treated as future work after validating the video-space head.
