# Local development and validation

## Requirements

- Python 3.13
- Node.js 24, or a compatible version declared in `frontend/package.json`
- npm
- MySQL

## Backend

```bash
cp .env.example .env
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r requirements.txt
python backend/manage.py migrate
python backend/manage.py runserver
```

## Frontend

In another terminal:

```bash
cd frontend
npm ci
npm run dev
```

## Validation

Run the same core checks used by Continuous Integration:

```bash
DJANGO_DEBUG=true DJANGO_USE_SQLITE_TESTS=true python backend/manage.py check
DJANGO_DEBUG=true DJANGO_USE_SQLITE_TESTS=true python backend/manage.py test
cd frontend
npm run lint:check
npm run build
```

The [GitHub Actions workflow](../.github/workflows/ci.yml) runs these checks on pull requests and pushes to `demo`, builds the backend and frontend images independently, and performs a clean-install Compose smoke test. Successful `demo` builds deploy the separately configured portfolio environment through the self-hosted earth-2 runner after every validation job succeeds.

Return to the [documentation index](README.md).
