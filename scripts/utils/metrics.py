"""Metric helpers used by Digital Marketing OS analysis scripts."""

import pandas as pd


def safe_numeric(series: pd.Series) -> pd.Series:
    """Convert common currency/percentage-formatted values to numeric values."""
    if series.dtype == object:
        series = (
            series.astype(str)
            .str.replace("$", "", regex=False)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
        )
    return pd.to_numeric(series, errors="coerce").fillna(0)


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate core Meta Ads metrics when source columns are available."""
    for col in ["spend", "impressions", "reach", "clicks", "leads", "conversions", "revenue", "frequency", "ctr", "cpc", "cpm", "cpa"]:
        if col in df.columns:
            df[col] = safe_numeric(df[col])

    if "ctr" not in df.columns and {"clicks", "impressions"}.issubset(df.columns):
        df["ctr"] = (df["clicks"] / df["impressions"].replace(0, pd.NA)).fillna(0) * 100

    if "cpc" not in df.columns and {"spend", "clicks"}.issubset(df.columns):
        df["cpc"] = (df["spend"] / df["clicks"].replace(0, pd.NA)).fillna(0)

    if "cpm" not in df.columns and {"spend", "impressions"}.issubset(df.columns):
        df["cpm"] = (df["spend"] / df["impressions"].replace(0, pd.NA)).fillna(0) * 1000

    if "cpa" not in df.columns:
        if {"spend", "leads"}.issubset(df.columns):
            df["cpa"] = (df["spend"] / df["leads"].replace(0, pd.NA)).fillna(0)
        elif {"spend", "conversions"}.issubset(df.columns):
            df["cpa"] = (df["spend"] / df["conversions"].replace(0, pd.NA)).fillna(0)

    if "roas" not in df.columns and {"revenue", "spend"}.issubset(df.columns):
        df["roas"] = (df["revenue"] / df["spend"].replace(0, pd.NA)).fillna(0)

    return df


def numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """Convert selected DataFrame columns to numeric values when they exist."""
    for col in cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df
