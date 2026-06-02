#!/usr/bin/env python3
"""Create a synthetic moving-square mp4 for pipeline smoke tests."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--fps", type=int, default=16)
    parser.add_argument("--duration", type=float, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    frame_count = max(2, int(round(args.fps * args.duration)))
    square_size = max(24, min(args.width, args.height) // 5)
    y0 = (args.height - square_size) // 2
    start_x = 16
    end_x = max(start_x, args.width - square_size - 16)

    writer = cv2.VideoWriter(
        str(out_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        args.fps,
        (args.width, args.height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not open writer for: {out_path}")

    try:
        for index in range(frame_count):
            alpha = index / max(1, frame_count - 1)
            x0 = int(round(start_x * (1.0 - alpha) + end_x * alpha))
            frame = np.full((args.height, args.width, 3), (235, 235, 225), dtype=np.uint8)
            cv2.rectangle(frame, (x0, y0), (x0 + square_size, y0 + square_size), (40, 120, 230), -1)
            cv2.circle(frame, (x0 + square_size // 2, y0 + square_size // 2), square_size // 5, (230, 80, 70), -1)
            writer.write(frame)
    finally:
        writer.release()


if __name__ == "__main__":
    main()
