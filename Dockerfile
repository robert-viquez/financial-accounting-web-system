FROM node:24-alpine AS frontend-build

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
ARG VITE_API_URL=/api/
ENV VITE_API_URL=$VITE_API_URL
RUN npm run build

FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=false \
    DJANGO_ALLOWED_HOSTS=* \
    DJANGO_SECURE_SSL_REDIRECT=false \
    DJANGO_SECURE_HSTS_SECONDS=0 \
    DJANGO_TRUST_X_FORWARDED_PROTO=true \
    FAWS_DATA_DIR=/data

WORKDIR /app

RUN apt-get update \
    && apt-get install --no-install-recommends -y default-libmysqlclient-dev gcc nginx pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

COPY backend/ /app/
COPY --from=frontend-build /build/dist/ /usr/share/nginx/html/
COPY docker/standalone-nginx.conf /etc/nginx/nginx.conf
COPY docker/standalone-entrypoint.sh /usr/local/bin/faws-entrypoint

RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data /app/staticfiles \
    && DJANGO_SECRET_KEY=build-only DATABASE_ENGINE=sqlite SQLITE_PATH=/tmp/build.sqlite3 python manage.py collectstatic --noinput \
    && chmod +x /usr/local/bin/faws-entrypoint \
    && chown -R appuser:appuser /data /app

VOLUME ["/data"]
EXPOSE 80

HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=6 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1/api/health/', timeout=3)"

ENTRYPOINT ["faws-entrypoint"]
