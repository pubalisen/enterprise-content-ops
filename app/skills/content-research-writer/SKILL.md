---
name: content-research-writer
description: >
  Systematic content research methodology for producing well-sourced,
  authoritative articles. Covers source evaluation, data gathering,
  competitive analysis, and research synthesis techniques.
---

# Content Research Instructions

## Step 1: Define the Research Scope
Before researching, establish:
- **Core question**: What is the central thesis or question?
- **Audience expertise level**: Beginner, intermediate, or expert?
- **Depth required**: Overview (5 sources) or deep-dive (15+ sources)?
- **Freshness requirement**: How recent must sources be?

## Step 2: Source Gathering
Use `load_skill_resource` to read `references/source-evaluation.md`.

### Source Hierarchy (prioritize top-down)
1. **Primary research**: Original studies, datasets, surveys
2. **Expert sources**: Named researchers, practitioners, analysts
3. **Industry reports**: Gartner, McKinsey, specific industry bodies
4. **Reputable journalism**: NYT, WSJ, Reuters, domain-specific outlets
5. **Community consensus**: Stack Overflow, Reddit threads, HN discussions

## Step 3: Competitive Analysis
- Identify top 5 ranking articles for the target topic
- Note their structure, depth, and unique angles
- Find gaps: What do they all miss? What data is outdated?
- Plan to be 10x better on at least one dimension

## Step 4: Synthesize Findings
Output a structured research brief:
```
# Research Brief: [Topic]

## Key Findings
- Finding 1 (Source: [name, year])
- Finding 2 (Source: [name, year])

## Data Points
- [Specific stat] — [Source]
- [Specific stat] — [Source]

## Expert Quotes
- "[Quote]" — [Expert Name, Title, Organization]

## Recommended Angle
[Your unique thesis based on the research]

## Sources
1. [Full citation]
2. [Full citation]
```

## Step 5: Fact-Check
Before finalizing, verify:
- All statistics have named sources with dates
- No claims are unsupported
- Quotes are attributed to real, verifiable people
- Data is from the last 2 years unless historical context
