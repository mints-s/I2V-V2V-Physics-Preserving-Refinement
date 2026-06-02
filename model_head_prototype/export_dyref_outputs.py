"""Export DyRefHead proof-of-concept videos from Stage-1 inputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch

from dyref_head import DyRefHead
from video_dataset import DEFAULT_SCENES, ROOT, read_video_tensor


CHECKPOINT_PATH = Path(__file__).resolve().parent / "checkpoints" / "dyref_overfit.pt"
OUTPUT_DIR = ROOT / "outputs" / "v2v" / "dyref_head"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", "--ckpt", dest="checkpoint", default=str(CHECKPOINT_PATH))
    parser.add_argument("--train-size", "--train_size", dest="train_size", type=int, default=None)
    parser.add_argument("--max-frames", "--max_frames", dest="max_frames", type=int, default=None)
    parser.add_argument("--output-dir", "--output_dir", dest="output_dir", default=str(OUTPUT_DIR))
    parser.add_argument("--fps", type=float, default=16)
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
    checkpoint = torch.load(args.checkpoint, map_location=args.device)
    config = checkpoint.get("config", {})
    train_size = args.train_size if args.train_size is not None else int(config.get("train_size", 128))
    max_frames = args.max_frames if args.max_frames is not None else int(config.get("max_frames", 32))

    model = DyRefHead(
        in_channels=int(config.get("in_channels", 3)),
        hidden_channels=int(config.get("hidden_channels", 32)),
        num_blocks=int(config.get("num_blocks", 3)),
        upsample=bool(config.get("upsample", False)),
    ).to(args.device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    stage1_dir = ROOT / "outputs" / "normalized" / "stage1"
    output_dir = Path(args.output_dir)
    with torch.no_grad():
        for scene in DEFAULT_SCENES:
            input_path = stage1_dir / f"{scene}.mp4"
            input_video = read_video_tensor(input_path, max_frames=max_frames, resize=train_size)
            pred = model(input_video.unsqueeze(0).to(args.device)).squeeze(0).clamp(0.0, 1.0)
            output_path = output_dir / f"{scene}.mp4"
            write_video(output_path, pred, fps=args.fps)
            print(f"wrote={output_path} shape={tuple(pred.shape)}")


if __name__ == "__main__":
    main()
