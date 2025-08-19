FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      libjpeg62-turbo-dev \
      zlib1g-dev \
      curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir gunicorn whitenoise dj-database-url "psycopg[binary]"

# Copy project
COPY . /app

# Default to your Django project
ARG DJANGO_PROJECT=online_judge
ENV DJANGO_SETTINGS_MODULE=${DJANGO_PROJECT}.settings

EXPOSE 8000

# Run migrations, collectstatic, and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn CodeFun.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120"]

