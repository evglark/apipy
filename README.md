# apipy

## Run project

```bash
source .venv/bin/activate
uvicorn main:app --reload
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Format code

```bash
black .
ruff check . --fix
```

## Run tests

```bash
pytest
```
