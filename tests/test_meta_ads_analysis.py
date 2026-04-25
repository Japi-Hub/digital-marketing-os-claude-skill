import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "scripts"))

from analyze_meta_ads import normalize_columns, calculate_metrics, classify_row, validate_dataframe


def test_normalize_columns_spanish_names():
    df = pd.DataFrame({
        "Nombre de la campaña": ["A"],
        "Importe gastado": [100],
        "Impresiones": [10000],
        "Clics en el enlace": [200],
        "Resultados": [10],
    })
    normalized = normalize_columns(df)
    assert "campaign" in normalized.columns
    assert "spend" in normalized.columns
    assert "impressions" in normalized.columns
    assert "clicks" in normalized.columns
    assert "leads" in normalized.columns


def test_calculate_metrics():
    df = pd.DataFrame({
        "spend": [100],
        "impressions": [10000],
        "clicks": [200],
        "leads": [10],
    })
    result = calculate_metrics(df)
    assert round(result.loc[0, "ctr"], 2) == 2.00
    assert round(result.loc[0, "cpc"], 2) == 0.50
    assert round(result.loc[0, "cpm"], 2) == 10.00
    assert round(result.loc[0, "cpa"], 2) == 10.00


def test_classify_strong_row():
    row = pd.Series({"spend": 100, "ctr": 2.0, "cpa": 10, "frequency": 1.2, "leads": 10, "conversions": 2, "roas": 3})
    benchmarks = {
        "target_cpa": 25,
        "max_cpa": 40,
        "min_ctr": 0.8,
        "good_ctr": 1.5,
        "fatigue_frequency": 3.0,
        "good_roas": 2.0,
    }
    analysis = classify_row(row, benchmarks)
    assert analysis["priority"] == "high"
    assert analysis["decision"] in ["scale_carefully", "maintain_or_scale"]


def test_validate_empty_dataframe_raises():
    with pytest.raises(SystemExit):
        validate_dataframe(pd.DataFrame())


def test_validate_no_recognized_columns_raises():
    df = pd.DataFrame({"fecha": ["2026-01-01"], "nombre": ["A"]})
    with pytest.raises(SystemExit):
        validate_dataframe(df)


def test_validate_missing_spend_raises():
    df = pd.DataFrame({"impressions": [1000], "clicks": [20]})
    with pytest.raises(SystemExit):
        validate_dataframe(df)
