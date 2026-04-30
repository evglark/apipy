from fastapi import FastAPI
from apipy.users.router import router as users_router

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


app.include_router(users_router)
