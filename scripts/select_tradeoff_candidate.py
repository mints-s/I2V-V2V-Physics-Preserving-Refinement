#!/usr/bin/env python3
"""Select the best tested VEnhancer trade-off candidate."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path


CANDIDATES = {
    "venhancer_n30",
    "venhancer_n50",
    "venhancer_n70",
    "venhancer_n100",
    "venhancer_n200",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="metrics/summary_detail.csv")
    parser.add_argument("--out", default="metrics/selected_tradeoff_candidate.txt")
    return parser.parse_args()


def as_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def normalize(values: list[float], value: float) -> float:
    lo = min(values)
    hi = max(values)
    if math.isclose(lo, hi):
        return 0.0
    return (value - lo) / (hi - lo)


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    rows: list[dict[str, str]] = list(csv.DictReader(input_path.open()))

    baseline_rows = [row for row in rows if row["v2v_method"] == "stage1_baseline"]
    if not baseline_rows:
        raise RuntimeError("stage1_baseline row not found")
    baseline = baseline_rows[0]
    baseline_sharpness = as_float(baseline, "mean_sharpness")

    candidates = [row for row in rows if row["v2v_method"] in CANDIDATES]
    if not candidates:
        raise RuntimeError("No candidate rows found")

    threshold = 2.0 * baseline_sharpness
    eligible = [row for row in candidates if as_float(row, "mean_sharpness") >= threshold]

    if eligible:
        selected = sorted(
            eligible,
            key=lambda row: (
                as_float(row, "mean_flow_epe"),
                abs(as_float(row, "flow_mag_ratio") - 1.0),
            ),
        )[0]
        reason = (
            "Selected the eligible candidate with mean_sharpness at least 2.0x "
            "the Stage-1 baseline and the lowest mean_flow_epe."
        )
    else:
        sharpness_gains = [
            as_float(row, "mean_sharpness") / baseline_sharpness for row in candidates
        ]
        flow_epes = [as_float(row, "mean_flow_epe") for row in candidates]
        log_ratios = [abs(math.log(as_float(row, "flow_mag_ratio"))) for row in candidates]

        scored: list[tuple[float, dict[str, str]]] = []
        for row, gain, epe, log_ratio in zip(candidates, sharpness_gains, flow_epes, log_ratios):
            score = normalize(sharpness_gains, gain) - normalize(flow_epes, epe) - normalize(
                log_ratios, log_ratio
            )
            scored.append((score, row))
        selected = sorted(scored, key=lambda item: item[0], reverse=True)[0][1]
        reason = (
            "No candidate reached 2.0x baseline sharpness; selected the highest fallback score."
        )

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as f:
        f.write("best trade-off candidate among tested VEnhancer strengths\n")
        f.write(f"selected_method: {selected['v2v_method']}\n")
        f.write(f"reason: {reason}\n")
        f.write(f"baseline_sharpness: {baseline_sharpness:.6f}\n")
        f.write(f"selected_sharpness: {as_float(selected, 'mean_sharpness'):.6f}\n")
        f.write(f"selected_mean_flow_epe: {as_float(selected, 'mean_flow_epe'):.6f}\n")
        f.write(f"selected_flow_mag_ratio: {as_float(selected, 'flow_mag_ratio'):.6f}\n")
        f.write("\nall_candidates:\n")
        f.write("method,mean_flow_epe,flow_mag_ratio,mean_sharpness,mean_frame_diff\n")
        for row in sorted(candidates, key=lambda item: item["v2v_method"]):
            f.write(
                "{method},{epe:.6f},{ratio:.6f},{sharpness:.6f},{frame_diff:.6f}\n".format(
                    method=row["v2v_method"],
                    epe=as_float(row, "mean_flow_epe"),
                    ratio=as_float(row, "flow_mag_ratio"),
                    sharpness=as_float(row, "mean_sharpness"),
                    frame_diff=as_float(row, "mean_frame_diff"),
                )
            )
    print(f"Wrote {out_path}")
    print(f"selected_method={selected['v2v_method']}")


if __name__ == "__main__":
    main()
