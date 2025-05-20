# Build stage
FROM python:3.10-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.10-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    DJANGO_SETTINGS_MODULE=MAAMS_NG_BE.settings \
    PORT=8000

RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && apt-get update && apt-get install -y --no-install-recommends \
    curl \
    default-mysql-client \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . /app/

RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs /app/backups && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

# Copy and set up entrypoint and database scripts
COPY entrypoint.sh /entrypoint.sh
COPY scripts/db_backup.sh /app/scripts/db_backup.sh
COPY scripts/db_restore.sh /app/scripts/db_restore.sh
RUN chmod +x /entrypoint.sh /app/scripts/db_backup.sh /app/scripts/db_restore.sh && \
    chown appuser:appuser /entrypoint.sh /app/scripts/db_backup.sh /app/scripts/db_restore.sh

USER appuser

RUN DJANGO_SETTINGS_MODULE=MAAMS_NG_BE.settings \
    DATABASE_URL=${DATABASE_URL} \
    SECRET_KEY=${SECRET_KEY} \
    python manage.py collectstatic --noinput || true

EXPOSE $PORT

ENTRYPOINT ["/entrypoint.sh"]