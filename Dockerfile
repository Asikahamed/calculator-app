# ── Stage 1: Test ─────────────────────────────────────────
FROM python:3.12-slim AS test

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install -e .

RUN pytest tests/ \
      --cov=app \
      --cov-report=term-missing \
      --cov-fail-under=80 \
      -v

# ── Stage 2: Production ───────────────────────────────────
FROM python:3.12-slim AS production

WORKDIR /app

# Non-root user for security
RUN adduser --disabled-password --gecos "" appuser

# Copy dependencies
COPY --from=test /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=test /usr/local/bin/uvicorn /usr/local/bin/uvicorn

# Copy app code
COPY app/ ./app/

# 🔥 FIX: give ownership to appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--timeout-graceful-shutdown", "30"]
