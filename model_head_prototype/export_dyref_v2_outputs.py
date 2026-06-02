"""Export DyRefHead v2 videos from Stage-1 inputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from dyref_head_v2 import DyRefHeadV2
from video_dataset import DEFAULT_SCENES, ROOT, read_video_tensor


DEFAULT_CKPT = Path(__file__).resolve().parent / "checkpoints" / "dyref_v2_e20_256.pt"
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "v2v" / "dyref_head_v2_e20_256"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ckpt", default=str(DEFAULT_CKPT))
    parser.add_argument("--train_size", type=int, default=None)
    parser.add_argument("--max_frames", type=int, default=None)
    parser.add_argument("--output_dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--fps", type=float, default=16)
    parser.add_argument("--channels", type=int, default=None)
    parser.add_argument("--num_blocks", type=int, default=None)
    parser.add_argument("--residual_scale", type=float, default=None)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def write_video(path: Path, video: torch.Tensor, fps: float) -> None:
    import imageio.v3 as iio

    path.parent.mkdir(parents=True, exist_ok=True)
    frames = video.detach().cpu().clamp(0.0, 1.0).permute(1, 2, 3, 0).numpy()
    frames_uint8 = (frames * 255.0).round().astype("uint8")
    iio.imwrite(path, frames_uint8, fps=fps, codec="libx264", pixelformat="yuv420p")


def main() -> None:
    args = parse_args()
    checkpoint = torch.load(args.ckpt, map_location=args.device)
    config = checkpoint.get("config", {})
    train_size = args.train_size if args.train_size is not None else int(config.get("train_size", 256))
    max_frames = args.max_frames if args.max_frames is not None else int(config.get("max_frames", 64))

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

    output_dir = Path(args.output_dir)
    stage1_dir = ROOT / "outputs" / "normalized" / "stage1"
    with torch.no_grad():
        for scene in DEFAULT_SCENES:
            input_video = read_video_tensor(
                stage1_dir / f"{scene}.mp4",
                max_frames=max_frames,
                resize=train_size,
            )
            output = model(input_video.unsqueeze(0).to(args.device)).squeeze(0)
            output_path = output_dir / f"{scene}.mp4"
            write_video(output_path, output, fps=args.fps)
            print(f"wrote={output_path} shape={tuple(output.shape)}")


if __name__ == "__main__":
    main()
