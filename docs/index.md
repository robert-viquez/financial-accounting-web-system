# Financial Accounting Web System documentation

FAWS combines operational records and double-entry accounting in a browser-based application. This documentation covers installation, day-to-day use, architecture, and contribution workflows.

## Guides

- [Usage guide](USAGE.md): setup, configuration, workflows, storage, and backup considerations
- [Technical overview](technical-overview.md): stack, architecture, persistence, integrations, and repository layout
- [Contributing](../CONTRIBUTING.md): development setup and pull request expectations

## Quick installation

Requirements: Docker Engine and Docker Compose.

```bash
git clone https://github.com/robert-viquez/financial-accounting-web-system.git
cd financial-accounting-web-system
docker compose up -d
```

Open <http://localhost:8080>. A new installation redirects to the one-time setup screen, where the first active superuser is created.

Check the application and its database-aware health endpoint:

```bash
docker compose ps
curl --fail http://localhost:8080/api/health/
```

The Compose stack uses the published `latest` image by default and can build the same standalone image from the repository. To force a local rebuild, run `docker compose up -d --build`.

[Back to the project README](../README.md)
