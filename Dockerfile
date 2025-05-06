FROM python:3.10-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    libpq-dev \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    DJANGO_SETTINGS_MODULE=MAAMS_NG_BE.settings \
    PORT=8000

RUN groupadd -r appuser && useradd -r -g appuser appuser

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    default-mysql-client \
    libpq5 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*

COPY . /app/

RUN mkdir -p /app/staticfiles /app/mediafiles /app/logs && \
    chown -R appuser:appuser /app && \
    chmod -R 755 /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    chown appuser:appuser /entrypoint.sh

USER appuser

RUN DJANGO_SETTINGS_MODULE=MAAMS_NG_BE.settings \
    DATABASE_URL=sqlite:///db.sqlite3 \
    SECRET_KEY=dummy \
    python manage.py collectstatic --noinput || true

EXPOSE $PORT

ENTRYPOINT ["/entrypoint.sh"]