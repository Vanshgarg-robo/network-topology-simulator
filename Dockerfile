# =============================================================================
# Stage 1: Build Frontend (Node.js)
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN chmod -R +x node_modules/.bin && npm run build

# =============================================================================
# Stage 2: Python Build & Dependencies
# =============================================================================
FROM python:3.12-slim AS python-builder

WORKDIR /build

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# =============================================================================
# Stage 3: Production Runtime
# =============================================================================
FROM python:3.12-slim AS runtime

# Security: Create non-privileged system user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app -s /sbin/nologin appuser

WORKDIR /app

# Install curl for health checks
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed wheels from python-builder
COPY --from=python-builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app

# Copy application source & built frontend
COPY app/ /app/app/
COPY packets.json /app/
COPY --from=frontend-builder /frontend/dist /app/frontend/dist

# Set ownership
RUN chown -R appuser:appgroup /app /home/appuser

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
