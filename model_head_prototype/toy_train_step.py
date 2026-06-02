"""One-step random-tensor training smoke test for DyRefHead."""

from __future__ import annotations

import torch

from dyref_head import DyRefHead
from losses import (
    flow_preservation_loss,
    identity_first_frame_loss,
    temporal_smoothness_loss,
    visual_l1_loss,
)


def main() -> None:
    torch.manual_seed(0)

    batch, channels, frames, height, width = 2, 3, 4, 32, 32
    stage1_video = torch.randn(batch, channels, frames, height, width)
    pseudo_target = stage1_video + 0.05 * torch.randn_like(stage1_video)

    # Placeholder flow tensors shaped B, 2, T-1, H, W. In a real experiment,
    # these would be produced by an optical-flow estimator outside this file.
    flow_ref = torch.randn(batch, 2, frames - 1, height, width)
    flow_pred = flow_ref + 0.01 * torch.randn_like(flow_ref)

    model = DyRefHead(in_channels=channels, hidden_channels=16, num_blocks=2)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3)

    pred = model(stage1_video)
    loss_visual = visual_l1_loss(pred, pseudo_target)
    loss_temp = temporal_smoothness_loss(pred)
    loss_flow = flow_preservation_loss(flow_pred, flow_ref)
    loss_id = identity_first_frame_loss(pred, stage1_video)

    total = loss_visual + 0.1 * loss_temp + 0.5 * loss_flow + 0.2 * loss_id

    optimizer.zero_grad(set_to_none=True)
    total.backward()
    optimizer.step()

    print(f"loss_total={total.item():.6f}")
    print(f"loss_visual={loss_visual.item():.6f}")
    print(f"loss_temporal={loss_temp.item():.6f}")
    print(f"loss_flow={loss_flow.item():.6f}")
    print(f"loss_identity={loss_id.item():.6f}")


if __name__ == "__main__":
    main()
