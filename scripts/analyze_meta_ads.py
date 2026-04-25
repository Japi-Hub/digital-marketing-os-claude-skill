#!/usr/bin/env python3
"""Analyze Meta Ads CSV/XLSX exports and produce a decision-ready JSON summary."""

import argparse
import json
from pathlib import Path

import pandas as pd


COLUMN_ALIASES = {
    "campaign": ["campaign", "campaign name", "nombre de la campaña", "campaña"],
    "adset": ["ad set", "ad set name", "conjunto de anuncios", "grupo de anuncios", "adset"],
    "ad": ["ad", "ad name", "anuncio", "nombre del anuncio"],
    "spend": ["amount spent", "spend", "importe gastado", "gasto", "inversión", "inversion"],
    "impressions": ["impressions", "impresiones"],
    "reach": ["reach", "alcance"],
    "clicks": ["link clicks", "clicks", "clics en el enlace", "clics", "clics únicos"],
    "leads": ["leads", "resultados", "clientes potenciales", "prospectos", "contacts"],
    "conversions": ["conversions", "compras", "purchases", "ventas", "conversiones"],
    "revenue": ["purchase conversion value", "revenue", "valor de conversión", "ingresos", "ventas valor"],
    "frequency": ["frequency", "frecuencia"],
    "ctr": ["ctr", "ctr link click-through rate", "ctr único", "porcentaje de clics"],
    "cpc": ["cpc", "cost per link click", "costo por clic", "coste por clic"],
    "cpm": ["cpm", "cost per 1,000 impressions", "costo por mil impresiones", "coste por mil impresiones"],
    "cpa": ["cost per result", "costo por resultado", "coste por resultado", "cpa", "cpl"],
}


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


def safe_numeric(series: pd.Series) -> pd.Series:
    if series.dtype == object:
        series = series.astype(str).str.replace("$", "", regex=False).str.replace(",", "", regex=False).str.replace("%", "", regex=False)
    return pd.to_numeric(series, errors="coerce").fillna(0)


def calculate_metrics(df: pd.DataFrame) -> pd.DataFrame:
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
    if input_path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(input_path)
    return pd.read_csv(input_path)


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
