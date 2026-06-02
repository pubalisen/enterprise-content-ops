FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source
COPY app/ ./app/

# Expose port — Cloud Run uses PORT env var
ENV PORT=8080
EXPOSE 8080

# Run the ADK Web UI (not api_server) so we get the full dev UI
CMD ["adk", "web", "--port", "8080", "--host", "0.0.0.0", "app"]
