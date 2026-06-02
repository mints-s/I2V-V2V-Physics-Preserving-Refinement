# Efficiency Benchmark Summary

Hardware: NVIDIA H200 NVL.

Input videos: 64 frames, 16 fps, 4 seconds.

VEnhancer condition: `noise_aug=30`, `steps=15`, `solver_mode=fast`, `target_fps=16`, `up_scale=1`.
Note that VEnhancer internally adjusts 512x512 inputs to 1174x1174 in this setup.

## Main Resident-Model Results

These timings exclude model loading and include video decode/preprocess, model inference, and mp4 writing.

| method | input/output condition | videos | mean sec/video | max sec/video | mean peak VRAM | max peak VRAM |
|---|---|---:|---:|---:|---:|---:|
| dyref_head_v2_e20_256 | 256x256 DyRefHead output | 3 | 2.0877 | 2.2735 | 4.6281 GiB | 4.6437 GiB |
| dyref_head_v3_edge075_temp015_e20_256 | 256x256 DyRefHead output | 3 | 1.9246 | 2.0085 | 4.6281 GiB | 4.6437 GiB |
| dyref_head_v2_e20_512input | 512x512 DyRefHead output | 3 | 7.9405 | 8.2102 | 18.5031 GiB | 18.5656 GiB |
| venhancer_n30 | 512x512 input, internal 1174x1174 processing | 3 | 1066.8113 | 1156.3768 | 36.3850 GiB | 37.1176 GiB |

## Load-Time Split

| method | model load seconds | amortized sec/video with load | single-video sec with load |
|---|---:|---:|---:|
| dyref_head_v2_e20_256 | 1.2040 | 2.4891 | 3.2973 |
| dyref_head_v3_edge075_temp015_e20_256 | 1.1457 | 2.3065 | 3.1542 |
| dyref_head_v2_e20_512input | 0.9610 | 8.2608 | 9.1575 |
| venhancer_n30 | 39.6509 | 1080.0282 | 1106.4622 |

For VEnhancer, `model_load_seconds` is from the second resident-model run that processed scene02 and scene03. The scene01 run was measured before load-time tracking was added, so the 3-scene resident-model average uses all three inference timings, while the load split uses the measured VEnhancer load time from the later run.

## Speed Ratios

Using resident-model mean sec/video:

| comparison | speed ratio |
|---|---:|
| venhancer_n30 / dyref_head_v2_e20_256 | 510.99x |
| venhancer_n30 / dyref_head_v2_e20_512input | 134.35x |

## Warm-Up Note

DyRefHead measurements run one unrecorded warm-up inference before timing.

For VEnhancer, a strict 3-scene warm-up-excluded result would require one additional discarded VEnhancer generation before measuring all three scenes, which was not run here because it would add roughly one more VEnhancer video generation. In the second resident-model VEnhancer run, scene03 is the warmed-pass proxy after scene02 has already executed in the same loaded process:

| method | warmed-pass proxy | sec/video | peak VRAM |
|---|---|---:|---:|
| venhancer_n30 | scene03 after scene02 in same process | 1014.8036 | 37.1176 GiB |

## Caveat

During these runs, `nvidia-smi` reported pre-existing GPU memory occupancy and high utilization from processes shown as `[Not Found]`. The benchmark values should therefore be treated as practical pipeline timings on the current machine state, not isolated hardware peak-performance numbers.
