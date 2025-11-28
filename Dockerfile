# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    GUNICORN_WORKERS=2

WORKDIR /app

# Create data directory for SQLite (avoids 'unable to open database file')
RUN mkdir -p /data

# Install system dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . /app

# Default DB location (mount a volume to /data for persistence)
ENV DATABASE_PATH=/data/market_data.db

EXPOSE 8080

# Optional healthcheck (uses curl)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT:-8080}/ || exit 1

# Run with Gunicorn
CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS:-2} -b 0.0.0.0:${PORT} app:app"]
