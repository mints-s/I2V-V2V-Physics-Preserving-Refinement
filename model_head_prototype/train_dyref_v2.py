"""Train DyRefHead v2 on paired Stage-1 and VEnhancer n30 videos."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from dyref_head_v2 import DyRefHeadV2
from losses_v2 import total_loss_v2
from video_dataset import PairedVideoDataset


DEFAULT_CKPT = Path(__file__).resolve().parent / "checkpoints" / "dyref_v2_e20_256.pt"
DEFAULT_LOG = Path(__file__).resolve().parent / "logs" / "train_dyref_v2_e20_256.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--train_size", type=int, default=256)
    parser.add_argument("--max_frames", type=int, default=64)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--batch_size", type=int, default=1)
    parser.add_argument("--channels", type=int, default=48)
    parser.add_argument("--num_blocks", type=int, default=6)
    parser.add_argument("--residual_scale", type=float, default=0.5)
    parser.add_argument("--lambda_visual", type=float, default=1.0)
    parser.add_argument("--lambda_edge", type=float, default=0.5)
    parser.add_argument("--lambda_temporal_delta", type=float, default=0.2)
    parser.add_argument("--lambda_identity", type=float, default=0.05)
    parser.add_argument("--out_ckpt", default=str(DEFAULT_CKPT))
    parser.add_argument("--log_csv", default=str(DEFAULT_LOG))
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def cuda_report(prefix: str) -> None:
    if torch.cuda.is_available():
        allocated = torch.cuda.memory_allocated() / (1024**3)
        reserved = torch.cuda.memory_reserved() / (1024**3)
        peak = torch.cuda.max_memory_allocated() / (1024**3)
        print(f"{prefix}_cuda_allocated_gb={allocated:.3f}")
        print(f"{prefix}_cuda_reserved_gb={reserved:.3f}")
        print(f"{prefix}_cuda_peak_allocated_gb={peak:.3f}")


def main() -> None:
    args = parse_args()
    torch.manual_seed(0)
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    dataset = PairedVideoDataset(train_size=args.train_size, max_frames=args.max_frames)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)

    model = DyRefHeadV2(
        channels=args.channels,
        num_blocks=args.num_blocks,
        residual_scale=args.residual_scale,
    ).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    weights = {
        "visual": args.lambda_visual,
        "edge": args.lambda_edge,
        "temporal_delta": args.lambda_temporal_delta,
        "identity": args.lambda_identity,
    }

    out_ckpt = Path(args.out_ckpt)
    log_csv = Path(args.log_csv)
    out_ckpt.parent.mkdir(parents=True, exist_ok=True)
    log_csv.parent.mkdir(parents=True, exist_ok=True)

    cuda_report("before_training")
    with log_csv.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "epoch",
                "loss_total",
                "loss_visual",
                "loss_edge",
                "loss_temporal_delta",
                "loss_identity",
            ],
        )
        writer.writeheader()

        for epoch in range(1, args.epochs + 1):
            sums = {
                "loss_total": 0.0,
                "loss_visual": 0.0,
                "loss_edge": 0.0,
                "loss_temporal_delta": 0.0,
                "loss_identity": 0.0,
            }
            count = 0
            for batch in loader:
                input_video = batch["input"].to(args.device)
                target_video = batch["target"].to(args.device)

                pred = model(input_video)
                loss_total, parts = total_loss_v2(pred, target_video, input_video, weights=weights)

                optimizer.zero_grad(set_to_none=True)
                loss_total.backward()
                optimizer.step()

                values = {
                    "loss_total": loss_total.item(),
                    "loss_visual": parts["visual"].item(),
                    "loss_edge": parts["edge"].item(),
                    "loss_temporal_delta": parts["temporal_delta"].item(),
                    "loss_identity": parts["identity"].item(),
                }
                if any(math.isnan(value) for value in values.values()):
                    raise FloatingPointError(f"NaN loss detected at epoch {epoch}: {values}")
                for key, value in values.items():
                    sums[key] += value
                count += 1

            row = {"epoch": epoch}
            row.update({key: value / max(count, 1) for key, value in sums.items()})
            writer.writerow(row)
            print(
                "epoch={epoch:03d} total={loss_total:.6f} visual={loss_visual:.6f} "
                "edge={loss_edge:.6f} temporal_delta={loss_temporal_delta:.6f} "
                "identity={loss_identity:.6f}".format(**row),
                flush=True,
            )

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": {
                "channels": args.channels,
                "num_blocks": args.num_blocks,
                "residual_scale": args.residual_scale,
                "train_size": args.train_size,
                "max_frames": args.max_frames,
                "loss_weights": weights,
            },
        },
        out_ckpt,
    )
    cuda_report("after_training")
    print(f"saved_checkpoint={out_ckpt}")
    print(f"saved_log={log_csv}")


if __name__ == "__main__":
    main()
