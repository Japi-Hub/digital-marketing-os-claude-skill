#!/usr/bin/env python3
"""Compare two Meta Ads exports and summarize metric changes."""

import argparse
import json
from pathlib import Path

import pandas as pd

from analyze_meta_ads import normalize_columns, calculate_metrics, read_table, summarize


def pct_change(current: float, previous: float):
    if previous == 0:
        return None
    return ((current - previous) / previous) * 100


def compare_summaries(previous: dict, current: dict) -> dict:
    keys = sorted(set(previous.keys()) | set(current.keys()))
    comparison = {}

    for key in keys:
        prev = previous.get(key)
        curr = current.get(key)
        if isinstance(prev, (int, float)) and isinstance(curr, (int, float)):
            comparison[key] = {
                "previous": prev,
                "current": curr,
                "absolute_change": curr - prev,
                "pct_change": pct_change(curr, prev),
            }

    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two Meta Ads exports")
    parser.add_argument("previous_file")
    parser.add_argument("current_file")
    parser.add_argument("--output", default="meta_ads_period_comparison.json")
    args = parser.parse_args()

    previous_df = calculate_metrics(normalize_columns(read_table(Path(args.previous_file))))
    current_df = calculate_metrics(normalize_columns(read_table(Path(args.current_file))))

    previous_summary = summarize(previous_df)
    current_summary = summarize(current_df)

    output = {
        "previous_summary": previous_summary,
        "current_summary": current_summary,
        "changes": compare_summaries(previous_summary, current_summary),
    }

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"Period comparison saved to {args.output}")


if __name__ == "__main__":
    main()
