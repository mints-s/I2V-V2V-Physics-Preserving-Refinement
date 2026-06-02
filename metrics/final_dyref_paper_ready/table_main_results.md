# Main Results

| method | role | mean_sharpness | mean_flow_epe | flow_mag_ratio | interpretation |
|---|---|---:|---:|---:|---|
| stage1_baseline | frozen I2V backbone output / motion prior | 279.5409 | 0.0000 | 1.0000 | Stage-1 serves as the physics-induced motion prior and reference dynamics. |
| venhancer_n30 | off-the-shelf pseudo-target | 364.3567 | 0.2782 | 3.4906 | High visual gain, but substantially higher drift from Stage-1 motion proxies. |
| dyref_head_v2_e20_256 | proposed representative head | 299.5439 | 0.1883 | 1.6971 | Balanced proof-of-concept: improves sharpness over Stage-1 while reducing drift relative to VEnhancer n30. |
| dyref_head_v3_edge075_temp015_e20_256 | loss ablation | 287.8850 | 0.1901 | 1.5899 | Better flow magnitude stability than v2, but weaker visual gain. |
