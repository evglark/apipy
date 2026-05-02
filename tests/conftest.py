import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text, pool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from apipy.database import get_db
from apipy.main import app
from os import getenv

DATABASE_URL = getenv(
    "DATABASE_URL", "postgresql+asyncpg://apipy:apipy@localhost:5432/apipy"
)


@pytest.fixture(scope="session")
def engine():
    # Use NullPool for tests to ensure connections are not reused between tasks unexpectedly
    return create_async_engine(DATABASE_URL, poolclass=pool.NullPool)


@pytest.fixture(autouse=True)
async def clear_db(engine):
    async with engine.begin() as conn:
        tables = [
            "ip_rate_limit_attempts",
            "magic_tokens",
            "email_verification_tokens",
            "security_events",
            "login_attempts",
            "token_blacklist",
            "refresh_tokens",
            "credentials",
            "users",
        ]
        # Single TRUNCATE call for all tables is more efficient and avoids multiple operations
        tables_str = ", ".join(tables)
        await conn.execute(text(f"TRUNCATE TABLE {tables_str} CASCADE"))

        # Seed basic roles and permissions required for authorization tests
        await conn.execute(
            text(
                "INSERT INTO roles (name) VALUES ('user'), ('admin') ON CONFLICT DO NOTHING"
            )
        )
        await conn.execute(
            text(
                "INSERT INTO permissions (name) VALUES ('create_user'), ('delete_user') ON CONFLICT DO NOTHING"
            )
        )

        # Link admin role to permissions
        await conn.execute(
            text("""
            INSERT INTO role_permissions (role, permission_id) 
            SELECT 'admin', id FROM permissions WHERE name IN ('create_user', 'delete_user')
            ON CONFLICT DO NOTHING
        """)
        )
    yield


@pytest.fixture
async def db_session(engine):
    Session = async_sessionmaker(engine, expire_on_commit=False)
    async with Session() as session:
        yield session
        await session.close()


@pytest.fixture
async def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
