"""Lightweight losses for the DyRef-I2V prototype.

No optical flow is estimated here. Flow tensors are assumed to be precomputed by
an external flow estimator.
"""

from __future__ import annotations

import torch
from torch.nn import functional as F


def visual_l1_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Basic visual reconstruction loss for pseudo-target supervision."""

    return F.l1_loss(pred, target)


def temporal_smoothness_loss(video: torch.Tensor) -> torch.Tensor:
    """Penalize large frame-to-frame changes to reduce flicker."""

    if video.ndim != 5:
        raise ValueError(f"Expected B, C, T, H, W video tensor, got shape {tuple(video.shape)}")
    if video.shape[2] < 2:
        return video.new_tensor(0.0)
    return (video[:, :, 1:] - video[:, :, :-1]).abs().mean()


def flow_preservation_loss(flow_pred: torch.Tensor, flow_ref: torch.Tensor) -> torch.Tensor:
    """Preserve Stage-1 dynamics using precomputed optical flow tensors."""

    return F.mse_loss(flow_pred, flow_ref)


def identity_first_frame_loss(pred: torch.Tensor, ref: torch.Tensor) -> torch.Tensor:
    """Keep the first refined frame close to the input or Stage-1 first frame."""

    if pred.ndim != 5 or ref.ndim != 5:
        raise ValueError("Expected pred and ref tensors shaped B, C, T, H, W")
    return F.l1_loss(pred[:, :, 0], ref[:, :, 0])
