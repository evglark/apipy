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
pip install -e .[dev]
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
pip install -e .[dev]
```

## Format code

```bash
black .
ruff check . --fix

black --check .
ruff check .
```

## Run tests

```bash
PYTHONPATH=src pytest

PYTHONPATH=src pytest -q --maxfail=1
```
