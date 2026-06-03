FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source and eval sets
COPY app/ ./app/

# Cloud Run injects PORT env var (default 8080)
EXPOSE 8080

# Use shell form so $PORT is expanded at runtime
CMD adk web --port ${PORT:-8080} --host 0.0.0.0
