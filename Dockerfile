# ---- base: runtime deps only, shared by test and runtime stages ----
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ACEEST_DB=/app/data/aceest_fitness.db

WORKDIR /app

# unprivileged user, sqlite file lives in a dir it owns
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /app/data && chown appuser:appuser /app/data

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .

# ---- test: adds pytest/flake8 + tests (used by CI) ----
FROM base AS test
COPY requirements-dev.txt .
RUN pip install -r requirements-dev.txt
COPY tests/ tests/
USER appuser
CMD ["pytest", "tests/", "-v"]

# ---- runtime: default target, no test tooling ----
FROM base AS runtime
USER appuser
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/')" || exit 1
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
