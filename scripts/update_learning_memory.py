#!/usr/bin/env python3
"""Save reusable marketing learnings by client."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_MEMORY = {
    "client_id": "",
    "industry": "",
    "winning_hooks": [],
    "winning_ads": [],
    "content_themes": [],
    "frequent_objections": [],
    "sales_bottlenecks": [],
    "audience_learnings": [],
    "offer_learnings": [],
    "landing_learnings": [],
    "decisions": []
}


def load_json(path: Path, client: str) -> dict:
    if path.exists():
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    data = DEFAULT_MEMORY.copy()
    data["client_id"] = client
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Save a reusable marketing learning")
    parser.add_argument("--client", required=True, help="Client slug, for example japi or metabolika")
    parser.add_argument("--category", required=True, help="Memory category, for example winning_hooks or frequent_objections")
    parser.add_argument("--learning", required=True, help="The reusable learning")
    parser.add_argument("--source", default="", help="Where this learning came from")
    parser.add_argument("--evidence", default="", help="Evidence supporting the learning")
    parser.add_argument("--impact", default="", help="Expected or observed business impact")
    parser.add_argument("--memory-dir", default="memory/clients")
    args = parser.parse_args()

    memory_dir = Path(args.memory_dir)
    memory_dir.mkdir(parents=True, exist_ok=True)

    path = memory_dir / f"{args.client}.json"
    data = load_json(path, args.client)

    if args.category not in data:
        data[args.category] = []

    entry = {
        "learning": args.learning,
        "source": args.source,
        "evidence": args.evidence,
        "impact": args.impact,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    data[args.category].append(entry)

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    print(f"Saved learning to {path}")


if __name__ == "__main__":
    main()
