FROM python:3.10-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --upgrade typing-extensions && \
    pip install --upgrade groq

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --chown=appuser:appuser . .
RUN rm -rf .git .env* .vscode secrets* && \
    find . -type f -name "*.log" -delete

USER appuser

ARG ENVIRONMENT
ARG SECRET_KEY

ENV ENVIRONMENT=${ENVIRONMENT}
ENV SECRET_KEY=${SECRET_KEY}

RUN if [ "$ENVIRONMENT" = "staging" ] || [ "$ENVIRONMENT" = "development" ]; then \
    python manage.py migrate; \
    fi

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "MAAMS_NG_BE.wsgi:application"]