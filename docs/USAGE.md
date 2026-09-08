# Usage guide

## Initial setup

Open the application and complete the setup screen. The first account is an active Django superuser and can access both the application administration features and Django Admin.

After setup, sign in through `/login`. The setup endpoint stops accepting new administrators while an active superuser exists.

## Basic workflow

1. Configure the company and application defaults under **Settings**.
2. Create users and assign roles and permissions.
3. Add customers, suppliers, categories, units of measure, and products.
4. Record purchases to increase stock and establish payables for credit purchases.
5. Record sales to decrease stock and establish receivables for credit sales.
6. Apply or reverse customer and supplier payments as needed.
7. Review journal entries, accounting periods, dashboards, and reports.

Sales, purchases, collections, and supplier payments create their related accounting records. Reversal operations also update the affected operational and accounting state. Closed accounting periods reject entries dated within the period.

## Configuration

Company settings include identity and contact information, logo, tax rate, currency (`CRC` or `USD`), default interface language, barcode-reader behavior, and a product-code prefix.

The interface supports Spanish and English. It resolves the language from the user's preference, the application default, and the browser language, with Spanish as the fallback.

Business administrators can manage application users, Django groups and permissions, and request audit records. Django Admin at `/admin/` is restricted to active superusers.

## Data storage

The default Docker installation uses SQLite. Its database, generated secret key, and uploaded media live under `/data` in the `faws_data` named volume. Container replacement and `docker compose down` retain the volume.

Do not run `docker compose down -v` unless permanent deletion of the stored application data is intended.

Local backend development uses MySQL by default. Set `DATABASE_ENGINE=sqlite` to use SQLite instead; `SQLITE_PATH`, `FAWS_DATA_DIR`, and `MEDIA_ROOT` can override storage locations.

## Backup and synchronization

FAWS does not provide an in-application backup, restore, cloud synchronization, or replication feature. Back up the complete `/data` volume with infrastructure-level tooling while application writes are stopped, and test restoration separately. A complete standalone backup must include both `faws.sqlite3` and the `media/` directory.

MySQL deployments require a database-native backup plus a copy of uploaded media. Never treat report exports as a system backup.

## Relevant controls

| Shortcut | Action |
| --- | --- |
| `Ctrl+B` | Expand or collapse the navigation menu. |
| `Ctrl+D` | Switch between light and dark themes. |
| `/` | Focus the first available text search field when the current focus is outside an input. |

Barcode input is available in supported inventory and sales forms when barcode-reader behavior is enabled. Pressing `Enter` submits a scanned code.

## Common use cases

- Track stock received through purchases and consumed through sales.
- Manage customer credit, supplier credit, partial payments, and outstanding balances.
- Record balanced manual journals and close accounting periods.
- Review sales, purchases, inventory, receivables, payables, journal, ledger, and trial-balance reports.
- Export selected reports as PDF or XLSX files.
- Review authenticated API activity through the audit log.

## Screenshots

The gallery uses fictional business data and keeps every view as a separate image.

| View | Description |
| --- | --- |
| [Login](screenshots/login.png) | Sign-in screen with a non-sensitive demo account. |
| [Dashboard](screenshots/dashboard.png) | Operational totals and recent activity. |
| [Products](screenshots/products.png) | Searchable product and stock list. |
| [Sales](screenshots/sales.png) | Sales records and transaction status. |
| [Reports](screenshots/reports.png) | Filters and PDF/XLSX export controls. |
| [Company settings](screenshots/configs_company.png) | Company identity and application defaults. |
| [Roles and permissions](screenshots/configs_roles_permissions.png) | Business access-control configuration. |

[Documentation index](index.md) · [Project README](../README.md)
