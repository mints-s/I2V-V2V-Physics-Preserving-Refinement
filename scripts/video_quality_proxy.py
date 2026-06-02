#!/usr/bin/env python3
"""Quick visual proxy metrics for a video."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--video", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=512)
    parser.add_argument("--height", type=int, default=512)
    parser.add_argument("--max_frames", type=int, default=64)
    return parser.parse_args()


def read_gray_frames(path: str, width: int, height: int, max_frames: int) -> list[np.ndarray]:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")

    frames: list[np.ndarray] = []
    try:
        while len(frames) < max_frames:
            ok, frame = cap.read()
            if not ok:
                break
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
    finally:
        cap.release()

    if not frames:
        raise RuntimeError(f"No frames found in video: {path}")
    return frames


def main() -> None:
    args = parse_args()
    frames = read_gray_frames(args.video, args.width, args.height, args.max_frames)

    sharpness = [float(cv2.Laplacian(frame, cv2.CV_64F).var()) for frame in frames]
    frame_diffs = [
        float(np.mean(cv2.absdiff(frames[index], frames[index + 1])))
        for index in range(len(frames) - 1)
    ]

    row = {
        "num_frames": len(frames),
        "mean_sharpness": float(np.mean(sharpness)),
        "std_sharpness": float(np.std(sharpness)),
        "mean_frame_diff": float(np.mean(frame_diffs)) if frame_diffs else 0.0,
        "std_frame_diff": float(np.std(frame_diffs)) if frame_diffs else 0.0,
    }

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    main()
