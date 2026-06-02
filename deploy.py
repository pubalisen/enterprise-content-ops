"""Deploy Enterprise Content Ops Agent to Vertex AI Agent Engine.

Usage:
    python deploy.py                          # Deploy to default project
    python deploy.py --project my-project     # Deploy to specific project
    python deploy.py --region us-central1     # Deploy to specific region
    python deploy.py --dry-run                # Validate without deploying
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Deploy agent to Vertex AI Agent Engine")
    parser.add_argument("--project", default=os.environ.get("GOOGLE_CLOUD_PROJECT", "robust-habitat-467517-r6"))
    parser.add_argument("--region", default=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"))
    parser.add_argument("--dry-run", action="store_true", help="Validate without deploying")
    parser.add_argument("--display-name", default="Enterprise Content Ops Agent")
    args = parser.parse_args()

    print(f"{'🧪 DRY RUN' if args.dry_run else '🚀 DEPLOYING'}")
    print(f"   Project:  {args.project}")
    print(f"   Region:   {args.region}")
    print(f"   Agent:    {args.display_name}")
    print()

    # Validate the agent can be imported
    print("📦 Validating agent...")
    try:
        from app.agent import root_agent
        print(f"   ✅ Root agent: {root_agent.name}")
        print(f"   ✅ Sub-agents: {[a.name for a in root_agent.sub_agents]}")
        print(f"   ✅ Tools: {len(root_agent.tools)} toolset(s)")
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        sys.exit(1)

    if args.dry_run:
        print("\n🧪 Dry run complete — agent is valid and ready to deploy.")
        return

    # Deploy to Agent Engine
    print("\n☁️ Deploying to Vertex AI Agent Engine...")
    try:
        import vertexai
        from vertexai import agent_engines

        vertexai.init(project=args.project, location=args.region)

        agent_engine = agent_engines.create(
            agent_engine=root_agent,
            display_name=args.display_name,
            description=(
                "Multi-agent content operations system demonstrating ADK 2.0"
                " workflows: SequentialAgent pipeline, ParallelAgent fan-out,"
                " LoopAgent refinement, and 4 skill patterns."
            ),
        )

        print(f"\n✅ Deployed successfully!")
        print(f"   Resource name: {agent_engine.resource_name}")
        print(f"   Display name:  {args.display_name}")
        print(f"\n📋 To test in production:")
        print(f"   session = agent_engine.create_session(user_id='test-user')")
        print(f"   response = session.send_message('Write an article about AI trends')")

    except ImportError:
        print("   ❌ google-cloud-aiplatform not installed.")
        print("   Run: pip install google-cloud-aiplatform>=1.90.0")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
