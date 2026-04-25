#!/usr/bin/env python3
"""Generate Markdown reports from Digital Marketing OS analysis JSON files."""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def detect_report_type(data: dict[str, Any]) -> str:
    """Detect the analysis JSON type from its structure."""
    if {"summary", "benchmarks_used", "items"}.issubset(data.keys()):
        return "meta_ads"
    if {"top_posts", "grouped_insights"}.issubset(data.keys()):
        return "content"

    print("ERROR: Cannot detect report type from JSON structure.", file=sys.stderr)
    print("       Expected Meta Ads keys: summary, benchmarks_used, items", file=sys.stderr)
    print("       Expected Content keys: top_posts, grouped_insights", file=sys.stderr)
    print(f"       Found keys: {sorted(data.keys())}", file=sys.stderr)
    sys.exit(1)


def fmt(value: Any, decimals: int = 2) -> str:
    """Format values for Markdown tables."""
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    """Build a simple Markdown table."""
    if not rows:
        return "No data available.\n"

    header_row = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"
    body = ["| " + " | ".join(fmt(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header_row, separator, *body]) + "\n"


def format_meta_ads_report(data: dict[str, Any]) -> str:
    """Generate a Meta Ads Markdown report."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    summary = data.get("summary", {})
    benchmarks = data.get("benchmarks_used", {})
    items = data.get("items", [])

    lines = [
        "# Meta Ads Report",
        f"_Generated: {generated}_",
        "",
        "## Summary",
        "",
    ]

    summary_rows = [
        ["Rows", summary.get("rows")],
        ["Total spend", summary.get("total_spend")],
        ["Total impressions", summary.get("total_impressions")],
        ["Total clicks", summary.get("total_clicks")],
        ["Total leads", summary.get("total_leads")],
        ["Total conversions", summary.get("total_conversions")],
        ["Total revenue", summary.get("total_revenue")],
        ["Blended CTR", summary.get("blended_ctr")],
        ["Blended CPC", summary.get("blended_cpc")],
        ["Blended CPL", summary.get("blended_cpl")],
        ["Blended ROAS", summary.get("blended_roas")],
    ]
    lines.append(md_table(["Metric", "Value"], summary_rows))

    lines.extend(["", "## Benchmarks used", ""])
    benchmark_rows = [[key, value] for key, value in benchmarks.items()]
    lines.append(md_table(["Benchmark", "Value"], benchmark_rows))

    lines.extend(["", "## Ad-level decisions", ""])
    decision_rows = []
    decision_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    flag_counter: Counter[str] = Counter()

    for item in items:
        analysis = item.get("analysis", {})
        decision = analysis.get("decision", "-")
        flags = analysis.get("flags", []) or []
        decision_groups[decision].append(item)
        flag_counter.update(flags)
        decision_rows.append([
            item.get("campaign", "-"),
            item.get("adset", "-"),
            item.get("ad", "-"),
            item.get("spend", "-"),
            item.get("ctr", "-"),
            item.get("cpa", "-"),
            decision,
            analysis.get("priority", "-"),
            ", ".join(flags) if flags else "-",
        ])

    lines.append(md_table(
        ["Campaign", "Ad set", "Ad", "Spend", "CTR", "CPA", "Decision", "Priority", "Flags"],
        decision_rows,
    ))

    lines.extend(["", "## Action groups", ""])
    for decision, grouped_items in sorted(decision_groups.items()):
        lines.append(f"### {decision}")
        lines.append("")
        for item in grouped_items:
            label = " / ".join(str(item.get(part, "-")) for part in ["campaign", "adset", "ad"])
            lines.append(f"- {label}")
        lines.append("")

    lines.extend(["## Next steps", ""])
    if flag_counter:
        for flag, count in flag_counter.most_common():
            if flag == "possible_creative_fatigue":
                lines.append(f"- Refresh creative for {count} item(s) showing possible fatigue.")
            elif flag == "low_ctr":
                lines.append(f"- Test new hooks or first frames for {count} item(s) with low CTR.")
            elif flag == "high_cost_per_result":
                lines.append(f"- Review budget allocation for {count} item(s) with high cost per result.")
            elif flag == "lead_quality_or_sales_problem":
                lines.append(f"- Investigate post-lead funnel and sales follow-up for {count} item(s).")
            elif flag == "strong_roas":
                lines.append(f"- Consider careful scaling for {count} item(s) with strong ROAS.")
            elif flag == "efficient_traffic":
                lines.append(f"- Maintain or scale {count} efficient traffic item(s), while monitoring quality.")
            else:
                lines.append(f"- Review {count} item(s) flagged as `{flag}`.")
    else:
        lines.append("- No major flags detected. Maintain monitoring and continue testing.")

    return "\n".join(lines).strip() + "\n"


def format_content_report(data: dict[str, Any]) -> str:
    """Generate a content insights Markdown report."""
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    grouped = data.get("grouped_insights", {})
    top_posts = data.get("top_posts", [])

    lines = [
        "# Content Insights Report",
        f"_Generated: {generated}_",
        "",
        "## Summary",
        "",
        md_table(["Metric", "Value"], [
            ["Rows analyzed", data.get("rows")],
            ["Available columns", ", ".join(data.get("available_columns", []))],
        ]),
        "",
        "## Top posts by score",
        "",
    ]

    top_rows = []
    for post in top_posts[:10]:
        top_rows.append([
            post.get("date", "-"),
            post.get("platform", "-"),
            post.get("format", "-"),
            post.get("topic", "-"),
            post.get("hook", "-"),
            post.get("content_score", "-"),
            post.get("engagement_rate", "-"),
            post.get("leads", "-"),
            post.get("messages", "-"),
        ])
    lines.append(md_table(["Date", "Platform", "Format", "Topic", "Hook", "Score", "Engagement", "Leads", "Messages"], top_rows))

    for key, title in [("topic", "Best patterns by topic"), ("format", "Best patterns by format"), ("platform", "Best patterns by platform")]:
        lines.extend(["", f"## {title}", ""])
        rows = []
        for item in grouped.get(key, []):
            rows.append([
                item.get(key, "-"),
                item.get("posts", "-"),
                item.get("avg_score", "-"),
                item.get("avg_engagement", "-"),
                item.get("total_leads", "-"),
                item.get("total_messages", "-"),
            ])
        lines.append(md_table([key.title(), "Posts", "Avg score", "Avg engagement", "Leads", "Messages"], rows))

    lines.extend(["", "## Next steps", ""])
    if grouped.get("topic"):
        top_topic = grouped["topic"][0].get("topic")
        lines.append(f"- Repeat and deepen the strongest topic: **{top_topic}**.")
    if grouped.get("format"):
        top_format = grouped["format"][0].get("format")
        lines.append(f"- Prioritize the strongest format: **{top_format}**.")
    if top_posts:
        lines.append("- Turn the highest-scoring posts into paid ad angles or remarketing assets.")
    lines.append("- Use posts with high messages/leads as conversion content, not just engagement content.")

    return "\n".join(lines).strip() + "\n"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        print(f"ERROR: File not found: '{path}'", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse JSON file '{path}': {exc}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Markdown report from analysis JSON")
    parser.add_argument("input_file")
    parser.add_argument("--output", default="report.md")
    args = parser.parse_args()

    data = read_json(Path(args.input_file))
    report_type = detect_report_type(data)

    if report_type == "meta_ads":
        report = format_meta_ads_report(data)
    elif report_type == "content":
        report = format_content_report(data)
    else:
        print(f"ERROR: Unsupported report type: {report_type}", file=sys.stderr)
        sys.exit(1)

    with open(args.output, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"Report saved to {args.output}")


if __name__ == "__main__":
    main()
