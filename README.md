<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="FAWS operational dashboard">
</p>

# Financial Accounting Web System (FAWS)

**Django · Vue · MySQL · Docker Compose · GitHub Actions · Cloudflare Tunnel**

[![CI](https://github.com/robert-viquez/financial-accounting-web-system/actions/workflows/ci.yml/badge.svg)](https://github.com/robert-viquez/financial-accounting-web-system/actions/workflows/ci.yml)

FAWS is a full-stack financial and accounting system that connects sales, purchases, inventory, receivables, payables, and double-entry accounting. It is also a deployed systems project: its public portfolio demo runs as a containerized application behind Cloudflare Tunnel, with health checks, persistent storage, and Continuous Integration.

The interface supports Spanish and English. Language is resolved from the user preference, application default, and browser language, with Spanish as the final fallback.

**[Open live demo](https://faws.robertviquez.com)** · **[Documentation](docs/README.md)** · **[Product tour](docs/product-tour.md)** · **[Architecture](docs/architecture.md)**

The demo uses a fictional **ByteForge Technologies** dataset. Credentials are prefilled on the login screen and authenticate through the normal application flow. Data is restored automatically every six hours; do not enter personal, confidential, or production information.

## What FAWS does

- Manages customers, suppliers, products, categories, barcodes, and stock movements.
- Records cash and credit sales and purchases with inventory validation and reversal flows.
- Tracks accounts receivable, accounts payable, and their payments.
- Produces double-entry journal records, accounting periods, and financial reports.
- Exports selected operational and accounting reports to PDF and XLSX.
- Provides JWT authentication, Django-based role access control, and an audit trail.
- Exposes an OpenAPI schema, Swagger UI, and a database-aware health endpoint.

## Quick start

Requirements: Git, Docker Engine, and the Docker Compose plugin.

```bash
git clone https://github.com/robert-viquez/financial-accounting-web-system.git
cd financial-accounting-web-system
cp .env.example .env
# Replace CHANGE_ME values and add the server address to DJANGO_ALLOWED_HOSTS.
docker compose up -d --build
```

Open `http://SERVER_IP:5173` (or the configured `FRONTEND_PORT`). A fresh database displays the one-time administrator setup screen.

See the [installation guide](docs/installation.md) for configuration, verification, upgrades, and persistent storage details.

## Documentation

- [Documentation index](docs/README.md)
- [Product tour](docs/product-tour.md)
- [Architecture and security](docs/architecture.md)
- [Installation and operation](docs/installation.md)
- [Local development and validation](docs/development.md)
- [Portfolio demo deployment](docs/deployment-demo.md)

## Repository map

```text
.
├── backend/               # Django project and business modules
├── frontend/              # Vue/Vite SPA and production Nginx config
├── docker/                # Container entrypoint
├── docs/                  # Project, operations, and demo documentation
├── scripts/               # Demo reset tooling
├── .github/workflows/     # Continuous integration
├── compose.yml            # Portable FAWS application stack
└── compose.demo.yml       # Portfolio demo proxy-network override
```

FAWS began as a university graduation project for a small-business accounting use case and continues as a portfolio project focused on full-stack engineering, systems administration, containerization, and cloud connectivity.

## License

See [LICENSE](LICENSE).
