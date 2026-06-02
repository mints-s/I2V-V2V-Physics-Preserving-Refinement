"""One-step DyRefHead v2 data, loss, and backward check."""

from __future__ import annotations

import argparse

import torch
from torch.utils.data import DataLoader

from dyref_head_v2 import DyRefHeadV2
from losses_v2 import total_loss_v2
from video_dataset import PairedVideoDataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--train_size", type=int, default=256)
    parser.add_argument("--max_frames", type=int, default=64)
    parser.add_argument("--channels", type=int, default=48)
    parser.add_argument("--num_blocks", type=int, default=6)
    parser.add_argument("--residual_scale", type=float, default=0.5)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def print_cuda(prefix: str) -> None:
    if torch.cuda.is_available():
        print(f"{prefix}_cuda_allocated_gb={torch.cuda.memory_allocated() / (1024**3):.3f}")
        print(f"{prefix}_cuda_reserved_gb={torch.cuda.memory_reserved() / (1024**3):.3f}")
        print(f"{prefix}_cuda_peak_allocated_gb={torch.cuda.max_memory_allocated() / (1024**3):.3f}")


def main() -> None:
    args = parse_args()
    torch.manual_seed(0)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    dataset = PairedVideoDataset(train_size=args.train_size, max_frames=args.max_frames)
    loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
    batch = next(iter(loader))

    input_video = batch["input"].to(args.device)
    target_video = batch["target"].to(args.device)
    model = DyRefHeadV2(
        channels=args.channels,
        num_blocks=args.num_blocks,
        residual_scale=args.residual_scale,
    ).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    print(f"dataset_size={len(dataset)}")
    print(f"input_shape={tuple(input_video.shape)}")
    print(f"target_shape={tuple(target_video.shape)}")
    print_cuda("before")

    output = model(input_video)
    loss_total, parts = total_loss_v2(output, target_video, input_video)

    optimizer.zero_grad(set_to_none=True)
    loss_total.backward()
    optimizer.step()

    print(f"output_shape={tuple(output.shape)}")
    print(f"loss_total={loss_total.item():.6f}")
    print(f"loss_visual={parts['visual'].item():.6f}")
    print(f"loss_edge={parts['edge'].item():.6f}")
    print(f"loss_temporal_delta={parts['temporal_delta'].item():.6f}")
    print(f"loss_identity={parts['identity'].item():.6f}")
    print("backward_ok=True")
    print_cuda("after")


if __name__ == "__main__":
    main()
