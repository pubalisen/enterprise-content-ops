"""Test all sub-agents and workflow patterns.

Usage:
    cd enterprise-content-ops
    source .venv/bin/activate
    python test_agents.py                  # Run all tests
    python test_agents.py --sequential     # Test only sequential pipeline
    python test_agents.py --parallel       # Test only parallel generator
    python test_agents.py --loop           # Test only quality loop
    python test_agents.py --skills         # Test only skills
    python test_agents.py --routing        # Test only routing logic
"""

import argparse
import asyncio
import os
import time

from dotenv import load_dotenv
load_dotenv("app/.env")

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.agent import root_agent


# ─── Test Infrastructure ─────────────────────────────────────

session_service = InMemorySessionService()

async def run_query(query: str, test_name: str, session_id: str = None) -> str:
    """Send a query to the root agent and return the response."""
    sid = session_id or f"test-{test_name}-{int(time.time())}"

    session = await session_service.create_session(
        app_name="enterprise_content_ops",
        user_id="test-user",
        session_id=sid,
    )

    runner = Runner(
        agent=root_agent,
        app_name="enterprise_content_ops",
        session_service=session_service,
    )

    content = types.Content(
        role="user",
        parts=[types.Part.from_text(text=query)],
    )

    response_text = ""
    async for event in runner.run_async(
        user_id="test-user",
        session_id=session.id,
        new_message=content,
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    response_text += part.text

    return response_text


def print_result(test_name: str, query: str, response: str, duration: float):
    """Pretty print a test result."""
    passed = len(response) > 50  # Basic check: got a meaningful response
    status = "✅ PASS" if passed else "❌ FAIL"

    print(f"\n{'━' * 70}")
    print(f"{status}  {test_name}")
    print(f"{'━' * 70}")
    print(f"  Query:    {query[:80]}...")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Response: {len(response)} chars")
    print(f"  Preview:  {response[:200].strip()}...")
    return passed


# ─── Test Cases ──────────────────────────────────────────────

async def test_sequential():
    """Test the SequentialAgent content pipeline."""
    query = (
        "Write a short article about how AI is transforming healthcare diagnostics. "
        "Use the full content pipeline: research, draft, and review."
    )
    start = time.time()
    response = await run_query(query, "sequential")
    return print_result(
        "Sequential Pipeline (Research → Draft → Review)",
        query, response, time.time() - start
    )


async def test_parallel():
    """Test the ParallelAgent multi-format generator."""
    query = (
        "I have content about 'The Rise of Remote Work in 2026'. "
        "Generate versions for all channels: blog, social media, email newsletter, "
        "and executive summary. Use the multi-format generator."
    )
    start = time.time()
    response = await run_query(query, "parallel")
    return print_result(
        "Parallel Generator (Blog + Social + Email + Exec Summary)",
        query, response, time.time() - start
    )


async def test_loop():
    """Test the LoopAgent quality refinement."""
    query = (
        "Write a really polished thought leadership piece about why companies "
        "should invest in developer experience (DevEx) in 2026. "
        "Keep refining until it's excellent quality."
    )
    start = time.time()
    response = await run_query(query, "loop")
    return print_result(
        "Quality Loop (Writer → Critic → Rewrite, up to 3 rounds)",
        query, response, time.time() - start
    )


async def test_skills_seo():
    """Test inline skill: SEO checklist."""
    query = (
        "Review this blog post for SEO: "
        "'Getting Started with Kubernetes: A Beginner Guide. "
        "Kubernetes is a container orchestration platform. "
        "It helps you manage containers at scale.'"
    )
    start = time.time()
    response = await run_query(query, "skills-seo")
    return print_result(
        "Skill: SEO Checklist (inline)",
        query, response, time.time() - start
    )


async def test_skills_research():
    """Test file-based skill: content research."""
    query = (
        "Use your content research skill to help me research the current state "
        "of quantum computing for enterprise applications."
    )
    start = time.time()
    response = await run_query(query, "skills-research")
    return print_result(
        "Skill: Content Research Writer (file-based)",
        query, response, time.time() - start
    )


async def test_skills_meta():
    """Test meta skill: skill creator."""
    query = (
        "I need a new skill for reviewing Python code for security vulnerabilities. "
        "Can you create a SKILL.md for it?"
    )
    start = time.time()
    response = await run_query(query, "skills-meta")
    return print_result(
        "Skill: Skill Creator (meta — generates new skills)",
        query, response, time.time() - start
    )


async def test_routing():
    """Test that the root orchestrator routes correctly."""
    query = "What workflows do you have available? List them all with descriptions."
    start = time.time()
    response = await run_query(query, "routing")
    return print_result(
        "Routing: Root Orchestrator (lists capabilities)",
        query, response, time.time() - start
    )


async def test_edge_nonexistent_skill():
    """Test edge case: request a skill that doesn't exist."""
    query = "Can you use your video-editing skill to create a thumbnail?"
    start = time.time()
    response = await run_query(query, "edge-nonexistent")
    return print_result(
        "Edge Case: Non-existent skill (graceful handling)",
        query, response, time.time() - start
    )


# ─── Main ────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Test Enterprise Content Ops Agent")
    parser.add_argument("--sequential", action="store_true", help="Test sequential pipeline only")
    parser.add_argument("--parallel", action="store_true", help="Test parallel generator only")
    parser.add_argument("--loop", action="store_true", help="Test quality loop only")
    parser.add_argument("--skills", action="store_true", help="Test skills only")
    parser.add_argument("--routing", action="store_true", help="Test routing only")
    args = parser.parse_args()

    run_all = not any([args.sequential, args.parallel, args.loop, args.skills, args.routing])

    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║         Enterprise Content Ops — Agent Test Suite                   ║")
    print("║         ADK 2.0 | google-adk 2.1.0                                 ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")

    results = []
    total_start = time.time()

    if run_all or args.routing:
        results.append(("Routing", await test_routing()))

    if run_all or args.sequential:
        results.append(("Sequential", await test_sequential()))

    if run_all or args.parallel:
        results.append(("Parallel", await test_parallel()))

    if run_all or args.loop:
        results.append(("Loop", await test_loop()))

    if run_all or args.skills:
        results.append(("SEO Skill", await test_skills_seo()))
        results.append(("Research Skill", await test_skills_research()))
        results.append(("Meta Skill", await test_skills_meta()))
        results.append(("Edge Case", await test_edge_nonexistent_skill()))

    # Summary
    total_time = time.time() - total_start
    passed = sum(1 for _, p in results if p)
    failed = sum(1 for _, p in results if not p)

    print(f"\n{'═' * 70}")
    print(f"  RESULTS: {passed} passed, {failed} failed, {len(results)} total")
    print(f"  TIME:    {total_time:.1f}s total")
    print(f"{'═' * 70}")

    for name, p in results:
        print(f"  {'✅' if p else '❌'} {name}")

    print(f"{'═' * 70}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
