# Enterprise Content Ops — ADK 2.0 Multi-Agent Workflows

An enterprise-grade content operations system built with **Google ADK 2.0** that demonstrates all major multi-agent workflow patterns in a single, deployable project.

<p align="center">
  <strong>SequentialAgent → ParallelAgent → LoopAgent → Skills → Agent Engine</strong>
</p>

## What This Demonstrates

| ADK 2.0 Feature | Implementation | Purpose |
|---|---|---|
| **SequentialAgent** | Content Pipeline | Research → Draft → Review in strict order |
| **ParallelAgent** | Multi-Format Generator | Blog + Social + Email + Exec Summary concurrently |
| **LoopAgent** | Quality Refinement | Write → Critique → Rewrite until score ≥ 8/10 |
| **Inline Skills** | SEO Checklist | Skill defined in Python code |
| **File-based Skills** | Blog Writer, Research Writer | Skills loaded from `SKILL.md` directories |
| **Meta Skills** | Skill Creator | Generates new skill definitions on demand |
| **LLM Routing** | Root Orchestrator | Automatic delegation to the right workflow |
| **Agent Engine** | `deploy.py` | One-command deployment to Vertex AI |

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    Root Orchestrator (LlmAgent)                  │
│   Routes user requests to the appropriate workflow agent         │
├────────────┬────────────────┬───────────────┬───────────────────┤
│            │                │               │                   │
│  Sequential│   Parallel     │    Loop       │   Skills          │
│  Pipeline  │   Generator    │    Refiner    │   Toolset         │
│            │                │               │                   │
│  Research  │  Blog Writer   │  Writer       │  seo-checklist    │
│    ↓       │  Social Writer │    ↓          │  blog-writer      │
│  Drafter   │  Email Writer  │  Critic       │  research-writer  │
│    ↓       │  Exec Summary  │    ↓ (loop)   │  skill-creator    │
│  Reviewer  │                │  Passes?      │                   │
└────────────┴────────────────┴───────────────┴───────────────────┘
```

## Quick Start

```bash
# Clone and setup
cd agents/enterprise-content-ops
python3 -m venv .venv && source .venv/bin/activate
pip install -e .

# Configure API key
cp .env.example app/.env
# Edit app/.env with your GOOGLE_API_KEY

# Run with ADK Web UI
adk web
```

## Try It

| # | Query | Workflow Triggered |
|---|-------|-------------------|
| 1 | "Write an article about AI in healthcare" | **SequentialAgent** — Full pipeline: Research → Draft → Review |
| 2 | "Take this content about cloud migration and create versions for all our channels" | **ParallelAgent** — Blog + Social + Email + Exec Summary generated concurrently |
| 3 | "Write a really polished thought leadership piece about the future of remote work" | **LoopAgent** — Iterative write → critique → rewrite (up to 3 rounds) |
| 4 | "Review this blog post for SEO issues" | **Skill** — seo-checklist loaded on demand |
| 5 | "Help me research the current state of quantum computing" | **Skill** — content-research-writer with source evaluation framework |
| 6 | "I need a new skill for reviewing legal contracts" | **Meta Skill** — skill-creator generates a new SKILL.md |
| 7 | "What workflows do you have available?" | **Direct** — Root agent explains its capabilities |

## Deploy to Vertex AI Agent Engine

```bash
# Validate locally (dry run)
python deploy.py --dry-run

# Deploy to your GCP project
python deploy.py --project robust-habitat-467517-r6 --region us-central1

# Deploy with custom name
python deploy.py --display-name "Content Ops v2"
```

### Prerequisites for Deployment
```bash
# Authenticate with GCP
gcloud auth application-default login
gcloud config set project robust-habitat-467517-r6

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
```

## Project Structure

```
enterprise-content-ops/
├── app/
│   ├── __init__.py          # Package init
│   ├── agent.py             # Root orchestrator + all workflow agents
│   └── skills/
│       ├── blog-writer/
│       │   ├── SKILL.md            # Blog writing guide
│       │   └── references/
│       │       └── blog-templates.md
│       └── content-research-writer/
│           ├── SKILL.md            # Research methodology
│           └── references/
│               └── source-evaluation.md
├── deploy.py                # Vertex AI Agent Engine deployment
├── .env.example             # Environment template
├── pyproject.toml           # Project config (ADK 2.0)
└── README.md
```

## Key Concepts

### Sequential Pipeline
The `content_pipeline` executes three agents in strict order. Each agent writes its output to a shared state key, which the next agent reads:
```
research_agent → state["research_brief"]
draft_agent    → reads research_brief, writes state["content_draft"]
review_agent   → reads content_draft, writes state["final_content"]
```

### Parallel Fan-Out
The `multi_format_generator` runs four agents simultaneously. They all read from the same input but write to different state keys, producing four format variants in the time it takes to generate one.

### Loop Refinement
The `quality_loop` alternates between a writer and a critic. The critic scores the content on 5 dimensions (clarity, engagement, accuracy, structure, actionability). If the average score is below 8/10, the writer gets the critique and rewrites. Max 3 iterations prevents infinite loops.

### Progressive Skill Disclosure
Skills use a three-level loading pattern:
- **L1**: `list_skills` → Returns only names + descriptions (~200 tokens)
- **L2**: `load_skill` → Loads full instructions when needed
- **L3**: `load_skill_resource` → Fetches reference files on demand

This keeps the context window lean while giving the agent access to deep knowledge.

## License

Apache License 2.0
