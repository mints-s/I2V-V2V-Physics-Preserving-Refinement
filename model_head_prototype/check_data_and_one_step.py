"""Check paired video loading and one DyRefHead optimization step."""

from __future__ import annotations

import torch
from torch.utils.data import DataLoader

from dyref_head import DyRefHead
from losses import identity_first_frame_loss, temporal_smoothness_loss, visual_l1_loss
from video_dataset import PairedVideoDataset


def main() -> None:
    torch.manual_seed(0)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    dataset = PairedVideoDataset(train_size=128, max_frames=32)
    print(f"dataset_size={len(dataset)}")

    sample = dataset[0]
    print(f"sample_scene={sample['scene']}")
    print(f"sample_input_shape={tuple(sample['input'].shape)}")
    print(f"sample_target_shape={tuple(sample['target'].shape)}")
    print(f"sample_input_range=({sample['input'].min().item():.6f}, {sample['input'].max().item():.6f})")
    print(f"sample_target_range=({sample['target'].min().item():.6f}, {sample['target'].max().item():.6f})")

    loader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)
    batch = next(iter(loader))
    input_video = batch["input"].to(device)
    target_video = batch["target"].to(device)
    print(f"batch_input_shape={tuple(input_video.shape)}")
    print(f"batch_target_shape={tuple(target_video.shape)}")

    model = DyRefHead(in_channels=3, hidden_channels=32, num_blocks=3).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)

    pred = model(input_video).clamp(0.0, 1.0)
    print(f"pred_shape={tuple(pred.shape)}")

    loss_visual = visual_l1_loss(pred, target_video)
    loss_temp = temporal_smoothness_loss(pred)
    loss_id = identity_first_frame_loss(pred, input_video)
    loss_total = loss_visual + 0.05 * loss_temp + 0.1 * loss_id

    optimizer.zero_grad(set_to_none=True)
    loss_total.backward()
    optimizer.step()

    print(f"loss_total={loss_total.item():.6f}")
    print(f"loss_visual={loss_visual.item():.6f}")
    print(f"loss_temporal={loss_temp.item():.6f}")
    print(f"loss_identity={loss_id.item():.6f}")
    print("backward_ok=True")


if __name__ == "__main__":
    main()
