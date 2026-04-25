import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "scripts"))

from analyze_content_csv import normalize_columns, add_scores, grouped_insights


def test_normalize_content_columns_spanish_names():
    df = pd.DataFrame({
        "Fecha": ["2026-04-01"],
        "Plataforma": ["Instagram"],
        "Formato": ["Reel"],
        "Tema": ["Ventas"],
        "Alcance": [1000],
        "Guardados": [20],
        "Mensajes": [5],
    })
    normalized = normalize_columns(df)
    assert "date" in normalized.columns
    assert "platform" in normalized.columns
    assert "format" in normalized.columns
    assert "topic" in normalized.columns
    assert "reach" in normalized.columns
    assert "saves" in normalized.columns
    assert "messages" in normalized.columns


def test_add_scores_creates_content_score():
    df = pd.DataFrame({
        "reach": [1000, 2000],
        "likes": [100, 50],
        "comments": [10, 3],
        "shares": [20, 5],
        "saves": [30, 10],
        "messages": [5, 2],
        "leads": [2, 1],
    })
    result = add_scores(df)
    assert "engagement_rate" in result.columns
    assert "message_rate" in result.columns
    assert "lead_rate" in result.columns
    assert "content_score" in result.columns


def test_grouped_insights_by_topic():
    df = pd.DataFrame({
        "topic": ["A", "A", "B"],
        "content_score": [10, 8, 3],
        "engagement_rate": [5, 4, 1],
        "leads": [2, 1, 0],
        "messages": [5, 3, 1],
    })
    insights = grouped_insights(df)
    assert "topic" in insights
    assert insights["topic"][0]["topic"] == "A"
