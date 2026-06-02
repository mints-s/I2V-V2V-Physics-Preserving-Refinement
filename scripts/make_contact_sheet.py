#!/usr/bin/env python3
"""Create a contact sheet from selected timestamps of multiple videos."""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--times", default="0.5,1.5,2.5,3.5")
    parser.add_argument("videos", nargs="+", help="label=path entries")
    return parser.parse_args()


def read_frame(path: Path, seconds: float) -> np.ndarray:
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 16.0
    frame_index = max(0, int(round(seconds * fps)))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not read frame {frame_index} from: {path}")
    return frame


def add_label(image: np.ndarray, text: str) -> np.ndarray:
    output = image.copy()
    cv2.rectangle(output, (0, 0), (output.shape[1], 28), (0, 0, 0), -1)
    cv2.putText(
        output,
        text,
        (8, 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.55,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return output


def main() -> None:
    args = parse_args()
    entries: list[tuple[str, Path]] = []
    for item in args.videos:
        if "=" not in item:
            raise ValueError(f"Expected label=path entry, got: {item}")
        label, path = item.split("=", 1)
        entries.append((label, Path(path)))

    times = [float(value) for value in args.times.split(",") if value]
    rows = []
    for label, path in entries:
        cells = []
        for seconds in times:
            frame = read_frame(path, seconds)
            frame = cv2.resize(frame, (256, 256), interpolation=cv2.INTER_AREA)
            cells.append(add_label(frame, f"{label}  t={seconds:.1f}s"))
        rows.append(np.concatenate(cells, axis=1))

    sheet = np.concatenate(rows, axis=0)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(out_path), sheet):
        raise RuntimeError(f"Could not write contact sheet: {out_path}")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
