# VBench Dynamic Degree Notes

- Repository: `/root/realwonder_test/benchmark_repos/VBench`
- Commit: `45e79ec14e69a2187202c675d2dbce1a71843d53`
- Environment: `vbench_eval`
- Requested dimension: `dynamic_degree`
- Input videos: existing 256x256 symlink folders under `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_inputs/`
- Raw output directory: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_dynamic_degree_raw/`
- Parsed CSV: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_dynamic_degree_results.csv`

## Support Check

The installed VBench repository contains `dynamic_degree` support in `vbench/dynamic_degree.py`, `evaluate.py`, and the repository dimension lists. The implementation uses RAFT to classify whether each video contains sufficient motion, then reports the average moving-video ratio.

## Exact Command Attempted

```bash
cd /root/realwonder_test/benchmark_repos/VBench
conda run -n vbench_eval python evaluate.py --dimension dynamic_degree --videos_path /root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_inputs/stage1_baseline --mode=custom_input --output_path /root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_dynamic_degree_raw/stage1_baseline_dynamic_degree
```

## Result

`dynamic_degree` did not complete. VBench attempted to download the RAFT checkpoint archive, but failed during checkpoint extraction because the `unzip` executable was unavailable in the runtime environment.

Relevant error:

```text
File /root/.cache/vbench/raft_model/models/raft-things.pth does not exist. Downloading...
FileNotFoundError: [Errno 2] No such file or directory: 'unzip'
ERROR conda.cli.main_run:execute(142): `conda run python evaluate.py --dimension dynamic_degree ...` failed.
```

Because the failure occurred before method-level evaluation and the task requested no unrelated benchmark hacks, the remaining methods were not evaluated with `dynamic_degree`.

## Paper Decision

Exclude VBench Dynamic Degree from the main paper table for the current revision. Use the fallback reduced table with VBench Imaging, VBench Motion Smoothness, Mean Flow EPE, and Flow Mag Ratio.
