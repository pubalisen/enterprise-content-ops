# 🧪 ADK 2.0 Agent Test Script — Web UI

> Open **http://127.0.0.1:8000** → Select **app** → Click **New Session**
> Paste each query below into the chat. Check the **Events** tab and **agent graph** on the left to verify the correct sub-agent was triggered.

---

## Test 1: Routing — Root Orchestrator
**What to verify:** Agent responds directly without delegating to any sub-agent.

```
What workflows do you have available? List all of them with descriptions.
```

✅ **Expected:** Lists content_pipeline, multi_format_generator, quality_loop, and skills.
📍 **Check:** Events tab shows only `enterprise_content_ops` — no sub-agent invocations.

---

## Test 2: Sequential Pipeline (Research → Draft → Review)
**What to verify:** Three sub-agents fire in order. Check the **State** tab for keys.

```
Write a short article about how AI is transforming healthcare diagnostics. Use the full content pipeline.
```

✅ **Expected:** A complete, reviewed article with research citations.
📍 **Check State tab for:**
- `research_brief` — populated by research_agent
- `content_draft` — populated by draft_agent  
- `final_content` — populated by review_agent

📍 **Check agent graph:** `content_pipeline` → `research_agent` → `draft_agent` → `review_agent` all highlighted.

---

## Test 3: Parallel Generator (4 formats at once)
**What to verify:** Four sub-agents run concurrently. Check the **State** tab for all 4 keys.

```
Take this topic and create versions for all channels: "Why Developer Experience (DevEx) is the most important investment in 2026"
```

✅ **Expected:** Blog post + social media posts + newsletter email + executive summary.
📍 **Check State tab for:**
- `blog_version`
- `social_version`
- `email_version`
- `exec_summary`

📍 **Check agent graph:** `multi_format_generator` → all 4 sub-agents highlighted simultaneously.

---

## Test 4: Quality Loop (Writer ↔ Critic)
**What to verify:** Multiple iterations visible in Events. Critic scores content each round.

```
Write a really polished thought leadership piece about the future of remote work. Keep refining it until it's excellent.
```

✅ **Expected:** High-quality content that went through 1-3 critique rounds.
📍 **Check Events tab for:**
- `iterative_writer` event (first draft)
- `quality_critic` event (scores + feedback)
- `iterative_writer` event again (if score < 8)
- `quality_critic` event with "APPROVED" (if score ≥ 8)

📍 **Check State tab for:**
- `current_draft` — latest version
- `critique` — latest critique with scores

---

## Test 5: Inline Skill — SEO Checklist
**What to verify:** The `seo-checklist` skill is loaded via `load_skill` in the Events.

```
Review this blog post for SEO issues: "Getting Started with Kubernetes. Kubernetes is a container orchestration platform that helps manage containers at scale. It was created by Google."
```

✅ **Expected:** Point-by-point SEO checklist evaluation (title, meta, headings, keywords, etc.)
📍 **Check Events:** Look for `list_skills` → `load_skill(seo-checklist)` tool calls.

---

## Test 6: File-Based Skill — Blog Writer
**What to verify:** The `blog-writer` SKILL.md is loaded, including its references.

```
I need help structuring a blog post about cloud cost optimization. Can you use your blog writing skill to guide me?
```

✅ **Expected:** Structured outline following the blog-writer templates.
📍 **Check Events:** Look for `load_skill(blog-writer)` and possibly `load_skill_resource(references/blog-templates.md)`.

---

## Test 7: File-Based Skill — Content Research Writer
**What to verify:** The research methodology skill is loaded with source evaluation framework.

```
Help me research the current state of quantum computing for enterprise applications. Use your research skill.
```

✅ **Expected:** Structured research brief with source hierarchy and CRAAP evaluation.
📍 **Check Events:** Look for `load_skill(content-research-writer)`.

---

## Test 8: Meta Skill — Skill Creator
**What to verify:** Generates a complete, valid SKILL.md file.

```
Create a new skill for reviewing Python code for security vulnerabilities. Generate the full SKILL.md file.
```

✅ **Expected:** Complete SKILL.md with frontmatter (name, description) and step-by-step instructions.
📍 **Check Events:** Look for `load_skill(skill-creator)` and `load_skill_resource(references/skill-spec.md)`.

---

## Test 9: Edge Case — Ambiguous Request
**What to verify:** Root orchestrator picks the most appropriate workflow.

```
I need a blog post about sustainable energy trends, make it really good and also give me social media versions.
```

✅ **Expected:** Should route to either `content_pipeline` (sequential) or `multi_format_generator` (parallel), depending on interpretation.
📍 **Watch:** Does it pick one workflow or combine? This tests LLM routing intelligence.

---

## Test 10: Edge Case — Simple Question
**What to verify:** Root orchestrator answers directly without invoking any sub-agent.

```
How many skills do you have loaded?
```

✅ **Expected:** Direct answer (4 skills) without delegating to a workflow.
📍 **Check Events:** Only `enterprise_content_ops` — no sub-agent calls.

---

## 📊 Results Tracker

| # | Test | Workflow | Pass? |
|---|------|----------|-------|
| 1 | Routing | Direct | ☐ |
| 2 | Sequential Pipeline | content_pipeline | ☐ |
| 3 | Parallel Generator | multi_format_generator | ☐ |
| 4 | Quality Loop | quality_loop | ☐ |
| 5 | SEO Skill (inline) | skills | ☐ |
| 6 | Blog Writer (file) | skills | ☐ |
| 7 | Research Writer (file) | skills | ☐ |
| 8 | Skill Creator (meta) | skills | ☐ |
| 9 | Ambiguous routing | auto | ☐ |
| 10 | Simple question | direct | ☐ |
