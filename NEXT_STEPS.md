# Next Steps for Digital Marketing OS Claude Skill

This document guides future work on the skill. Follow this order. Do not turn this into a generic marketing assistant.

## Current status

The repository has a functional MVP foundation:

- `SKILL.md` with skill behavior and activation logic
- knowledge files for Meta Ads, content, funnels, WhatsApp sales, landing pages, reporting, and Método JAPI
- scripts to analyze Meta Ads exports, organic content exports, period comparisons, and learning memory
- templates for Meta Ads reports, content insights, executive summaries, and creative briefs
- sample CSV files
- basic tests

## Main principle

This skill must work as a Digital Marketing Operating System.

It should analyze real information, identify patterns, recommend decisions, and produce execution-ready outputs.

Every future improvement must strengthen one of these capabilities:

1. Better data ingestion
2. Better analysis
3. Better decisions
4. Better reporting
5. Better learning memory
6. Better creative production based on evidence

## What not to do

Do not:

- rewrite the whole strategy
- make generic marketing advice
- add unnecessary complexity before the MVP is stable
- connect APIs before file-based workflows are solid
- remove the distinction between observed data, interpretation, hypothesis, decision, and next action
- ignore Método JAPI when analyzing WhatsApp or sales conversations

## Phase 1: Stabilize the MVP

### 1. Run tests

```bash
pip install -r requirements.txt
pytest
```

Fix any failures before adding features.

### 2. Test scripts with sample files

```bash
python scripts/analyze_meta_ads.py examples/sample_meta_ads_export.csv --output meta_ads_analysis.json
python scripts/analyze_content_csv.py examples/sample_content_report.csv --output content_analysis.json
python scripts/compare_meta_periods.py examples/sample_meta_ads_export.csv examples/sample_meta_ads_export.csv --output meta_ads_period_comparison.json
```

### 3. Review JSON outputs

Confirm the outputs are useful for Claude to interpret.

The JSON should include:

- summary metrics
- available columns
- item-level analysis
- decision labels
- flags
- reasons

### 4. Improve error handling

Add helpful error messages when:

- the uploaded file is missing required columns
- numeric fields cannot be parsed
- a CSV uses unsupported delimiters
- there is no spend, reach, impressions, clicks, leads, or conversion data

### 5. Add CLI help examples

Each script should clearly show usage when called with `--help`.

## Phase 2: Improve Meta Ads analysis

Add a more robust Meta Ads analysis engine.

### Needed improvements

- group results by campaign
- group results by ad set
- group results by ad
- detect creative fatigue more explicitly
- compare performance to account averages
- flag high spend with low result
- flag low CPL but weak sales quality when sales data exists
- support custom benchmark files by client

### Suggested new files

```txt
scripts/utils/metrics.py
scripts/utils/column_mapping.py
scripts/utils/scoring.py
scripts/analyze_meta_ads_advanced.py
schemas/meta_ads_input_schema.json
schemas/meta_ads_output_schema.json
```

### Desired decision labels

- scale_carefully
- maintain
- reduce_budget
- pause
- refresh_creative
- test_new_hook
- investigate_funnel
- investigate_tracking
- insufficient_data

## Phase 3: Improve content intelligence

The content analysis should identify patterns that help decide what to create next.

### Needed improvements

- classify posts by funnel stage
- detect best hooks
- detect best topics
- detect best formats
- detect content that creates messages or leads
- detect content that gets engagement but no commercial action
- recommend content themes for next week
- identify organic posts that should become ads
- identify paid angles that should become organic content

### Suggested new files

```txt
scripts/analyze_content_advanced.py
schemas/content_input_schema.json
schemas/content_output_schema.json
templates/weekly-content-calendar.md
```

## Phase 4: Add WhatsApp and DM analysis

Create a script that can process exported conversations or pasted text.

### Needed capabilities

- detect questions asked by leads
- detect objections
- detect where the lead cooled down
- detect overly long seller messages
- detect missing CTA
- detect price sent too early
- detect follow-up gaps
- recommend sales script improvements
- recommend content based on repeated objections

### Suggested new files

```txt
scripts/analyze_whatsapp_export.py
schemas/whatsapp_analysis_output_schema.json
templates/whatsapp-sales-insights-report.md
```

## Phase 5: Add landing page audit support

Create a script or structured workflow for landing page copy audits.

### MVP approach

Start with pasted text or HTML.

### Future approach

Add URL fetching and parsing using:

- requests
- beautifulsoup4
- readability-lxml
- playwright only if necessary

### Suggested new files

```txt
scripts/audit_landing_text.py
scripts/audit_landing_url.py
templates/landing-audit-report.md
```

## Phase 6: Improve learning memory

Memory should become a decision asset, not a notes folder.

### Needed improvements

- deduplicate similar learnings
- add confidence levels
- add evidence count
- add client industry
- add date range
- add related campaigns or content
- allow querying memory by client, category, or theme

### Suggested new files

```txt
scripts/query_learning_memory.py
scripts/consolidate_learning_memory.py
memory/global-hooks.json
memory/winning-ads.json
memory/objections.json
memory/decisions-log.jsonl
```

## Phase 7: Reporting engine

Create a script that turns analysis JSON into Markdown reports.

### Needed capabilities

- generate client-facing report
- generate internal tactical report
- generate action table
- generate decision log
- generate creative brief from insights

### Suggested new files

```txt
scripts/generate_report.py
templates/internal-decision-report.md
templates/monthly-client-report.md
templates/decision-log.md
```

## Phase 8: Creative production system

Creative work must come from data, not random ideas.

### Needed capabilities

Generate:

- ad concepts
- hooks
- reels scripts
- carousel structures
- video briefs
- design briefs
- email ideas
- WhatsApp follow-up assets
- remarketing angles

Inputs should include:

- Meta Ads winners
- organic content winners
- WhatsApp objections
- landing page gaps
- client offer
- audience segment

### Suggested new files

```txt
templates/video-brief.md
templates/reel-script.md
templates/carousel-structure.md
templates/ad-variations.md
knowledge/creative-direction-guide.md
```

## Phase 9: Integrations later, not now

Do not add API integrations until file workflows are stable.

Future integrations:

- Meta Ads API
- Instagram Insights API
- Google Analytics
- Google Search Console
- ManyChat
- WhatsApp Business API
- Supabase
- Google Drive
- Notion

## Recommended next technical task

Start with this:

1. Run tests.
2. Run the scripts with sample files.
3. Improve error handling in `scripts/analyze_meta_ads.py`.
4. Add `scripts/utils/column_mapping.py` and move aliases there.
5. Add `scripts/utils/metrics.py` and move metric calculations there.
6. Add `scripts/generate_report.py` to turn analysis JSON into Markdown.

## Done criteria for MVP

The MVP is considered usable when:

- tests pass
- sample files produce valid JSON
- Claude can read the JSON and produce a useful report
- Meta Ads decisions are clear
- content recommendations are actionable
- learning memory can save reusable insights
- README explains how to use everything

## Prompt for Claude Code or Codex

Use this prompt when asking another coding assistant to continue:

```txt
Review this repository and improve the Digital Marketing OS Claude Skill.

Start by running the tests. Then run the scripts with the sample files.

Do not rewrite the marketing strategy. Focus on technical improvements that make the skill more reliable, easier to use, and better at analyzing real files.

Priorities:
1. Improve error handling in the scripts.
2. Move repeated logic into scripts/utils/.
3. Add report generation from analysis JSON to Markdown.
4. Add or improve tests.
5. Keep outputs decision-ready for Claude.

Respect the structure in NEXT_STEPS.md.
```
