# Figure Caption Candidates

## Architecture Figure

DyRefHead pipeline overview. A frozen I2V backbone produces a Stage-1 video that is treated as a physics-induced motion prior. A trainable video-space residual refinement head then predicts bounded RGB corrections, supervised by a pseudo visual target while constrained by lightweight Stage-1 dynamics preservation losses.

## Main Result Table

Main 256x256 evaluation comparing Stage-1 baseline, VEnhancer n30, DyRefHead v2, and DyRefHead v3. DyRefHead v2 improves sharpness over Stage-1 while reducing flow drift proxies relative to VEnhancer n30, showing a balanced proof-of-concept refinement result.

## Contact Sheet Comparison

Qualitative comparison across sampled timestamps. Stage-1 provides the motion prior, VEnhancer n30 provides stronger visual enhancement with larger dynamics drift, and DyRefHead variants demonstrate output-space refinement under Stage-1 dynamics-aware constraints.

## v2/v3 Ablation Result

Loss-weight ablation between DyRefHead v2 and v3. Increasing edge/detail emphasis with weaker temporal-delta weighting improves flow magnitude stability in v3 but reduces sharpness relative to v2, illustrating the visual gain-dynamics drift trade-off.
