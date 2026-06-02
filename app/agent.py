"""Enterprise Content Ops Agent — ADK 2.0 Multi-Agent Workflows Showcase.

Demonstrates 5 core ADK 2.0 patterns in a single, production-ready system:

  1. SequentialAgent  — Research → Draft → Review pipeline
  2. ParallelAgent    — Generate blog, social, email, exec summary concurrently
  3. LoopAgent        — Iterative write → critique → rewrite until quality passes
  4. Skill Patterns   — Inline, file-based, external, and meta skills
  5. LLM Delegation   — Root orchestrator with automatic agent transfer

Architecture:
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
"""

import pathlib

from google.adk.agents import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.loop_agent import LoopAgent
from google.adk.skills import load_skill_from_dir, models
from google.adk.tools.skill_toolset import SkillToolset


# =============================================================================
# 1. SKILLS — Four patterns of reusable knowledge
# =============================================================================

# Pattern A: Inline skill (defined in code)
seo_skill = models.Skill(
    frontmatter=models.Frontmatter(
        name="seo-checklist",
        description=(
            "SEO optimization checklist for content. Covers title tags,"
            " meta descriptions, heading structure, keyword placement,"
            " readability, and internal/external linking best practices."
        ),
    ),
    instructions=(
        "When optimizing content for SEO, check each item:\n\n"
        "1. **Title**: 50-60 chars, primary keyword near the start\n"
        "2. **Meta description**: 150-160 chars, includes a call-to-action\n"
        "3. **Headings**: H2/H3 hierarchy, keywords in 2-3 headings\n"
        "4. **First paragraph**: Primary keyword in first 100 words\n"
        "5. **Keyword density**: 1-2%, never forced or awkward\n"
        "6. **Paragraphs**: 2-3 sentences max, use bullet lists often\n"
        "7. **Links**: 2-3 internal + 3-5 external to authoritative sources\n"
        "8. **Images**: Alt text with keywords, compressed, descriptive names\n"
        "9. **URL slug**: Short, keyword-rich, hyphenated\n"
        "10. **Schema markup**: FAQ, HowTo, or Article structured data\n\n"
        "Review the content against each item and suggest specific improvements."
    ),
)

# Pattern B: File-based skill (loaded from directory)
blog_writer_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "blog-writer"
)

# Pattern C: External skill (loaded from a downloaded repo)
content_researcher_skill = load_skill_from_dir(
    pathlib.Path(__file__).parent / "skills" / "content-research-writer"
)

