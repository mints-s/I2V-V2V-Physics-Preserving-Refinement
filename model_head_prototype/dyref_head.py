"""Prototype dynamics-preserving output refinement head.

This module is a lightweight placeholder for the paper concept. It is meant to
sit after a frozen I2V backbone output and predict a small residual correction
in video space.
"""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class ConvBlock3D(nn.Module):
    """Small 3D convolution block for video tensors shaped B, C, T, H, W."""

    def __init__(self, channels: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv3d(channels, channels, kernel_size=3, padding=1),
            nn.GroupNorm(num_groups=1, num_channels=channels),
            nn.SiLU(inplace=True),
            nn.Conv3d(channels, channels, kernel_size=3, padding=1),
            nn.GroupNorm(num_groups=1, num_channels=channels),
            nn.SiLU(inplace=True),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class DyRefHead(nn.Module):
    """Residual output refinement head for frozen I2V backbone outputs.

    Input shape: B, C, T, H, W
    Output shape: B, C, T, H, W

    The default configuration keeps the same spatial and temporal resolution.
    Optional upsampling can be enabled for experiments, but the first prototype
    should use same-resolution refinement.
    """

    def __init__(
        self,
        in_channels: int = 3,
        hidden_channels: int = 32,
        num_blocks: int = 3,
        upsample: bool = False,
    ) -> None:
        super().__init__()
        self.upsample = upsample
        self.input_proj = nn.Conv3d(in_channels, hidden_channels, kernel_size=3, padding=1)
        self.blocks = nn.Sequential(*[ConvBlock3D(hidden_channels) for _ in range(num_blocks)])
        self.output_proj = nn.Conv3d(hidden_channels, in_channels, kernel_size=3, padding=1)

        # Start near identity so the head initially behaves like a conservative
        # output-side adaptation module.
        nn.init.zeros_(self.output_proj.weight)
        nn.init.zeros_(self.output_proj.bias)

    def forward(self, video: torch.Tensor) -> torch.Tensor:
        if video.ndim != 5:
            raise ValueError(f"Expected B, C, T, H, W video tensor, got shape {tuple(video.shape)}")

        x = video
        if self.upsample:
            x = F.interpolate(x, scale_factor=(1, 2, 2), mode="trilinear", align_corners=False)

        features = self.input_proj(x)
        features = self.blocks(features)
        residual = self.output_proj(features)
        return x + residual
