# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    GUNICORN_WORKERS=2

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy application
COPY . /app

# Default DB location (mount a volume to /data for persistence)
ENV DATABASE_PATH=/data/market_data.db

EXPOSE 8080

# Optional healthcheck (skips extra packages)
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import urllib.request, sys, os\nport = os.environ.get('PORT', '8080')\nurl = f'http://127.0.0.1:{port}/api/imports'\ntry:\n    with urllib.request.urlopen(url, timeout=3) as r:\n        sys.exit(0 if r.status == 200 else 1)\nexcept Exception:\n    sys.exit(1)\n"]

# Run with Gunicorn
CMD ["sh", "-c", "gunicorn -w ${GUNICORN_WORKERS:-2} -b 0.0.0.0:${PORT} app:app"]
