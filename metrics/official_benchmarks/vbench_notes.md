# VBench Notes

- Repository: `/root/realwonder_test/benchmark_repos/VBench`
- Commit: `45e79ec14e69a2187202c675d2dbce1a71843d53`
- Environment: `vbench_eval`
- Output CSV: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_results.csv`
- Raw outputs: `/root/realwonder_test/i2v_v2v_physics/metrics/official_benchmarks/vbench_raw/`

## Install Commands

```bash
cd /root/realwonder_test/benchmark_repos
git clone https://github.com/Vchitect/VBench.git
conda create -n vbench_eval python=3.10 -y
conda run -n vbench_eval pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
conda run -n vbench_eval pip install -e /root/realwonder_test/benchmark_repos/VBench
conda run -n vbench_eval pip install --no-build-isolation -e /root/realwonder_test/benchmark_repos/VBench
conda run -n vbench_eval pip install 'setuptools<81'
```

The first editable install failed because build isolation could not import the already installed `torch`. The `--no-build-isolation` retry succeeded. `setuptools<81` was installed because VBench imported `pkg_resources`.

## Evaluation Commands

```bash
conda run -n vbench_eval python evaluate.py --dimension imaging_quality --videos_path <method_symlink_folder> --mode=custom_input --output_path <raw_output_dir>
conda run -n vbench_eval python evaluate.py --dimension motion_smoothness --videos_path <method_symlink_folder> --mode=custom_input --output_path <raw_output_dir>
```

## Status

- Succeeded: `imaging_quality`, `motion_smoothness`
- Not run: `aesthetic_quality`, `dynamic_degree`, `subject_consistency`, `background_consistency`

## Caveats

VBench reports both aggregate rows and per-video rows. The aggregate table uses the `ALL` rows returned by VBench for consistency with the benchmark output scale.
