# Technical overview

## Language and framework

FAWS consists of a Python 3.13 backend and a JavaScript frontend.

| Area | Implementation |
| --- | --- |
| Backend | Django 6, Django REST Framework, Gunicorn |
| Frontend | Vue 3, Vite, Vuetify, Pinia, Vue Router, Vue I18n |
| Authentication | JWT through Django REST Framework Simple JWT |
| Persistence | SQLite in the standalone image; configurable MySQL support |
| Reports | ReportLab for PDF and openpyxl for XLSX |
| Web entry point | Nginx serving the SPA and proxying Django routes |

Python dependencies are pinned in [`requirements.txt`](../requirements.txt). Frontend version ranges are declared in [`frontend/package.json`](../frontend/package.json) and resolved by `frontend/package-lock.json`.

## Architecture

The Vue single-page application calls the Django REST API under `/api/`. Nginx serves frontend assets, uploaded media, and collected Django static files, and proxies `/api/` and `/admin/` to Gunicorn.

Django is divided into business applications:

- `usuarios`: initial setup, users, groups, permissions, company settings, preferences, and audit records
- `terceros`: customers, suppliers, and payment methods
- `inventario`: products, categories, units, stock, and movements
- `ventas` and `compras`: transactions and their detail lines
- `finanzas`: receivables, payables, and payments
- `contabilidad`: accounts, journals, periods, and reports

Service modules coordinate cross-domain operations inside database transactions. Sales and purchases update inventory and accounting; credit operations create receivables or payables; payments update balances and accounting entries.

## Persistence and configuration

The standalone container sets `FAWS_DATA_DIR=/data` and defaults to SQLite at `/data/faws.sqlite3`. Media is stored at `/data/media`, and a generated Django secret is retained at `/data/.django_secret_key` unless `DJANGO_SECRET_KEY` is supplied.

Django configuration is environment-based. Supported storage variables include `DATABASE_ENGINE`, `SQLITE_PATH`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_HOST`, `MYSQL_PORT`, `FAWS_DATA_DIR`, and `MEDIA_ROOT`. Security and origin settings use the `DJANGO_*`, `CORS_ALLOWED_ORIGINS`, and `CSRF_TRUSTED_ORIGINS` variables defined in [`backend/config/settings.py`](../backend/config/settings.py).

## System integrations

The application exposes an OpenAPI schema at `/api/schema/`, Swagger UI at `/api/docs/`, and a database-aware health check at `/api/health/`.

There is no implemented connection to an external accounting platform, payment provider, tax authority, cloud storage provider, or synchronization service. Electronic receipt records are preparatory drafts only; the service explicitly performs no communication with Costa Rica's Ministry of Finance.

## Packaging and distribution

The root [`Dockerfile`](../Dockerfile) builds the Vue application and packages it with Django, Gunicorn, and Nginx in one Linux image. [`compose.yml`](../compose.yml) publishes port `8080` by default and attaches the `faws_data` volume.

GitHub Actions checks Django, runs backend and frontend tests, lints and builds the frontend, builds the standalone container image, and exercises a clean installation. A separate workflow publishes multi-architecture images to GitHub Container Registry from `main` and version tags.

## Repository structure

```text
.
├── backend/               Django project and business applications
├── frontend/              Vue single-page application
├── docker/                Container entrypoint and Nginx configuration
├── docs/                  User and technical documentation
│   └── screenshots/       Independent, sanitized product captures
├── scripts/               Validation scripts
├── .github/workflows/     Continuous integration and image publishing
├── compose.yml            Standalone Docker Compose service
├── Dockerfile             Multi-stage standalone image
└── requirements.txt       Python dependencies
```

[Documentation index](index.md) · [Project README](../README.md)
