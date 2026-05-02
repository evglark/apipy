import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from apipy.auth.services.cleanup_service import cleanup_loop
from apipy.auth.router import router as auth_router
from apipy.users.router import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    cleanup_task = asyncio.create_task(cleanup_loop())
    try:
        yield
    finally:
        cleanup_task.cancel()
        await asyncio.gather(cleanup_task, return_exceptions=True)


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(users_router)
app.include_router(auth_router)
