FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source and eval sets
COPY app/ ./app/

# Eval files at ./app/*.evalset.json are auto-discovered by ADK Web UI

# Ensure .adk directories exist and are writable
RUN mkdir -p ./app/.adk/eval_sets ./app/.adk/eval_history && chmod -R 777 ./app/.adk

# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

# Start ADK web directly — eval sets are already at ./app/*.evalset.json
CMD ["sh", "-c", "adk web --port ${PORT:-8080} --host 0.0.0.0"]
