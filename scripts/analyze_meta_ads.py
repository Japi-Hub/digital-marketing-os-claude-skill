#!/usr/bin/env python3
"""Analyze Meta Ads CSV/XLSX exports and produce a decision-ready JSON summary."""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from utils.column_mapping import META_ADS_COLUMN_ALIASES as COLUMN_ALIASES
from utils.metrics import calculate_metrics  # noqa: F401

MINIMUM_COLUMNS = {"spend", "impressions", "clicks", "leads", "conversions"}
SPEND_ALIASES = COLUMN_ALIASES["spend"]


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    original = {str(col).lower().strip(): col for col in df.columns}
    rename_map = {}

    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            key = alias.lower().strip()
            if key in original:
                rename_map[original[key]] = canonical
                break

    return df.rename(columns=rename_map)


def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate that the normalized Meta Ads dataframe has enough data to analyze."""
    if df.empty:
        print("ERROR: The file has no rows. Nothing to analyze.", file=sys.stderr)
        sys.exit(1)

    recognized = MINIMUM_COLUMNS.intersection(set(df.columns))
    if not recognized:
        print("ERROR: No recognized columns found after normalization.", file=sys.stderr)
        print(f"       Columns in file: {list(df.columns)}", file=sys.stderr)
        print("       At least one of these is required: spend, impressions, clicks, leads, conversions", file=sys.stderr)
        print("       Check that you are uploading a Meta Ads export.", file=sys.stderr)
        sys.exit(1)

    if "spend" not in df.columns:
        print("ERROR: Column 'spend' not found. This column is required for all analysis.", file=sys.stderr)
        print(f"       Recognized aliases: {', '.join(SPEND_ALIASES)}", file=sys.stderr)
        print("       Check your export settings in Meta Ads Manager.", file=sys.stderr)
        sys.exit(1)

    spend_numeric = pd.to_numeric(
        df["spend"].astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.replace("%", "", regex=False),
        errors="coerce"
    ).fillna(0)

    if spend_numeric.sum() == 0:
        print(
            "WARNING: Column 'spend' found but total spend is 0. Analysis will proceed but results may not be meaningful.",
            file=sys.stderr,
        )


def classify_row(row: pd.Series, benchmarks: dict) -> dict:
    spend = float(row.get("spend", 0) or 0)
    ctr = float(row.get("ctr", 0) or 0)
    cpa = float(row.get("cpa", 0) or 0)
    frequency = float(row.get("frequency", 0) or 0)
    leads = float(row.get("leads", 0) or 0)
    conversions = float(row.get("conversions", 0) or 0)
    roas = float(row.get("roas", 0) or 0)

    flags = []
    decision = "maintain"
    priority = "medium"

    if spend <= 0:
        return {"decision": "insufficient_data", "priority": "low", "flags": ["no_spend"], "reason": "No spend detected."}

    if frequency >= benchmarks["fatigue_frequency"] and ctr < benchmarks["min_ctr"]:
        flags.append("possible_creative_fatigue")
        decision = "refresh_creative"
        priority = "high"

    if ctr and ctr < benchmarks["min_ctr"]:
        flags.append("low_ctr")
        decision = "test_new_hook_or_creative"
        priority = "high"

    if cpa and cpa > benchmarks["max_cpa"]:
        flags.append("high_cost_per_result")
        decision = "reduce_or_restructure"
        priority = "high"

    if leads > 0 and conversions == 0:
        flags.append("lead_quality_or_sales_problem")
        decision = "investigate_funnel_after_lead"
        priority = "high"

    if roas >= benchmarks["good_roas"] and conversions > 0:
        flags.append("strong_roas")
        decision = "scale_carefully"
        priority = "high"

    if ctr >= benchmarks["good_ctr"] and cpa and cpa <= benchmarks["target_cpa"]:
        flags.append("efficient_traffic")
        decision = "maintain_or_scale"
        priority = "high"

    return {
        "decision": decision,
        "priority": priority,
        "flags": flags,
        "reason": "; ".join(flags) if flags else "Performance is within acceptable range."
    }


def summarize(df: pd.DataFrame) -> dict:
    summary = {
        "rows": len(df),
        "total_spend": float(df["spend"].sum()) if "spend" in df else None,
        "total_impressions": int(df["impressions"].sum()) if "impressions" in df else None,
        "total_clicks": int(df["clicks"].sum()) if "clicks" in df else None,
        "total_leads": int(df["leads"].sum()) if "leads" in df else None,
        "total_conversions": int(df["conversions"].sum()) if "conversions" in df else None,
        "total_revenue": float(df["revenue"].sum()) if "revenue" in df else None,
    }

    if summary.get("total_spend") and summary.get("total_clicks"):
        summary["blended_cpc"] = summary["total_spend"] / summary["total_clicks"]
    if summary.get("total_impressions") and summary.get("total_clicks"):
        summary["blended_ctr"] = summary["total_clicks"] / summary["total_impressions"] * 100
    if summary.get("total_spend") and summary.get("total_leads"):
        summary["blended_cpl"] = summary["total_spend"] / summary["total_leads"]
    if summary.get("total_revenue") and summary.get("total_spend"):
        summary["blended_roas"] = summary["total_revenue"] / summary["total_spend"]

    return summary


def read_table(input_path: Path) -> pd.DataFrame:
    if not input_path.exists():
        print(f"ERROR: File not found: '{input_path}'", file=sys.stderr)
        sys.exit(1)

    if input_path.suffix.lower() not in [".csv", ".xlsx", ".xls"]:
        print(f"ERROR: Unsupported file format '{input_path.suffix}'. Use CSV or XLSX.", file=sys.stderr)
        sys.exit(1)

    try:
        if input_path.suffix.lower() in [".xlsx", ".xls"]:
            return pd.read_excel(input_path)
        return pd.read_csv(input_path)
    except pd.errors.EmptyDataError:
        print("ERROR: The file is empty or cannot be parsed as a table.", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"ERROR: Could not read file '{input_path}': {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Meta Ads export")
    parser.add_argument("input_file")
    parser.add_argument("--output", default="meta_ads_analysis.json")
    parser.add_argument("--target-cpa", type=float, default=25.0)
    parser.add_argument("--max-cpa", type=float, default=40.0)
    parser.add_argument("--min-ctr", type=float, default=0.8)
    parser.add_argument("--good-ctr", type=float, default=1.5)
    parser.add_argument("--fatigue-frequency", type=float, default=3.0)
    parser.add_argument("--good-roas", type=float, default=2.0)
    args = parser.parse_args()

    df = read_table(Path(args.input_file))
    df = normalize_columns(df)
    validate_dataframe(df)
    df = calculate_metrics(df)

    benchmarks = {
        "target_cpa": args.target_cpa,
        "max_cpa": args.max_cpa,
        "min_ctr": args.min_ctr,
        "good_ctr": args.good_ctr,
        "fatigue_frequency": args.fatigue_frequency,
        "good_roas": args.good_roas,
    }

    items = []
    for _, row in df.iterrows():
        item = row.to_dict()
        item["analysis"] = classify_row(row, benchmarks)
        items.append(item)

    output = {
        "summary": summarize(df),
        "benchmarks_used": benchmarks,
        "available_columns": list(df.columns),
        "items": items,
    }

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"Analysis saved to {args.output}")


if __name__ == "__main__":
    main()
