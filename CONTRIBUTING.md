# Contributing

Contributions should be focused, reproducible, and consistent with the existing Django and Vue architecture.

## Report an issue

Search existing issues before opening a new one. Include:

- A concise description of the problem
- Steps to reproduce it
- Expected and actual behavior
- Relevant browser, operating system, and deployment details
- Sanitized logs or screenshots when useful

Do not include credentials, customer data, database exports, or other sensitive information.

## Propose a feature

Open an issue describing the use case, affected workflow, expected behavior, and any compatibility or data-migration concerns. Keep proposals within the project's financial, inventory, and accounting scope.

## Development requirements

- Python 3.13
- Node.js `^22.18.0` or `>=24.12.0`
- npm
- MySQL, or SQLite for local development

Docker Engine and Docker Compose are required only for the container workflow.

## Install dependencies

From the repository root:

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r requirements.txt
cd frontend
npm ci
```

## Run the project

Run the backend with SQLite from the repository root:

```bash
source backend/.venv/bin/activate
DATABASE_ENGINE=sqlite DJANGO_DEBUG=true python backend/manage.py migrate
DATABASE_ENGINE=sqlite DJANGO_DEBUG=true python backend/manage.py runserver
```

In another terminal:

```bash
cd frontend
npm run dev
```

The frontend development server uses `http://127.0.0.1:8000/api/` when `VITE_API_URL` is not set.

## Validate changes

```bash
DJANGO_DEBUG=true DJANGO_USE_SQLITE_TESTS=true python backend/manage.py check
DJANGO_DEBUG=true DJANGO_USE_SQLITE_TESTS=true python backend/manage.py test
cd frontend
npm run test
npm run lint:check
npm run build
```

## Pull request expectations

- Explain the problem and the chosen solution.
- Keep unrelated changes out of the pull request.
- Add or update tests for changed behavior.
- Update documentation when commands, configuration, or user workflows change.
- Include sanitized, independent screenshots for visible UI changes.
- Confirm that the validation commands pass.
- Call out migrations, compatibility risks, and operational follow-up explicitly.

[Project README](README.md) · [Documentation index](docs/index.md)
