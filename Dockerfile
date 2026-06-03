FROM python:3.12-slim

WORKDIR /app

# Install curl for health checks and eval loading
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source, eval sets, and startup script
COPY app/ ./app/
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Ensure .adk directories exist and are writable
RUN mkdir -p ./app/.adk/eval_sets ./app/.adk/eval_history && chmod -R 777 ./app/.adk

# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

# Use entrypoint script that starts ADK web + loads evals
CMD ["./entrypoint.sh"]
