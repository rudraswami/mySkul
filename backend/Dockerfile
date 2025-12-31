# ===================================================
# PRODUCTION DOCKERFILE - Optimized for Railway (< 2GB)
# Multi-stage build to minimize final image size
# ===================================================
# 
# NOTE: Railway build context is REPO ROOT (not backend/)
# because Dockerfile path is /backend/Dockerfile
# So we must COPY from backend/ explicitly
# ===================================================

# === STAGE 1: Builder ===
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies (only in builder stage)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy production requirements from backend/
COPY backend/requirements-prod.txt .

# Install Python dependencies into a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install deps with no cache to reduce size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-prod.txt


# === STAGE 2: Production Runtime ===
FROM python:3.11-slim AS runtime

WORKDIR /app

# Install only runtime system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean \
    && rm -rf /var/cache/apt/archives/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy ONLY backend/ contents as app root
# This makes /app contain: main.py, api/, services/, core/, etc.
COPY backend/ .

# Remove unnecessary files from final image
RUN rm -rf \
    tests/ \
    scripts/ \
    *.md \
    __pycache__/ \
    .pytest_cache/ \
    .mypy_cache/ \
    requirements.txt \
    requirements-dev.txt \
    audio_processor.py \
    Dockerfile \
    .dockerignore \
    2>/dev/null || true

# Create necessary directories
RUN mkdir -p logs temp

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
