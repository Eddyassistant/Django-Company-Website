FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y build-essential libpq-dev libjpeg-dev libpng-dev curl && rm -rf /var/lib/apt/lists/*
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen
COPY . .
RUN mkdir -p /app/media
ENV DJANGO_SETTINGS_MODULE=config.settings.production
RUN SECRET_KEY=build-placeholder uv run python manage.py collectstatic --noinput
HEALTHCHECK --interval=30s --timeout=10s CMD curl -f http://localhost:8000/health/ || exit 1
EXPOSE 8000
CMD ["sh", "-c", "uv run python manage.py migrate --noinput && uv run gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --access-logfile - --error-logfile -"]
