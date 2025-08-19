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

# Run migrations, collectstatic, create superuser (if not exists), then start Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && \
python manage.py collectstatic --noinput && \
python manage.py shell -c \"import os; \
from django.contrib.auth import get_user_model; \
User = get_user_model(); \
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin'); \
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com'); \
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'adminpass'); \
User.objects.filter(username=username).exists() or \
User.objects.create_superuser(username, email, password)\" && \
gunicorn online_judge.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3 --timeout 120"]
