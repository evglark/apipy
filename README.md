# apipy

Учебный FastAPI-проект с CRUD для пользователей и базовой авторизацией.

## Что есть сейчас

- CRUD модуль `/users`.
- Auth модуль `/auth/register` и `/auth/login`.
- Хранилище пока in-memory (для обучения и быстрого старта).

> TODO: перенести хранилище в PostgreSQL, поднятый в Docker (например через `docker compose`).

## Run project

```bash
source .venv/bin/activate
pip install -e .[dev]
uvicorn apipy.main:app --reload
deactivate
```

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
pytest

pytest -q --maxfail=1
```
