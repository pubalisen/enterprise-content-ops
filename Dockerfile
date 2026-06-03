FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source, eval sets, and .adk directory
COPY app/ ./app/

# Ensure .adk directories exist and are writable
RUN mkdir -p ./app/.adk/eval_sets ./app/.adk/eval_history && chmod -R 777 ./app/.adk

# Copy eval sets to BOTH locations (app root for CLI, .adk for Web UI)
RUN cp -f ./app/*.evalset.json ./app/.adk/eval_sets/ 2>/dev/null || true

# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

# Use shell form so $PORT is expanded at runtime
CMD adk web --port ${PORT:-8080} --host 0.0.0.0