# Pattern D: Meta skill (generates new skills on demand)
skill_creator = models.Skill(
    frontmatter=models.Frontmatter(
        name="skill-creator",
        description=(
            "Creates new ADK-compatible skill definitions from requirements."
            " Generates complete SKILL.md files following the Agent Skills"
            " specification at agentskills.io."
        ),
    ),
    instructions=(
        "When asked to create a new skill, generate a complete SKILL.md file.\n\n"
        "Read `references/skill-spec.md` for the format specification.\n"
        "Read `references/example-skill.md` for a working example.\n\n"
        "Follow these rules:\n"
        "1. Name must be kebab-case, max 64 characters\n"
        "2. Description must be under 1024 characters\n"
        "3. Instructions should be clear, step-by-step\n"
        "4. Reference files in references/ for detailed domain knowledge\n"
        "5. Keep SKILL.md under 500 lines — put details in references/\n"
        "6. Output the complete file content the user can save directly\n"
    ),
    resources=models.Resources(
        references={
            "skill-spec.md": (
                "# Agent Skills Specification (agentskills.io)\n\n"
                "## SKILL.md Format\n"
                "Every skill directory must contain a SKILL.md file.\n\n"
                "### Frontmatter (YAML)\n"
                "```yaml\n"
                "---\n"
                "name: my-skill-name          # kebab-case, max 64 chars\n"
                "description: What this skill does.  # max 1024 chars\n"
                "---\n"
                "```\n\n"
                "### Body (Markdown)\n"
                "The body contains the skill instructions. Write clear,\n"
                "step-by-step instructions the agent will follow.\n\n"
                "### Directory Structure\n"
                "```\n"
                "my-skill-name/\n"
                "  SKILL.md           # Required: metadata + instructions\n"
                "  references/        # Optional: detailed reference docs\n"
                "  assets/            # Optional: templates, data files\n"
                "  scripts/           # Optional: executable scripts\n"
                "```\n\n"
                "### Key Rules\n"
                "- Directory name MUST match the `name` field in frontmatter\n"
                "- Name must be kebab-case: ^[a-z0-9]+(-[a-z0-9]+)*$\n"
                "- Description is what the LLM uses to decide when to load\n"
                "- Keep instructions actionable — tell the agent WHAT to do\n"
                "- Use `load_skill_resource` references for detailed docs\n"
            ),
            "example-skill.md": (
                "# Example: Code Review Skill\n\n"
                "```markdown\n"
                "---\n"
                "name: code-review\n"
                "description: Reviews Python code for correctness, style, "
                "and performance. Checks for common bugs, PEP 8 compliance, "
                "and suggests optimizations.\n"
                "---\n\n"
                "# Code Review Instructions\n\n"
                "When asked to review code:\n\n"
                "## Step 1: Read the Guidelines\n"
                "Use `load_skill_resource` to read `references/review-checklist.md`.\n\n"
                "## Step 2: Analyze\n"
                "Check the code against each item in the checklist.\n\n"
                "## Step 3: Report\n"
                "Provide findings organized by severity:\n"
                "- **Critical**: Bugs, security issues\n"
                "- **Warning**: Style violations, performance concerns\n"
                "- **Info**: Suggestions for improvement\n"
                "```\n"
            ),
        }
    ),
)

skill_toolset = SkillToolset(
    skills=[
        seo_skill,
        blog_writer_skill,
        content_researcher_skill,
        skill_creator,
    ]
)


# =============================================================================
# 2. SEQUENTIAL AGENT — Content Production Pipeline
# =============================================================================
# Executes Research → Draft → Review in strict order.
# Each sub-agent's output feeds into the next via shared session state.

research_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="research_agent",
    description="Conducts research on a given topic and produces structured findings.",
    instruction=(
        "You are a senior research analyst. Given a topic:\n\n"
        "1. Identify the 3-5 most important angles to cover\n"
        "2. List key data points, statistics, or expert quotes\n"
        "3. Note the target audience and their likely knowledge level\n"
        "4. Suggest a recommended structure (sections, flow)\n"
        "5. Identify 3-5 high-authority sources to reference\n\n"
        "Output a structured research brief in markdown format.\n"
        "Store your findings in state key 'research_brief'."
    ),
    output_key="research_brief",
)

draft_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="draft_agent",
    description="Writes a polished first draft based on research findings.",
    instruction=(
        "You are a senior content writer. Using the research brief from the"
        " previous step (available in state as 'research_brief'):\n\n"
        "1. Write a complete, publication-ready article (800-1200 words)\n"
        "2. Use clear headings (H2/H3), short paragraphs, bullet lists\n"
        "3. Open with a compelling hook that addresses the reader directly\n"
        "4. Include specific data points from the research\n"
        "5. End with a clear call-to-action\n"
        "6. Maintain a professional but conversational tone\n\n"
        "Store your draft in state key 'content_draft'."
    ),
    output_key="content_draft",
)

review_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="review_agent",
    description="Reviews content for quality, accuracy, and SEO readiness.",
    instruction=(
        "You are a senior editor and SEO specialist. Review the draft"
        " (available in state as 'content_draft'):\n\n"
        "1. Check factual accuracy and logical consistency\n"
        "2. Evaluate readability (Flesch score target: 60-70)\n"
        "3. Assess SEO readiness: title, meta description, headings, keywords\n"
        "4. Check for grammar, tone consistency, and flow\n"
        "5. Provide specific revision suggestions\n\n"
        "Output a final reviewed version with your improvements applied,"
        " followed by a summary of changes made.\n"
        "Store the final version in state key 'final_content'."
    ),
    output_key="final_content",
)

