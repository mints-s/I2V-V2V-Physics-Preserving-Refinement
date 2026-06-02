# Architecture Specification

## Name Candidate

DyRef-I2V: Dynamics-preserving Refinement Head for Frozen I2V Backbones

## Overall Structure

```text
Input image I and prompt P
↓
Frozen I2V backbone F
↓
Stage-1 video V0 or latent z0
↓
Dynamics extractor E_dyn
  - optical flow
  - optional mask / centroid trajectory
↓
Output refinement head H_ref
↓
Final video V_hat
```

The frozen I2V backbone is not modified. Its Stage-1 output is treated as a physics-induced motion prior, not physical ground truth. The output refinement head improves visual/spatio-temporal quality while being constrained by Stage-1 dynamics preservation.

## Variant A: Video-Space Head

```text
V0 = F(I, P)
V_hat = H_ref(V0, Flow(V0), I)
```

In this variant, the frozen I2V backbone first generates a Stage-1 video `V0`. A dynamics extractor computes optical flow or related motion features from `V0`. The refinement head receives the Stage-1 video, dynamics features, and optionally the input image, then predicts the final refined video `V_hat`.

This variant is recommended first because it is easier to implement and can reuse existing Stage-1 outputs. It also allows direct use of current pilot evidence from RealWonder and VEnhancer outputs.

## Variant B: Latent-Space Head

```text
z0 = F_latent(I, P)
z_hat = H_ref(z0, dyn_features)
V_hat = Decoder(z_hat)
```

In this variant, the refinement head is inserted before VAE decoding or another final rendering stage. The head modifies latent features rather than RGB video frames. This may provide stronger integration with the I2V model but requires access to model internals and careful compatibility with the decoder.

Latent-space refinement is more difficult and should be kept as future work unless the frozen I2V backbone exposes stable latent interfaces.

## Why This Is More Than a Pipeline

This direction is more than "I2V output + external V2V post-processing" for three reasons.

First, the head has an explicit refinement objective rather than only applying a generic enhancement model. Second, the head uses Stage-1 dynamics as a preservation constraint through flow or trajectory-based losses. Third, the module is designed as an output-side adaptation component attached to a frozen I2V backbone.

The goal is not simply upscaling. The goal is dynamics-preserving output-side adaptation for frozen I2V backbones.
