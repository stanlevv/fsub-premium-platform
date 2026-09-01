# Dockerfile — FSub Platform Engine (PRD v5.0 Hardened)
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements & install dependencies
COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

# Copy source code
COPY . .

# Environment & volume defaults
ENV PYTHONUNBUFFERED=1

# Healthcheck to detect zombie containers (PRD Council Meeting #6)
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import Kymang; print('OK')" || exit 1

CMD ["python", "-m", "Kymang"]

