import asyncio
from apipy.database import async_session
from apipy.users.models import User
from apipy.auth.models import Credential
from apipy.auth.security import hash_password


async def seed_data():
    async with async_session() as db:
        # Check if user already exists
        from sqlalchemy import select

        result = await db.execute(select(User).where(User.name == "Alice"))
        if result.scalar_one_or_none():
            print("Alice already exists, skipping seed.")
            return

        print("Seeding initial data...")
        alice = User(name="Alice", email="alice@example.com")
        db.add(alice)
        await db.flush()  # Get ID

        cred = Credential(user_id=alice.id, password_hash=hash_password("password123"))
        db.add(cred)

        await db.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed_data())
