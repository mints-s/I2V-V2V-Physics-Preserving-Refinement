#!/usr/bin/env python3
"""Write ffprobe metadata for experiment videos."""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="metrics/video_metadata_summary.csv")
    return parser.parse_args()


def fps_to_float(value: str) -> float | str:
    if "/" not in value:
        try:
            return float(value)
        except ValueError:
            return value
    num, den = value.split("/", 1)
    try:
        den_f = float(den)
        return float(num) / den_f if den_f else value
    except ValueError:
        return value


def probe(path: Path) -> dict[str, object]:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=width,height,r_frame_rate,duration,nb_frames",
        "-of",
        "json",
        str(path),
    ]
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    return {
        "path": str(path),
        "width": stream.get("width", ""),
        "height": stream.get("height", ""),
        "fps": fps_to_float(str(stream.get("r_frame_rate", ""))),
        "duration": stream.get("duration", ""),
        "num_frames": stream.get("nb_frames", ""),
    }


def main() -> None:
    args = parse_args()
    patterns = [
        "outputs/normalized/stage1/*.mp4",
        "outputs/v2v/*/*.mp4",
        "outputs/normalized/v2v/*/*.mp4",
    ]
    paths: list[Path] = []
    for pattern in patterns:
        paths.extend(Path(".").glob(pattern))
    rows = [probe(path) for path in sorted(set(paths))]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=["path", "width", "height", "fps", "duration", "num_frames"]
        )
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
