"""Deploy Enterprise Content Ops Agent to Vertex AI Agent Engine.

Usage (from GCP Cloud Shell):
    # First time: authenticate and create staging bucket
    gcloud auth application-default login
    gsutil mb -l us-central1 gs://YOUR_PROJECT-adk-staging

    # Deploy
    python deploy.py
    python deploy.py --project mygenerativeai
    python deploy.py --dry-run
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="Deploy agent to Vertex AI Agent Engine")
    parser.add_argument("--project", default=os.environ.get("GOOGLE_CLOUD_PROJECT", "mygenerativeai"))
    parser.add_argument("--region", default=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"))
    parser.add_argument("--staging-bucket", default=None, help="GCS bucket for staging (e.g. gs://my-bucket)")
    parser.add_argument("--dry-run", action="store_true", help="Validate without deploying")
    parser.add_argument("--display-name", default="Enterprise Content Ops Agent")
    args = parser.parse_args()

    print(f"{'🧪 DRY RUN' if args.dry_run else '🚀 DEPLOYING'}")
    print(f"   Project:  {args.project}")
    print(f"   Region:   {args.region}")
    print(f"   Agent:    {args.display_name}")
    print()

    # ── Step 1: Validate agent import ────────────────────────
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

    # ── Step 2: Check authentication ─────────────────────────
    print("\n🔐 Checking authentication...")

    try:
        import google.auth
        credentials, project = google.auth.default()
        cred_type = type(credentials).__name__
        print(f"   ✅ Credentials found: {cred_type}")
        if project:
            print(f"   ✅ Default project: {project}")
    except google.auth.exceptions.DefaultCredentialsError:
        print("   ❌ No credentials found!")
        print("   Run: gcloud auth application-default login")
        print("   Or set: GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json")
        sys.exit(1)

    # ── Step 3: Determine staging bucket ─────────────────────
    staging_bucket = args.staging_bucket or f"gs://{args.project}-adk-staging"
    print(f"\n📦 Staging bucket: {staging_bucket}")

    # Check if bucket exists, create if not
    try:
        from google.cloud import storage
        client = storage.Client(project=args.project)
        bucket_name = staging_bucket.replace("gs://", "")
        bucket = client.bucket(bucket_name)
        if not bucket.exists():
            print(f"   Creating bucket {staging_bucket}...")
            bucket = client.create_bucket(bucket_name, location=args.region)
            print(f"   ✅ Bucket created")
        else:
            print(f"   ✅ Bucket exists")
    except Exception as e:
        print(f"   ⚠️  Could not verify bucket: {e}")
        print(f"   Create it manually: gsutil mb -l {args.region} {staging_bucket}")

    # ── Step 4: Deploy to Agent Engine ───────────────────────
    print("\n☁️  Deploying to Vertex AI Agent Engine...")
    print("   (This may take 3-5 minutes...)")

    try:
        import vertexai
        from vertexai import agent_engines

        vertexai.init(
            project=args.project,
            location=args.region,
            staging_bucket=staging_bucket,
        )

        agent_engine = agent_engines.create(
            agent_engine=root_agent,
            display_name=args.display_name,
            description=(
                "Multi-agent content operations system demonstrating ADK 2.0"
                " workflows: SequentialAgent pipeline, ParallelAgent fan-out,"
                " LoopAgent refinement, and 4 skill patterns."
            ),
            requirements=[
                "google-adk[eval]>=2.1.0",
                "google-cloud-aiplatform>=1.154.0",
                "cloudpickle>=3.1.0",
                "pydantic>=2.12.0",
            ],
        )

        print(f"\n{'━' * 55}")
        print(f"✅ DEPLOYED SUCCESSFULLY")
        print(f"{'━' * 55}")
        print(f"   Resource: {agent_engine.resource_name}")
        print(f"   Name:     {args.display_name}")
        print(f"   Project:  {args.project}")
        print(f"   Region:   {args.region}")
        print()
        print("📋 Test in production:")
        print(f"   from vertexai import agent_engines")
        print(f"   engine = agent_engines.get('{agent_engine.resource_name}')")
        print(f"   session = engine.create_session(user_id='test-user')")
        print(f"   resp = session.send_message('What workflows do you have?')")
        print(f"   print(resp.text)")
        print()
        print("🔗 Console:")
        print(f"   https://console.cloud.google.com/ai/agent-engine?project={args.project}")
        print(f"{'━' * 55}")

    except ImportError:
        print("   ❌ google-cloud-aiplatform not installed.")
        print("   Run: pip install google-cloud-aiplatform>=1.90.0")
        sys.exit(1)
    except Exception as e:
        error_msg = str(e)
        print(f"\n   ❌ Deployment failed: {error_msg}")
        print()

        if "missing 'email'" in error_msg or "metadata server" in error_msg:
            print("   🔧 FIX: Cloud Shell metadata auth doesn't work with Agent Engine.")
            print("   Run this first, then retry:")
            print("     gcloud auth application-default login")
        elif "staging_bucket" in error_msg or "bucket" in error_msg.lower():
            print("   🔧 FIX: Create a staging bucket:")
            print(f"     gsutil mb -l {args.region} {staging_bucket}")
        elif "403" in error_msg or "permission" in error_msg.lower():
            print("   🔧 FIX: Enable APIs and grant permissions:")
            print("     gcloud services enable aiplatform.googleapis.com")
            print(f"     gcloud projects add-iam-policy-binding {args.project} \\")
            print(f"       --member='user:$(gcloud config get account)' \\")
            print(f"       --role='roles/aiplatform.admin'")
        else:
            print("   🔧 Common fixes:")
            print("     1. gcloud auth application-default login")
            print(f"     2. gsutil mb -l {args.region} {staging_bucket}")
            print("     3. gcloud services enable aiplatform.googleapis.com")

        sys.exit(1)


if __name__ == "__main__":
    main()
