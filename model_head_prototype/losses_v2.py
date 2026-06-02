"""Improved lightweight losses for DyRefHead v2."""

from __future__ import annotations

import torch
from torch.nn import functional as F


DEFAULT_WEIGHTS = {
    "visual": 1.0,
    "edge": 0.5,
    "temporal_delta": 0.2,
    "identity": 0.05,
}


def _check_video(video: torch.Tensor, name: str) -> None:
    if video.ndim != 5:
        raise ValueError(f"Expected {name} shaped B, C, T, H, W, got {tuple(video.shape)}")


def visual_l1_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    return F.l1_loss(pred, target)


def spatial_gradient_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """Match simple x/y finite-difference gradients per video frame."""

    _check_video(pred, "pred")
    _check_video(target, "target")
    pred_dx = pred[..., :, 1:] - pred[..., :, :-1]
    target_dx = target[..., :, 1:] - target[..., :, :-1]
    pred_dy = pred[..., 1:, :] - pred[..., :-1, :]
    target_dy = target[..., 1:, :] - target[..., :-1, :]
    return F.l1_loss(pred_dx, target_dx) + F.l1_loss(pred_dy, target_dy)


def temporal_delta_preservation_loss(pred: torch.Tensor, ref: torch.Tensor) -> torch.Tensor:
    """Preserve Stage-1 frame-to-frame deltas without computing optical flow."""

    _check_video(pred, "pred")
    _check_video(ref, "ref")
    if pred.shape[2] < 2:
        return pred.new_tensor(0.0)
    pred_delta = pred[:, :, 1:] - pred[:, :, :-1]
    ref_delta = ref[:, :, 1:] - ref[:, :, :-1]
    return F.l1_loss(pred_delta, ref_delta)


def identity_first_frame_loss(pred: torch.Tensor, ref: torch.Tensor) -> torch.Tensor:
    _check_video(pred, "pred")
    _check_video(ref, "ref")
    return F.l1_loss(pred[:, :, 0], ref[:, :, 0])


def total_loss_v2(
    pred: torch.Tensor,
    target: torch.Tensor,
    ref: torch.Tensor,
    weights: dict[str, float] | None = None,
) -> tuple[torch.Tensor, dict[str, torch.Tensor]]:
    loss_weights = DEFAULT_WEIGHTS.copy()
    if weights is not None:
        loss_weights.update(weights)

    loss_visual = visual_l1_loss(pred, target)
    loss_edge = spatial_gradient_loss(pred, target)
    loss_temporal_delta = temporal_delta_preservation_loss(pred, ref)
    loss_identity = identity_first_frame_loss(pred, ref)
    loss_total = (
        loss_weights["visual"] * loss_visual
        + loss_weights["edge"] * loss_edge
        + loss_weights["temporal_delta"] * loss_temporal_delta
        + loss_weights["identity"] * loss_identity
    )
    return loss_total, {
        "visual": loss_visual,
        "edge": loss_edge,
        "temporal_delta": loss_temporal_delta,
        "identity": loss_identity,
    }
