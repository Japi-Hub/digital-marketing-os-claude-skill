#!/usr/bin/env python3
"""Analyze organic content CSV/XLSX reports and produce a decision-ready JSON summary."""

import argparse
import json
from pathlib import Path

import pandas as pd

from utils.column_mapping import CONTENT_COLUMN_ALIASES as COLUMN_ALIASES
from utils.metrics import numeric


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


def add_scores(df: pd.DataFrame) -> pd.DataFrame:
    df = numeric(df, ["reach", "views", "likes", "comments", "shares", "saves", "messages", "leads", "clicks"])

    engagement_cols = [c for c in ["likes", "comments", "shares", "saves"] if c in df.columns]
    if engagement_cols:
        df["engagement_total"] = df[engagement_cols].sum(axis=1)

    denominator = "reach" if "reach" in df.columns else "views" if "views" in df.columns else None

    if denominator and "engagement_total" in df.columns:
        df["engagement_rate"] = (df["engagement_total"] / df[denominator].replace(0, pd.NA)).fillna(0) * 100

    if denominator and "messages" in df.columns:
        df["message_rate"] = (df["messages"] / df[denominator].replace(0, pd.NA)).fillna(0) * 100

    if denominator and "leads" in df.columns:
        df["lead_rate"] = (df["leads"] / df[denominator].replace(0, pd.NA)).fillna(0) * 100

    score_parts = []
    for col, weight in [
        ("engagement_rate", 1),
        ("message_rate", 3),
        ("lead_rate", 5),
        ("saves", 2),
        ("shares", 2),
    ]:
        if col in df.columns:
            score_parts.append(df[col].rank(pct=True) * weight)

    if score_parts:
        df["content_score"] = sum(score_parts)

    return df


def grouped_insights(df: pd.DataFrame) -> dict:
    insights = {}

    for group_col in ["topic", "format", "platform"]:
        if group_col in df.columns and "content_score" in df.columns:
            agg = {"posts": (group_col, "count"), "avg_score": ("content_score", "mean")}
            if "engagement_rate" in df.columns:
                agg["avg_engagement"] = ("engagement_rate", "mean")
            if "leads" in df.columns:
                agg["total_leads"] = ("leads", "sum")
            if "messages" in df.columns:
                agg["total_messages"] = ("messages", "sum")

            grouped = df.groupby(group_col).agg(**agg).sort_values("avg_score", ascending=False).reset_index()
            insights[group_col] = grouped.to_dict(orient="records")

    return insights


def read_table(input_path: Path) -> pd.DataFrame:
    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(input_path)
    return pd.read_csv(input_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze organic content export")
    parser.add_argument("input_file")
    parser.add_argument("--output", default="content_analysis.json")
    args = parser.parse_args()

    df = read_table(Path(args.input_file))
    df = normalize_columns(df)
    df = add_scores(df)

    top_posts = []
    if "content_score" in df.columns:
        top_posts = df.sort_values("content_score", ascending=False).head(10).to_dict(orient="records")

    output = {
        "rows": len(df),
        "available_columns": list(df.columns),
        "top_posts": top_posts,
        "grouped_insights": grouped_insights(df),
    }

    with open(args.output, "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print(f"Content analysis saved to {args.output}")


if __name__ == "__main__":
    main()