content_pipeline = SequentialAgent(
    name="content_pipeline",
    description=(
        "End-to-end content production pipeline. Takes a topic through"
        " Research → Draft → Review stages sequentially. Use this when"
        " the user wants a fully produced piece of content."
    ),
    sub_agents=[research_agent, draft_agent, review_agent],
)


# =============================================================================
# 3. PARALLEL AGENT — Multi-Format Content Generator
# =============================================================================
# Generates blog post, social media, email, and exec summary concurrently.

blog_format_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="blog_format_agent",
    description="Generates a long-form blog post version.",
    instruction=(
        "You are a blog content specialist. Using the content from the user"
        " or session state, produce a complete blog post:\n\n"
        "- 800-1500 words with H2/H3 headings\n"
        "- SEO-optimized title (50-60 chars)\n"
        "- Meta description (150-160 chars)\n"
        "- 3-5 internal link placeholders\n"
        "- Author-friendly conversational tone\n\n"
        "Store output in state key 'blog_version'."
    ),
    output_key="blog_version",
)

social_format_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="social_format_agent",
    description="Generates social media posts for multiple platforms.",
    instruction=(
        "You are a social media strategist. Using the content from the user"
        " or session state, produce platform-specific posts:\n\n"
        "1. **LinkedIn** (1300 chars): Professional hook, 3 key insights, CTA\n"
        "2. **Twitter/X** (280 chars): Punchy one-liner with hashtags\n"
        "3. **Twitter/X Thread** (5-7 tweets): Breakdown with thread emoji\n"
        "4. **Instagram Caption** (2200 chars): Story-driven, emoji-rich\n\n"
        "Store output in state key 'social_version'."
    ),
    output_key="social_version",
)

email_format_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="email_format_agent",
    description="Generates a newsletter email version.",
    instruction=(
        "You are an email marketing specialist. Using the content from the"
        " user or session state, produce a newsletter email:\n\n"
        "- Subject line (40-60 chars, curiosity-driven)\n"
        "- Preview text (90-130 chars)\n"
        "- Body: Hook → 3 key points → CTA\n"
        "- Keep under 500 words\n"
        "- Include 1-2 link placeholders\n\n"
        "Store output in state key 'email_version'."
    ),
    output_key="email_version",
)

exec_summary_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="exec_summary_agent",
    description="Generates a concise executive summary.",
    instruction=(
        "You are a business communications expert. Using the content from"
        " the user or session state, produce an executive summary:\n\n"
        "- 150-250 words maximum\n"
        "- Lead with the 'so what' — why this matters\n"
        "- 3-5 bullet points of key takeaways\n"
        "- Recommended next steps or actions\n"
        "- No jargon, no fluff\n\n"
        "Store output in state key 'exec_summary'."
    ),
    output_key="exec_summary",
)

multi_format_generator = ParallelAgent(
    name="multi_format_generator",
    description=(
        "Generates content in 4 formats simultaneously: blog post, social"
        " media posts, newsletter email, and executive summary. Use this"
        " when the user needs the same content adapted for multiple channels."
    ),
    sub_agents=[
        blog_format_agent,
        social_format_agent,
        email_format_agent,
        exec_summary_agent,
    ],
)


# =============================================================================
# 4. LOOP AGENT — Iterative Quality Refinement
# =============================================================================
# Writer produces content, Critic evaluates it. Loop continues until
# the Critic signals approval or max iterations is reached.

iterative_writer = LlmAgent(
    model="gemini-2.5-flash",
    name="iterative_writer",
    description="Writes or rewrites content based on critique feedback.",
    instruction=(
        "You are a skilled content writer engaged in iterative refinement.\n\n"
        "If this is the FIRST iteration (no critique in state):\n"
        "  - Write a complete piece based on the user's request\n\n"
        "If critique feedback exists in state (key: 'critique'):\n"
        "  - Read the previous draft from state (key: 'current_draft')\n"
        "  - Read the critique from state (key: 'critique')\n"
        "  - Rewrite the content addressing EVERY point in the critique\n"
        "  - Do NOT simply acknowledge the feedback — apply it\n\n"
        "Always store your output in state key 'current_draft'."
    ),
    output_key="current_draft",
)

