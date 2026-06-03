#!/bin/bash
set -e

PORT=${PORT:-8080}

# Start ADK web in background
adk web --port $PORT --host 0.0.0.0 &
ADK_PID=$!

# Wait for server to be ready
echo "⏳ Waiting for ADK server..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:$PORT/list-apps > /dev/null 2>&1; then
    echo "✅ ADK server ready"
    break
  fi
  sleep 1
done

# Load eval sets via API
echo "📦 Loading eval sets..."
for f in /app/app/*.evalset.json; do
  if [ -f "$f" ]; then
    EVAL_SET=$(cat "$f")
    RESPONSE=$(curl -sf -X POST "http://localhost:$PORT/dev/apps/app/eval-sets" \
      -H "Content-Type: application/json" \
      -d "{\"evalSet\": $EVAL_SET}" 2>&1 || true)
    BASENAME=$(basename "$f")
    echo "  ✅ Loaded: $BASENAME"
  fi
done

echo "🚀 ADK running on port $PORT with evals loaded"

# Wait for ADK process
wait $ADK_PID
