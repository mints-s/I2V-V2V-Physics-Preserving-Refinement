# Claim Safety Checklist

## Safe Claims

- DyRefHead v2 improves the sharpness proxy over Stage-1 baseline in the tested three-scene proof-of-concept.
- DyRefHead v2 reduces flow drift proxies compared to VEnhancer n30 in the 256x256 evaluation.
- VEnhancer n30 provides stronger visual gain but also larger drift from Stage-1 motion proxies.
- DyRefHead v3 suggests that stronger flow magnitude stabilization can reduce visual gain.
- The results indicate a visual gain-dynamics drift trade-off in output-space refinement.
- Stage-1 can be used as a physics-induced motion prior for lightweight dynamics-aware refinement.

## Unsafe Claims

- The model achieves physical ground truth.
- The method guarantees true physical correctness.
- The method perfectly preserves motion or dynamics.
- DyRefHead is globally optimal.
- DyRefHead is a complete model for physics-aware video generation.
- VEnhancer n30 is a ground-truth video.
- Stage-1 is a ground-truth physical trajectory.

## Terms To Use

- Stage-1 dynamics preservation
- physics-induced motion prior
- frozen I2V backbone
- trainable output refinement head
- pseudo visual target
- visual gain-dynamics drift trade-off
- lightweight dynamics proxy
- proof-of-concept

## Terms To Avoid

- physical ground truth
- true physical correctness
- perfect preservation
- globally optimal
- complete model
- guaranteed physics
- ground-truth video target
- exact dynamics recovery
