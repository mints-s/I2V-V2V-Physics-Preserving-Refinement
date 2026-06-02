"""Shape smoke test for DyRefHead."""

from __future__ import annotations

import torch

from dyref_head import DyRefHead


def main() -> None:
    video = torch.randn(2, 3, 5, 32, 48)
    model = DyRefHead(in_channels=3, hidden_channels=8, num_blocks=1)
    output = model(video)

    assert output.shape == video.shape, f"Expected {tuple(video.shape)}, got {tuple(output.shape)}"
    print(f"shape_ok input={tuple(video.shape)} output={tuple(output.shape)}")


if __name__ == "__main__":
    main()
