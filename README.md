# apipy

A modern FastAPI backend boilerplate with PostgreSQL, SQLAlchemy 2.0 (Async), and Alembic migrations.

## 🚀 Quick Start

### 1. Initial Setup (Prerequisites)

Before running the project, you must configure your environment variables:

1. **Clone the repository** and enter the directory.
2. **Initialize Environment**:
   Create your `.env` file and generate a secure secret key automatically:
   ```bash
   python3 scripts/generate_secret.py
   ```
3. **Verify Settings**: Open `.env` if you need to change your database credentials (defaults work for Docker).

---

## Option 1: Running with Docker (Recommended)

This is the fastest way to get the project running. It handles the database, application, and migrations automatically.

```bash
docker-compose up --build
```

- **Application**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Database**: PostgreSQL runs on `localhost:5432`

*Note: Migrations run automatically on startup.*

---

## Option 2: Local Development Setup

Use this method if you want to run the application directly on your machine for faster debugging and hot-reloading.

### 1. Start the Database only
You still need a database. The easiest way is to run only the Postgres container from our docker-compose:

```bash
docker-compose up -d db
```

### 2. Set up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
#deactivate
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Application
```bash
PYTHONPATH=src uvicorn apipy.main:app --reload
```

---

## 🧪 Testing & Quality Control

You can run these commands locally (if `.venv` is set up) or directly inside the Docker container.

### Running Tests
```bash
# Locally
pytest

# Inside Docker
docker-compose exec app pytest
```

### Coverage Report
```bash
# Locally
pytest --cov=src

# Inside Docker
docker-compose exec app pytest --cov=src
```

### Linting & Formatting
```bash
# Locally
ruff format .
ruff check . --fix

# Inside Docker
docker-compose exec app ruff format .
docker-compose exec app ruff check . --fix
```

---

## 🛠 Project Structure
- `src/apipy/`: Main application source code.
- `tests/`: Pytest suite.
- `migrations/`: Alembic database migration scripts.
- `docker-compose.yml`: Infrastructure configuration.
