"""Deploy to Vertex AI Agent Engine and register in the Agent Registry.

Usage (from Cloud Shell or local with gcloud auth):

    # Deploy to Agent Engine
    python deploy_to_registry.py

    # Deploy to a specific project
    python deploy_to_registry.py --project mygenerativeai --region us-central1

    # Dry run (validate only)
    python deploy_to_registry.py --dry-run

    # List existing deployed agents
    python deploy_to_registry.py --list
"""

import argparse
import os
import sys

from dotenv import load_dotenv
load_dotenv("app/.env")


def main():
    parser = argparse.ArgumentParser(description="Deploy agent to Vertex AI Agent Engine")
    parser.add_argument("--project", default=os.environ.get("GOOGLE_CLOUD_PROJECT", "mygenerativeai"))
    parser.add_argument("--region", default=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"))
    parser.add_argument("--display-name", default="Enterprise Content Ops Agent")
    parser.add_argument("--dry-run", action="store_true", help="Validate without deploying")
    parser.add_argument("--list", action="store_true", help="List existing deployed agents")
    args = parser.parse_args()

    # ─── Validate Agent ──────────────────────────────────────
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║       Deploy to Vertex AI Agent Engine & Registry          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print()
    print(f"  Project:  {args.project}")
    print(f"  Region:   {args.region}")
    print(f"  Agent:    {args.display_name}")
    print()

    # Import and validate
    print("📦 Step 1: Validating agent structure...")
    try:
        from app.agent import root_agent
        print(f"   ✅ Root agent: {root_agent.name}")
        print(f"   ✅ Model: {root_agent.model}")
        sub_agents = root_agent.sub_agents or []
        print(f"   ✅ Sub-agents ({len(sub_agents)}):")
        for sa in sub_agents:
            agent_type = type(sa).__name__
            sub_count = len(sa.sub_agents) if hasattr(sa, 'sub_agents') and sa.sub_agents else 0
            print(f"       • {sa.name} ({agent_type}) — {sub_count} sub-agents")
        print(f"   ✅ Tools: {len(root_agent.tools)} toolset(s)")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        sys.exit(1)

    if args.dry_run:
        print("\n🧪 Dry run complete — agent is valid and ready to deploy.")
        return

    # ─── Initialize Vertex AI ────────────────────────────────
    print("\n☁️  Step 2: Initializing Vertex AI...")
    try:
        import vertexai
        from vertexai import agent_engines

        sa_key = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if sa_key:
            print(f"   Using service account from: {os.path.basename(sa_key)}")

        vertexai.init(project=args.project, location=args.region)
        print(f"   ✅ Vertex AI initialized ({args.project}/{args.region})")
    except Exception as e:
        print(f"   ❌ Vertex AI init failed: {e}")
        sys.exit(1)

    # ─── List existing agents ────────────────────────────────
    if args.list:
        print("\n📋 Step 3: Listing deployed agents...")
        try:
            engines = agent_engines.list()
            engines_list = list(engines)
            if not engines_list:
                print("   No agents deployed yet.")
            else:
                for eng in engines_list:
                    print(f"   • {eng.display_name or 'unnamed'}")
                    print(f"     Resource: {eng.resource_name}")
                    print()
        except Exception as e:
            print(f"   ❌ List failed: {e}")
        return

    # ─── Deploy ──────────────────────────────────────────────
    print("\n🚀 Step 3: Deploying to Agent Engine...")
    print("   (This may take 2-5 minutes...)")

    try:
        agent_engine = agent_engines.create(
            agent_engine=root_agent,
            display_name=args.display_name,
            description=(
                "Enterprise content operations system built with ADK 2.0. "
                "Demonstrates SequentialAgent (Research → Draft → Review), "
                "ParallelAgent (Blog + Social + Email + Exec Summary), "
                "LoopAgent (iterative quality refinement), and "
                "4 skill patterns (inline, file-based, external, meta)."
            ),
        )

        print(f"\n{'━' * 60}")
        print(f"✅ DEPLOYED SUCCESSFULLY")
        print(f"{'━' * 60}")
        print(f"  Resource:     {agent_engine.resource_name}")
        print(f"  Display Name: {args.display_name}")
        print(f"  Project:      {args.project}")
        print(f"  Region:       {args.region}")
        print()
        print("📋 Test your deployed agent:")
        print()
        print("  from vertexai import agent_engines")
        print(f"  engine = agent_engines.get('{agent_engine.resource_name}')")
        print("  session = engine.create_session(user_id='test-user')")
        print("  response = session.send_message('What workflows do you have?')")
        print("  print(response.text)")
        print()
        print("🔗 View in Console:")
        print(f"  https://console.cloud.google.com/ai/agent-engine?project={args.project}")
        print(f"{'━' * 60}")

    except Exception as e:
        print(f"\n   ❌ Deployment failed: {e}")
        print()
        print("   Common fixes:")
        print("   1. Enable API: gcloud services enable aiplatform.googleapis.com")
        print("   2. IAM role: roles/aiplatform.user on your account")
        print("   3. Quota: Check Vertex AI quotas in console")
        sys.exit(1)


if __name__ == "__main__":
    main()
