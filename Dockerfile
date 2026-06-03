FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy EVERYTHING (agent source, eval sets, entrypoint)
COPY app/ ./app/

# Debug: list what's in /app/app/ at build time
RUN echo "=== Files in /app/app/ ===" && ls -la /app/app/ && echo "=== Evalset files ===" && find /app -name "*.evalset.json" -exec echo {} \;

# Ensure .adk directories exist and are writable  
RUN mkdir -p /app/app/.adk/eval_sets /app/app/.adk/eval_history /app/.adk/artifacts && chmod -R 777 /app/.adk /app/app/.adk

# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

CMD ["sh", "-c", "echo '=== Runtime files ===' && ls -la /app/app/*.evalset.json 2>&1 && adk web --port ${PORT:-8080} --host 0.0.0.0"]
