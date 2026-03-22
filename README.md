# apipy

## Run project

```bash
source .venv/bin/activate
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
```
