# ─── Base stage ───────────────────────────────────────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ─── Development stage ────────────────────────────────────────────────────────
FROM base AS development

COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt

COPY . .

EXPOSE 8000

# Hot-reload enabled via --reload flag
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ─── Builder stage (install only production deps) ─────────────────────────────
FROM base AS builder

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt

# ─── Production stage ─────────────────────────────────────────────────────────
FROM base AS production

# Copy installed packages from builder
COPY --from=builder /install /usr/local

COPY . .

# Create a non-root user
RUN addgroup --system app && adduser --system --ingroup app app \
    && mkdir -p /app/media \
    && chown -R app:app /app

USER app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
