#!/usr/bin/env python3
"""Run flow preservation and quality proxy metrics for configured experiments."""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/experiments.csv")
    return parser.parse_args()


def run_command(command: list[str]) -> None:
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    args = parse_args()
    config_path = ROOT / args.config

    with config_path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            scene = row["scene"]
            seed = row["seed"]
            method = row["v2v_method"]
            stage1 = ROOT / row["stage1_video"]
            refined = ROOT / row["refined_video"]

            if not stage1.exists() or not refined.exists():
                print(f"Skipping {scene} seed{seed} {method}: missing stage1 or refined video")
                continue

            prefix = f"{scene}_seed{seed}_{method}"
            flow_out = ROOT / "metrics" / f"{prefix}_flow.csv"
            quality_out = ROOT / "metrics" / f"{prefix}_quality.csv"

            run_command(
                [
                    sys.executable,
                    "scripts/flow_preservation_metric.py",
                    "--stage1",
                    str(stage1),
                    "--refined",
                    str(refined),
                    "--out",
                    str(flow_out),
                ]
            )
            run_command(
                [
                    sys.executable,
                    "scripts/video_quality_proxy.py",
                    "--video",
                    str(refined),
                    "--out",
                    str(quality_out),
                ]
            )


if __name__ == "__main__":
    main()