quality_critic = LlmAgent(
    model="gemini-2.5-flash",
    name="quality_critic",
    description="Evaluates content quality and signals when it passes.",
    instruction=(
        "You are a demanding content quality reviewer. Read the current draft"
        " from state (key: 'current_draft') and evaluate it against:\n\n"
        "1. **Clarity** (1-10): Is it easy to understand?\n"
        "2. **Engagement** (1-10): Does it hook and hold attention?\n"
        "3. **Accuracy** (1-10): Are claims supported and precise?\n"
        "4. **Structure** (1-10): Is the flow logical with clear headings?\n"
        "5. **Actionability** (1-10): Does the reader know what to do next?\n\n"
        "Calculate an overall score (average of all 5).\n\n"
        "If overall score >= 8.0:\n"
        "  - Respond with 'APPROVED' on the first line\n"
        "  - Provide brief praise for what works well\n\n"
        "If overall score < 8.0:\n"
        "  - List specific, actionable improvements needed\n"
        "  - Be precise: quote the weak text, suggest better alternatives\n"
        "  - Focus on the 2-3 most impactful changes\n\n"
        "Store your evaluation in state key 'critique'."
    ),
    output_key="critique",
)

quality_loop = LoopAgent(
    name="quality_loop",
    description=(
        "Iterative content refinement loop. A writer produces content,"
        " a critic evaluates it, and the loop continues until the critic"
        " approves (score >= 8/10) or 3 iterations are reached. Use this"
        " when the user needs high-quality, polished content."
    ),
    sub_agents=[iterative_writer, quality_critic],
    max_iterations=3,
)


# =============================================================================
# 5. ROOT ORCHESTRATOR — Intelligent Routing
# =============================================================================
# The root agent decides which workflow to invoke based on the user's request.

root_agent = LlmAgent(
    model="gemini-2.5-flash",
    name="enterprise_content_ops",
    description="Enterprise content operations system with multi-agent workflows.",
    instruction=(
        "You are an enterprise content operations assistant powered by a"
        " team of specialized AI agents. You route user requests to the"
        " most appropriate workflow.\n\n"
        "## Available Workflows\n\n"
        "### 1. Content Pipeline (Sequential)\n"
        "Use `content_pipeline` when the user wants a fully produced piece"
        " of content from scratch. This runs: Research → Draft → Review.\n"
        "Example: 'Write me an article about AI in healthcare'\n\n"
        "### 2. Multi-Format Generator (Parallel)\n"
        "Use `multi_format_generator` when the user has content and wants it"
        " adapted for multiple channels simultaneously (blog, social, email,"
        " exec summary).\n"
        "Example: 'Take this content and create versions for all channels'\n\n"
        "### 3. Quality Refinement (Loop)\n"
        "Use `quality_loop` when the user explicitly wants iterative"
        " refinement — high-polish content that goes through critique cycles.\n"
        "Example: 'Write a really polished piece about X, keep refining'\n\n"
        "### 4. Skills (Direct)\n"
        "Use skills directly when the user needs a specific capability:\n"
        "  - `seo-checklist`: SEO review of existing content\n"
        "  - `blog-writer`: Blog writing guidelines\n"
        "  - `content-research-writer`: Research methodology\n"
        "  - `skill-creator`: Create new skill definitions\n\n"
        "## Routing Rules\n"
        "1. If the request is about creating new content → content_pipeline\n"
        "2. If the request mentions multiple formats/channels → multi_format_generator\n"
        "3. If the request emphasizes quality/polish/iteration → quality_loop\n"
        "4. If the request is about SEO, skills, or specific tools → use skills\n"
        "5. For simple questions or clarifications → respond directly\n\n"
        "Always explain which workflow you're using and why."
    ),
    tools=[skill_toolset],
    sub_agents=[content_pipeline, multi_format_generator, quality_loop],
)
