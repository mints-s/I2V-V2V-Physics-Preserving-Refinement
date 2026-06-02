#!/usr/bin/env python3
"""Optical-flow based Stage-1 dynamics preservation metric.

This script compares motion fields from a Stage-1 video and a visually refined
video. It measures whether Stage-1 dynamics are preserved after refinement; it
does not measure true physical correctness or physical ground-truth accuracy.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage1", required=True, help="Path to normalized Stage-1 video")
    parser.add_argument("--refined", required=True, help="Path to normalized refined video")
    parser.add_argument("--out", required=True, help="Output CSV path")
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
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frames.append(gray)
    finally:
        cap.release()

    if len(frames) < 2:
        raise RuntimeError(f"Need at least 2 frames for optical flow: {path}")
    return frames


def farneback(prev_frame: np.ndarray, next_frame: np.ndarray) -> np.ndarray:
    return cv2.calcOpticalFlowFarneback(
        prev_frame,
        next_frame,
        None,
        pyr_scale=0.5,
        levels=3,
        winsize=15,
        iterations=3,
        poly_n=5,
        poly_sigma=1.2,
        flags=0,
    )


def summarize_pair(index: int, stage1_flow: np.ndarray, refined_flow: np.ndarray) -> dict[str, float | str]:
    diff = stage1_flow - refined_flow
    epe = np.linalg.norm(diff, axis=2)
    stage1_mag = np.linalg.norm(stage1_flow, axis=2)
    refined_mag = np.linalg.norm(refined_flow, axis=2)

    mean_stage1_mag = float(np.mean(stage1_mag))
    mean_refined_mag = float(np.mean(refined_mag))
    return {
        "frame_pair": str(index),
        "mean_flow_epe": float(np.mean(epe)),
        "median_flow_epe": float(np.median(epe)),
        "stage1_flow_mag": mean_stage1_mag,
        "refined_flow_mag": mean_refined_mag,
        "flow_mag_ratio": mean_refined_mag / (mean_stage1_mag + 1e-8),
    }


def main() -> None:
    args = parse_args()
    stage1_frames = read_gray_frames(args.stage1, args.width, args.height, args.max_frames)
    refined_frames = read_gray_frames(args.refined, args.width, args.height, args.max_frames)
    frame_count = min(len(stage1_frames), len(refined_frames))

    rows = []
    for index in range(frame_count - 1):
        stage1_flow = farneback(stage1_frames[index], stage1_frames[index + 1])
        refined_flow = farneback(refined_frames[index], refined_frames[index + 1])
        rows.append(summarize_pair(index, stage1_flow, refined_flow))

    fieldnames = [
        "frame_pair",
        "mean_flow_epe",
        "median_flow_epe",
        "stage1_flow_mag",
        "refined_flow_mag",
        "flow_mag_ratio",
    ]
    mean_row: dict[str, float | str] = {"frame_pair": "mean"}
    for name in fieldnames[1:]:
        mean_row[name] = float(np.mean([float(row[name]) for row in rows]))
    rows.append(mean_row)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    main()
