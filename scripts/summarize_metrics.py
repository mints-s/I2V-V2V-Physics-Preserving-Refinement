#!/usr/bin/env python3
"""Summarize per-experiment metric CSV files."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
METRICS_DIR = ROOT / "metrics"
CONFIG_PATH = ROOT / "configs" / "experiments.csv"
NAME_RE = re.compile(r"^(?P<scene>.+)_seed(?P<seed>[^_]+)_(?P<v2v_method>.+)_(?P<kind>flow|quality)\.csv$")
SUMMARY_COLUMNS = [
    "mean_flow_epe",
    "median_flow_epe",
    "flow_mag_ratio",
    "mean_sharpness",
    "mean_frame_diff",
]


def metadata(path: Path) -> dict[str, str] | None:
    match = NAME_RE.match(path.name)
    if not match:
        return None
    return match.groupdict()


def main() -> None:
    records: dict[tuple[str, str, str], dict[str, object]] = {}
    allowed_keys: set[tuple[str, str, str]] | None = None

    if CONFIG_PATH.exists():
        config = pd.read_csv(CONFIG_PATH, dtype={"scene": str, "seed": str, "v2v_method": str})
        allowed_keys = {
            (row.scene, row.seed, row.v2v_method)
            for row in config.itertuples(index=False)
        }

    for flow_path in METRICS_DIR.glob("*_flow.csv"):
        meta = metadata(flow_path)
        if meta is None:
            continue
        key = (meta["scene"], meta["seed"], meta["v2v_method"])
        if allowed_keys is not None and key not in allowed_keys:
            continue
        df = pd.read_csv(flow_path)
        mean_rows = df[df["frame_pair"].astype(str) == "mean"]
        if mean_rows.empty:
            continue
        record = records.setdefault(
            key,
            {"scene": meta["scene"], "seed": meta["seed"], "v2v_method": meta["v2v_method"]},
        )
        for column in ["mean_flow_epe", "median_flow_epe", "flow_mag_ratio"]:
            record[column] = float(mean_rows.iloc[0][column])

    for quality_path in METRICS_DIR.glob("*_quality.csv"):
        meta = metadata(quality_path)
        if meta is None:
            continue
        key = (meta["scene"], meta["seed"], meta["v2v_method"])
        if allowed_keys is not None and key not in allowed_keys:
            continue
        df = pd.read_csv(quality_path)
        if df.empty:
            continue
        record = records.setdefault(
            key,
            {"scene": meta["scene"], "seed": meta["seed"], "v2v_method": meta["v2v_method"]},
        )
        for column in ["mean_sharpness", "mean_frame_diff"]:
            record[column] = float(df.iloc[0][column])

    detail = pd.DataFrame(records.values())
    detail_path = METRICS_DIR / "summary_detail.csv"
    by_method_path = METRICS_DIR / "summary_by_method.csv"

    if detail.empty:
        detail.to_csv(detail_path, index=False)
        pd.DataFrame().to_csv(by_method_path, index=False)
        print("No metric files found to summarize.")
        return

    detail = detail.sort_values(["scene", "seed", "v2v_method"])
    detail.to_csv(detail_path, index=False)

    present_columns = [column for column in SUMMARY_COLUMNS if column in detail.columns]
    summary = detail.groupby("v2v_method")[present_columns].agg(["mean", "std"])
    summary.columns = [f"{metric}_{stat}" for metric, stat in summary.columns]
    summary = summary.reset_index()
    summary.to_csv(by_method_path, index=False)
    print(f"Wrote {detail_path}")
    print(f"Wrote {by_method_path}")


if __name__ == "__main__":
    main()
