# Digital Marketing OS Claude Skill

A Claude Skill designed to work as a senior digital marketing operating system.

It analyzes real marketing inputs such as:

- Meta Ads CSV/XLSX exports
- organic content reports
- funnel data
- landing page copy
- WhatsApp or DM conversations
- client briefs
- campaign reports
- reusable marketing learnings

The goal is not to produce generic marketing advice. The goal is to analyze, interpret, recommend decisions, and generate execution-ready outputs.

## What this skill does

- Meta Ads analysis
- Campaign, ad set, and ad diagnosis
- Funnel and CAC/LTV diagnosis
- Organic content intelligence
- WhatsApp/DM sales conversation analysis
- Landing page audits
- Client reporting
- Creative direction
- Learning memory by client

## Folder structure

```txt
.
├── SKILL.md
├── knowledge/
├── templates/
├── scripts/
├── schemas/
├── memory/
└── requirements.txt
```

## How to use with Claude

Upload this folder as a Claude Skill or use the files as the base for a custom skill.

Example prompts:

```txt
Analyze this Meta Ads export and tell me what to pause, scale, maintain, or investigate.
```

```txt
Analyze this organic content report and recommend next week's content based on data.
```

```txt
Review these WhatsApp conversations and tell me where leads are cooling down.
```

```txt
Audit this landing page copy and tell me what to change to improve conversion.
```

## How to run scripts locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Analyze Meta Ads:

```bash
python scripts/analyze_meta_ads.py examples/sample_meta_ads_export.csv --output meta_ads_analysis.json
```

Analyze organic content:

```bash
python scripts/analyze_content_csv.py examples/sample_content_report.csv --output content_analysis.json
```

Save a reusable learning:

```bash
python scripts/update_learning_memory.py \
  --client japi \
  --category frequent_objections \
  --learning "People ask for price before understanding the cost of poor WhatsApp sales follow-up." \
  --source "WhatsApp analysis" \
  --evidence "Repeated in multiple conversations"
```

## MVP limitations

This first version works primarily with uploaded files and manual inputs.

It does not yet connect directly to:

- Meta Ads API
- Google Analytics
- Search Console
- ManyChat
- WhatsApp Business API
- Supabase
- Notion
- Google Drive

Those should be added in later phases.

## Roadmap

### Phase 1: MVP functional

- Skill instructions
- Knowledge files
- Meta Ads script
- Organic content script
- Learning memory script
- Basic report templates

### Phase 2: Advanced analysis

- Period comparison
- Creative fatigue detection
- Funnel analysis
- CAC/LTV analysis
- Lead quality analysis

### Phase 3: Integrations

- Meta Ads API
- Google Analytics
- Google Search Console
- ManyChat
- WhatsApp Business API
- Supabase

### Phase 4: Learning and reporting system

- Client memory
- Decision logs
- Monthly reports
- Global hook library
- Winning ad library

### Phase 5: Creative production and distribution

- Creative briefs
- Video prompts
- Reels scripts
- Carousel structures
- Email sequences
- WhatsApp follow-up assets
- Distribution calendars
