"""Minimal overfit training for DyRefHead on three paired videos."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import torch
from torch.utils.data import DataLoader

from dyref_head import DyRefHead
from losses import identity_first_frame_loss, temporal_smoothness_loss, visual_l1_loss
from video_dataset import PairedVideoDataset


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_PATH = Path(__file__).resolve().parent / "checkpoints" / "dyref_overfit.pt"
LOG_PATH = Path(__file__).resolve().parent / "logs" / "train_dyref_overfit.csv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--train-size", "--train_size", dest="train_size", type=int, default=128)
    parser.add_argument("--max-frames", "--max_frames", dest="max_frames", type=int, default=32)
    parser.add_argument("--batch-size", "--batch_size", dest="batch_size", type=int, default=1)
    parser.add_argument("--hidden-channels", type=int, default=32)
    parser.add_argument("--num-blocks", type=int, default=3)
    parser.add_argument("--out-ckpt", "--out_ckpt", dest="out_ckpt", default=str(CHECKPOINT_PATH))
    parser.add_argument("--log-csv", "--log_csv", dest="log_csv", default=str(LOG_PATH))
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    torch.manual_seed(0)

    dataset = PairedVideoDataset(train_size=args.train_size, max_frames=args.max_frames)
    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)

    model = DyRefHead(
        in_channels=3,
        hidden_channels=args.hidden_channels,
        num_blocks=args.num_blocks,
        upsample=False,
    ).to(args.device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)

    lambda_visual = 1.0
    lambda_temp = 0.05
    lambda_id = 0.1
    # TODO: Add flow preservation loss once a lightweight flow estimator or
    # precomputed Stage-1/refined flow cache is wired into this prototype.

    log_path = Path(args.log_csv)
    checkpoint_path = Path(args.out_ckpt)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    with log_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["epoch", "step", "scene", "loss_total", "loss_visual", "loss_temp", "loss_id"],
        )
        writer.writeheader()

        global_step = 0
        for epoch in range(1, args.epochs + 1):
            for batch in loader:
                input_video = batch["input"].to(args.device)
                target_video = batch["target"].to(args.device)

                pred = model(input_video).clamp(0.0, 1.0)
                loss_visual = visual_l1_loss(pred, target_video)
                loss_temp = temporal_smoothness_loss(pred)
                loss_id = identity_first_frame_loss(pred, input_video)
                loss_total = (
                    lambda_visual * loss_visual
                    + lambda_temp * loss_temp
                    + lambda_id * loss_id
                )

                optimizer.zero_grad(set_to_none=True)
                loss_total.backward()
                optimizer.step()

                global_step += 1
                scene = ",".join(batch["scene"])
                row = {
                    "epoch": epoch,
                    "step": global_step,
                    "scene": scene,
                    "loss_total": loss_total.item(),
                    "loss_visual": loss_visual.item(),
                    "loss_temp": loss_temp.item(),
                    "loss_id": loss_id.item(),
                }
                writer.writerow(row)
                print(
                    f"epoch={epoch:03d} step={global_step:04d} scene={scene} "
                    f"total={loss_total.item():.6f} visual={loss_visual.item():.6f} "
                    f"temp={loss_temp.item():.6f} id={loss_id.item():.6f}",
                    flush=True,
                )

    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "config": {
                "in_channels": 3,
                "hidden_channels": args.hidden_channels,
                "num_blocks": args.num_blocks,
                "upsample": False,
                "train_size": args.train_size,
                "max_frames": args.max_frames,
            },
        },
        checkpoint_path,
    )
    print(f"saved_checkpoint={checkpoint_path}")
    print(f"saved_log={log_path}")


if __name__ == "__main__":
    main()
