from fastapi import FastAPI

from apipy.routers.auth import router as auth_router
from apipy.routers.users import router as users_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(users_router)
app.include_router(auth_router)
