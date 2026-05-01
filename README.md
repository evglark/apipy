# apipy

## Что есть сейчас

- CRUD module `/users`.
- Auth module `/auth` (register/login/refresh/logout/magic-link/me).
- Docker setup with two containers:
  - `app` — FastAPI/uvicorn.
  - `db` — PostgreSQL 16.

## Run project locally (venv)

```bash
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn apipy.main:app --reload
deactivate
```

## Run with Docker (app + postgres in separate containers)

```bash
docker compose up --build
```

Application: `http://localhost:8000`
PostgreSQL: `localhost:5432` (`apipy/apipy`, db `apipy`)

## Install dependencies

```bash
pip install -e ".[dev]"
```

## Check style

```bash
ruff format --check .
ruff check .
```

## Format and Lint code

```bash
ruff format .
ruff check . --fix
```

## Run tests

```bash
PYTHONPATH=src pytest
PYTHONPATH=src pytest -q --maxfail=1
```

## Environment setup (English)

1. Copy the example file:

```bash
cp .env.example .env
```

2. Open `.env` and set real secrets (never commit `.env`):
   - `API_SECRET_KEY` for HS algorithms, or
   - `JWT_PRIVATE_KEY` + `JWT_PUBLIC_KEY` for RS/ES algorithms.

3. Keep timing/security variables configured as needed:
   - `ACCESS_TOKEN_EXPIRE_SECONDS`
   - `REFRESH_TOKEN_EXPIRE_SECONDS`
   - `MAX_LOGIN_ATTEMPTS`
   - `LOGIN_BLOCK_SECONDS`
   - `IP_RATE_LIMIT_ATTEMPTS`
   - `IP_RATE_LIMIT_WINDOW_SECONDS`

4. Run app with env loaded (Docker Compose or local shell).
