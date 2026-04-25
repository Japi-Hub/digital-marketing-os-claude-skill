import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "scripts"))

from generate_report import detect_report_type, format_content_report, format_meta_ads_report


def test_detect_meta_ads_type():
    data = {"summary": {}, "benchmarks_used": {}, "items": []}
    assert detect_report_type(data) == "meta_ads"


def test_detect_content_type():
    data = {"top_posts": [], "grouped_insights": {}}
    assert detect_report_type(data) == "content"


def test_detect_unknown_type_exits():
    with pytest.raises(SystemExit):
        detect_report_type({"hello": "world"})


def test_format_meta_ads_report_sections():
    data = {
        "summary": {"rows": 1, "total_spend": 100, "total_clicks": 50, "total_leads": 5},
        "benchmarks_used": {"target_cpa": 25},
        "items": [
            {
                "campaign": "Campaign A",
                "adset": "Ad set A",
                "ad": "Ad A",
                "spend": 100,
                "ctr": 1.2,
                "cpa": 20,
                "analysis": {"decision": "maintain_or_scale", "priority": "high", "flags": ["efficient_traffic"]},
            }
        ],
    }
    report = format_meta_ads_report(data)
    assert "# Meta Ads Report" in report
    assert "## Summary" in report
    assert "## Ad-level decisions" in report
    assert "## Next steps" in report


def test_format_content_report_sections():
    data = {
        "rows": 1,
        "available_columns": ["topic", "format"],
        "top_posts": [
            {
                "date": "2026-04-01",
                "platform": "Instagram",
                "format": "Reel",
                "topic": "WhatsApp",
                "hook": "Hook",
                "content_score": 10,
                "engagement_rate": 2,
                "leads": 1,
                "messages": 2,
            }
        ],
        "grouped_insights": {
            "topic": [{"topic": "WhatsApp", "posts": 1, "avg_score": 10, "avg_engagement": 2, "total_leads": 1, "total_messages": 2}],
            "format": [{"format": "Reel", "posts": 1, "avg_score": 10, "avg_engagement": 2, "total_leads": 1, "total_messages": 2}],
            "platform": [{"platform": "Instagram", "posts": 1, "avg_score": 10, "avg_engagement": 2, "total_leads": 1, "total_messages": 2}],
        },
    }
    report = format_content_report(data)
    assert "# Content Insights Report" in report
    assert "## Summary" in report
    assert "## Top posts by score" in report
    assert "## Next steps" in report
