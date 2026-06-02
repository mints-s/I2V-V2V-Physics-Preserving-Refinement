"""Benchmark resident-model refinement latency for DyRefHead and VEnhancer.

The benchmark measures one Stage-1 video -> refined mp4 pass after the model is
constructed. It includes video decode/preprocess and output encoding because
both refinement paths need those steps in the current pipeline.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path

import torch


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCENES = ("scene01_seed0", "scene02_seed0", "scene03_seed0")


def cuda_sync() -> None:
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def reset_peak_memory() -> None:
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.reset_peak_memory_stats()


def peak_memory_gib() -> float:
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.max_memory_allocated() / (1024**3)


def write_video(path: Path, video: torch.Tensor, fps: float) -> None:
    import imageio.v3 as iio

    path.parent.mkdir(parents=True, exist_ok=True)
    frames = video.detach().cpu().clamp(0.0, 1.0).permute(1, 2, 3, 0).numpy()
    frames_uint8 = (frames * 255.0).round().astype("uint8")
    iio.imwrite(path, frames_uint8, fps=fps, codec="libx264", pixelformat="yuv420p")


def load_dyref(args: argparse.Namespace):
    prototype_dir = ROOT / "model_head_prototype"
    sys.path.insert(0, str(prototype_dir))
    from dyref_head_v2 import DyRefHeadV2

    checkpoint = torch.load(args.ckpt, map_location=args.device)
    config = checkpoint.get("config", {})
    model = DyRefHeadV2(
        channels=args.channels if args.channels is not None else int(config.get("channels", 48)),
        num_blocks=args.num_blocks if args.num_blocks is not None else int(config.get("num_blocks", 6)),
        residual_scale=(
            args.residual_scale
            if args.residual_scale is not None
            else float(config.get("residual_scale", 0.5))
        ),
    ).to(args.device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, int(args.train_size or config.get("train_size", 256)), int(args.max_frames or config.get("max_frames", 64))


def run_dyref(args: argparse.Namespace, scenes: list[str]) -> tuple[list[dict[str, object]], float]:
    prototype_dir = ROOT / "model_head_prototype"
    sys.path.insert(0, str(prototype_dir))
    from video_dataset import read_video_tensor

    load_start = time.perf_counter()
    model, train_size, max_frames = load_dyref(args)
    cuda_sync()
    load_seconds = time.perf_counter() - load_start
    stage1_dir = Path(args.stage1_dir).resolve()
    output_dir = Path(args.output_dir)
    rows: list[dict[str, object]] = []

    # Warm one inference without recording, so timings reflect a resident model.
    warm_video = read_video_tensor(stage1_dir / f"{scenes[0]}.mp4", max_frames=max_frames, resize=train_size)
    with torch.no_grad():
        _ = model(warm_video.unsqueeze(0).to(args.device))
    cuda_sync()

    for scene in scenes:
        input_path = stage1_dir / f"{scene}.mp4"
        output_path = output_dir / args.method / f"{scene}.mp4"
        reset_peak_memory()
        cuda_sync()
        start = time.perf_counter()
        with torch.no_grad():
            input_video = read_video_tensor(input_path, max_frames=max_frames, resize=train_size)
            output = model(input_video.unsqueeze(0).to(args.device)).squeeze(0)
            cuda_sync()
            write_video(output_path, output, fps=args.fps)
        cuda_sync()
        seconds = time.perf_counter() - start
        rows.append(
            {
                "method": args.method,
                "scene": scene,
                "seconds_per_video": seconds,
                "frames": int(output.shape[1]),
                "height": int(output.shape[2]),
                "width": int(output.shape[3]),
                "fps_processed": float(output.shape[1]) / seconds,
                "peak_memory_gib": peak_memory_gib(),
                "output_path": str(output_path),
            }
        )
    return rows, load_seconds


def load_venhancer(args: argparse.Namespace):
    venhancer_root = Path(args.venhancer_root)
    sys.path.insert(0, str(venhancer_root))
    cwd = os.getcwd()
    os.chdir(venhancer_root)
    try:
        from enhance_a_video import VEnhancer

        model = VEnhancer(
            result_dir=str(Path(args.output_dir) / args.method),
            version="v2",
            model_path=args.model_path,
            solver_mode=args.solver_mode,
            steps=args.steps,
            guide_scale=args.cfg,
            s_cond=args.s_cond,
        )
    finally:
        os.chdir(cwd)
    return model, venhancer_root


def run_venhancer(args: argparse.Namespace, scenes: list[str]) -> tuple[list[dict[str, object]], float]:
    load_start = time.perf_counter()
    model, venhancer_root = load_venhancer(args)
    cuda_sync()
    load_seconds = time.perf_counter() - load_start
    stage1_dir = Path(args.stage1_dir).resolve()
    rows: list[dict[str, object]] = []

    for scene in scenes:
        input_path = stage1_dir / f"{scene}.mp4"
        scene_output_dir = Path(args.output_dir) / args.method / scene
        scene_output_dir.mkdir(parents=True, exist_ok=True)
        model.result_dir = str(scene_output_dir)
        reset_peak_memory()
        cuda_sync()
        start = time.perf_counter()
        cwd = os.getcwd()
        os.chdir(venhancer_root)
        try:
            result_stem = model.enhance_a_video(
                str(input_path),
                args.prompt,
                up_scale=args.up_scale,
                target_fps=args.target_fps,
                noise_aug=args.noise_aug,
            )
        finally:
            os.chdir(cwd)
        cuda_sync()
        seconds = time.perf_counter() - start
        output_path = Path(result_stem + ".mp4")
        rows.append(
            {
                "method": args.method,
                "scene": scene,
                "seconds_per_video": seconds,
                "frames": "",
                "height": "",
                "width": "",
                "fps_processed": "",
                "peak_memory_gib": peak_memory_gib(),
                "output_path": str(output_path),
            }
        )
    return rows, load_seconds


def write_rows(rows: list[dict[str, object]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "method",
        "scene",
        "seconds_per_video",
        "frames",
        "height",
        "width",
        "fps_processed",
        "peak_memory_gib",
        "output_path",
    ]
    with csv_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary(rows: list[dict[str, object]], summary_path: Path, load_seconds: float) -> None:
    seconds = [float(row["seconds_per_video"]) for row in rows]
    memory = [float(row["peak_memory_gib"]) for row in rows]
    payload = {
        "method": rows[0]["method"] if rows else "",
        "num_videos": len(rows),
        "model_load_seconds": load_seconds,
        "mean_seconds_per_video": sum(seconds) / len(seconds) if seconds else 0.0,
        "max_seconds_per_video": max(seconds) if seconds else 0.0,
        "amortized_seconds_per_video_with_load": (
            (load_seconds + sum(seconds)) / len(seconds) if seconds else 0.0
        ),
        "single_video_seconds_with_load": load_seconds + seconds[0] if seconds else 0.0,
        "mean_peak_memory_gib": sum(memory) / len(memory) if memory else 0.0,
        "max_peak_memory_gib": max(memory) if memory else 0.0,
    }
    summary_path.write_text(json.dumps(payload, indent=2) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", choices=("dyref", "venhancer"), required=True)
    parser.add_argument("--method", required=True)
    parser.add_argument("--scenes", nargs="+", default=list(DEFAULT_SCENES))
    parser.add_argument("--output_dir", default=str(ROOT / "metrics" / "efficiency_benchmark" / "outputs"))
    parser.add_argument("--stage1_dir", default=str(ROOT / "outputs" / "normalized" / "stage1"))
    parser.add_argument("--csv_path", default="")
    parser.add_argument("--summary_path", default="")
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")

    parser.add_argument("--ckpt", default=str(ROOT / "model_head_prototype" / "checkpoints" / "dyref_v2_e20_256.pt"))
    parser.add_argument("--train_size", type=int, default=None)
    parser.add_argument("--max_frames", type=int, default=None)
    parser.add_argument("--channels", type=int, default=None)
    parser.add_argument("--num_blocks", type=int, default=None)
    parser.add_argument("--residual_scale", type=float, default=None)
    parser.add_argument("--fps", type=float, default=16)

    parser.add_argument("--venhancer_root", default="/root/realwonder_test/v2v_repos/VEnhancer")
    parser.add_argument("--model_path", default="/root/realwonder_test/v2v_repos/VEnhancer/ckpts/venhancer_v2.pt")
    parser.add_argument("--prompt", default="a high quality physically plausible video with stable motion")
    parser.add_argument("--noise_aug", type=int, default=30)
    parser.add_argument("--target_fps", type=int, default=16)
    parser.add_argument("--up_scale", type=float, default=1)
    parser.add_argument("--solver_mode", default="fast")
    parser.add_argument("--steps", type=int, default=15)
    parser.add_argument("--cfg", type=float, default=7.5)
    parser.add_argument("--s_cond", type=float, default=8)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    rows, load_seconds = run_dyref(args, args.scenes) if args.backend == "dyref" else run_venhancer(args, args.scenes)
    base_dir = ROOT / "metrics" / "efficiency_benchmark"
    csv_path = Path(args.csv_path) if args.csv_path else base_dir / f"{args.method}.csv"
    summary_path = Path(args.summary_path) if args.summary_path else base_dir / f"{args.method}_summary.json"
    write_rows(rows, csv_path)
    write_summary(rows, summary_path, load_seconds)
    print(f"wrote_csv={csv_path}")
    print(f"wrote_summary={summary_path}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
