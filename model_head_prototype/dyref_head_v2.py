"""DyRefHead v2: video-space output refinement for frozen I2V backbones."""

from __future__ import annotations

import torch
from torch import nn


class ConvBlock3DV2(nn.Module):
    """Batch-size-safe 3D convolution block for B, C, T, H, W videos."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv3d(channels, channels, kernel_size=3, padding=1),
            nn.GroupNorm(num_groups=8 if channels % 8 == 0 else 1, num_channels=channels),
            nn.SiLU(inplace=True),
            nn.Conv3d(channels, channels, kernel_size=3, padding=1),
            nn.GroupNorm(num_groups=8 if channels % 8 == 0 else 1, num_channels=channels),
            nn.SiLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return x + self.net(x)


class DyRefHeadV2(nn.Module):
    """Residual video-space refinement head for frozen I2V backbone outputs.

    The input Stage-1 video is treated as a dynamics prior. This head predicts a
    same-resolution residual in RGB video space and keeps the update bounded by
    a configurable residual scale. It does not perform upscaling.
    """

    def __init__(
        self,
        in_channels: int = 3,
        channels: int = 48,
        num_blocks: int = 6,
        residual_scale: float = 0.5,
    ) -> None:
        super().__init__()
        self.residual_scale = residual_scale
        self.input_proj = nn.Sequential(
            nn.Conv3d(in_channels, channels, kernel_size=3, padding=1),
            nn.GroupNorm(num_groups=8 if channels % 8 == 0 else 1, num_channels=channels),
            nn.SiLU(inplace=True),
        )
        self.blocks = nn.Sequential(*[ConvBlock3DV2(channels) for _ in range(num_blocks)])
        self.output_proj = nn.Conv3d(channels, in_channels, kernel_size=3, padding=1)

        # Start close to identity so early training refines Stage-1 instead of
        # replacing its motion structure.
        nn.init.zeros_(self.output_proj.weight)
        nn.init.zeros_(self.output_proj.bias)

    def forward(self, video: torch.Tensor) -> torch.Tensor:
        if video.ndim != 5:
            raise ValueError(f"Expected B, C, T, H, W video tensor, got shape {tuple(video.shape)}")

        features = self.input_proj(video)
        features = self.blocks(features)
        residual = self.output_proj(features)
        return torch.clamp(video + self.residual_scale * residual, 0.0, 1.0)
