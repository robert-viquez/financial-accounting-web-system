# Installation and operation

A default Docker installation is intentionally separate from the public portfolio demo:

- no demo data or demo company identity is loaded;
- demo login prefill and demo seeding are disabled;
- no superuser—or any other user—is created automatically;
- application secrets and environment-specific configuration come from `.env`;
- MySQL and uploaded media persist in named Docker volumes.

## Requirements

- Git
- Docker Engine
- Docker Compose plugin

## Install

```bash
git clone https://github.com/robert-viquez/financial-accounting-web-system.git
cd financial-accounting-web-system
cp .env.example .env
# Replace CHANGE_ME values and add the server address to DJANGO_ALLOWED_HOSTS.
docker compose up -d --build
```

Open `http://SERVER_IP:5173` or the configured `FRONTEND_PORT`. On a fresh database, FAWS opens the initial setup screen. Create the first technical administrator there; no `createsuperuser` command is required. The setup endpoint becomes unavailable as soon as an active superuser exists.

See [`.env.example`](../.env.example) for the available configuration. Demo-specific settings are documented separately in the [portfolio demo deployment guide](deployment-demo.md).

## Verify

```bash
docker compose ps
curl --fail http://127.0.0.1:5173/api/health/
```

The backend entrypoint applies migrations and collects static files whenever its container starts.

## Upgrade

```bash
git pull
docker compose up -d --build
```

Back up important data before upgrading and verify the health endpoint afterward.

## Persistent storage

`mysql_data` stores MySQL data, `media_data` stores uploads, and `static_data` shares collected Django assets with Nginx. `docker compose down` removes containers and networks but retains these volumes.

> **Warning:** `docker compose down -v` permanently deletes the application database and persisted application volumes.

Return to the [documentation index](README.md).
