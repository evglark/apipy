from pydantic import BaseModel


class User(BaseModel):
    id: int
    name: str


class UserCreate(BaseModel):
    name: str
