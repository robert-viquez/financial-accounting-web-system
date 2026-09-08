# Portfolio demo deployment

This is a small, resettable portfolio-demo topology, not a production deployment blueprint. It keeps MySQL and Gunicorn on the internal Compose network and publishes only Nginx on the host loopback interface for an externally managed Cloudflare Tunnel.

```text
Browser → Cloudflare → Cloudflare Tunnel → 127.0.0.1:5173
                                             ↓
                                      Nginx / Vue SPA
                                             ↓ internal Docker network
                                         Gunicorn → MySQL
```

The repository contains no tunnel credentials. In Cloudflare, configure the public hostname you control (for example `faws.example.net`) with the HTTP origin `http://127.0.0.1:5173`. DNS is normally created when that public hostname is attached to the tunnel.

## Configure and start

Copy `.env.example` to the ignored `.env`, replace every placeholder, and use settings like these for the demo:

```dotenv
DJANGO_DEBUG=false
DJANGO_SECRET_KEY=generate-a-long-unique-value
DJANGO_ALLOWED_HOSTS=faws.example.net,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://faws.example.net
CSRF_TRUSTED_ORIGINS=https://faws.example.net
DJANGO_TRUST_X_FORWARDED_PROTO=true
DJANGO_SECURE_SSL_REDIRECT=false
DJANGO_SECURE_HSTS_SECONDS=0

MYSQL_DATABASE=faws_demo
MYSQL_USER=accounting_app
MYSQL_PASSWORD=choose-a-unique-database-password
MYSQL_ROOT_PASSWORD=choose-a-different-root-password

FRONTEND_BIND_ADDRESS=127.0.0.1
FRONTEND_PORT=5173
VITE_DEMO_MODE=true
VITE_DEMO_USERNAME=demo
VITE_DEMO_PASSWORD=<public-demo-password>
ALLOW_DEMO_SEED=true
DEMO_USERNAME=demo
DEMO_PASSWORD=<public-demo-password>
```

All three `VITE_DEMO_*` variables shown above are required for the public demo. They are compiled into the browser bundle when the frontend image is built, so their values are client-visible and must be treated as public, never as secrets. Use them only for the non-privileged `demo` account, and set `VITE_DEMO_PASSWORD` to the same value as the backend `DEMO_PASSWORD` so the preloaded form can authenticate normally. Never reuse this password for MySQL, Django superusers, Cloudflare, or any infrastructure account.

Demo login prefill is enabled only when `VITE_DEMO_MODE` is exactly `true`. With the default `false` value, the fields remain empty and no demo notice is rendered. Changing a `VITE_*` value requires rebuilding the frontend image; `docker compose up` alone does not update values already compiled into the bundle.

`DJANGO_TRUST_X_FORWARDED_PROTO=true` makes Django trust the sanitized `X-Forwarded-Proto: https` passed through Nginx. Nginx accepts only the exact incoming value `https`; otherwise it uses its own scheme. Loopback binding prevents untrusted LAN clients from reaching that proxy directly. HTTPS redirection is left off because Cloudflare already redirects/terminates HTTPS and the container health check uses HTTP. Enable HSTS only after validating HTTPS for the chosen hostname.

Start and verify:

```bash
docker compose build
docker compose up -d
docker compose ps
curl --fail http://127.0.0.1:5173/api/health/
```

## Seed and reset

Seeding is explicit and never runs for a clean installation:

```bash
docker compose exec backend python manage.py seed_demo --reset --seed 20260828
```

This creates a deterministic, interconnected, entirely fictional ByteForge Technologies dataset and a normal application user from `DEMO_USERNAME` and `DEMO_PASSWORD`. The user belongs to the existing `Operaciones` application group but is neither Django staff nor a superuser (`is_staff=False`, `is_superuser=False`).

The host reset wrapper applies migrations, resets/reseeds through the Django command, and retries the externally facing Nginx health endpoint. It does not delete volumes or uploaded media, and `flock` rejects overlapping runs:

```bash
chmod +x scripts/reset-demo.sh
./scripts/reset-demo.sh
```

The public portfolio server runs this reset every six hours. An equivalent host cron entry is:

```cron
0 */6 * * * /absolute/path/to/financial-accounting-web-system/scripts/reset-demo.sh >> /var/log/faws-demo-reset.log 2>&1
```

The cron user needs permission to run Docker and write the selected log. Test the script manually as that user first. The committed script never prints the demo password.

## Updating

```bash
git pull
docker compose build
docker compose up -d
docker compose ps
curl --fail http://127.0.0.1:5173/api/health/
./scripts/reset-demo.sh
```

Back up the MySQL named volume before an update if its current state matters. The scheduled reset intentionally destroys application records in the dedicated demo database; never point it at valuable data. The `mysql_data`, `media_data`, and `static_data` volumes persist across ordinary container recreation. Uploaded media is preserved by resets and must be reviewed or cleaned deliberately if the public demo permits uploads.

## Clean installations and troubleshooting

For a clean installation, keep `VITE_DEMO_MODE=false` and `ALLOW_DEMO_SEED=false`, leave all frontend and backend demo credential values blank, and never run `seed_demo`. Migrations alone produce an empty application ready for configuration, while the login form remains unchanged with empty fields and no demo notice.

- If Compose rejects configuration, confirm all required database and secret values exist in `.env`.
- If Django reports `DisallowedHost`, add the exact public hostname to `DJANGO_ALLOWED_HOSTS`.
- If browser requests fail, use the exact HTTPS origin (scheme and hostname, without a path) in CORS and CSRF settings.
- If health fails, inspect `docker compose ps` and `docker compose logs backend frontend db`.
- If reset reports another run, inspect the process before removing the lock file; the lock is released automatically when the process exits.
- Keep `.env`, database exports, customer data, and Cloudflare tunnel tokens outside version control.

This design is intentionally modest: it has no embedded `cloudflared`, scheduler, centralized secrets service, automated backups, or high-availability guarantees.
