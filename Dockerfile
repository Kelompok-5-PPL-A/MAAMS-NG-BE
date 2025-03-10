FROM python:3.9-slim

ARG ENVIRONMENT
ARG DATABASE_URL
ARG DATABASE_USERNAME
ARG DATABASE_PASSWORD
ARG SECRET_KEY

ENV ENVIRONMENT=${ENVIRONMENT}
ENV DATABASE_URL=${DATABASE_URL}
ENV DATABASE_USERNAME=${DATABASE_USERNAME}
ENV DATABASE_PASSWORD=${DATABASE_PASSWORD}
ENV SECRET_KEY=${SECRET_KEY}
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

RUN if [ "$ENVIRONMENT" = "staging" ] || [ "$ENVIRONMENT" = "development" ]; then \
    python manage.py migrate; \
    fi

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "MAAMS_NG_BE.wsgi:application"]