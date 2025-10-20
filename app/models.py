# app/models.py
from pydantic import BaseModel, Field, constr

Username = constr(strip_whitespace=True, min_length=3, max_length=32, pattern=r"^[A-Za-z0-9_.-]+$")
Password = constr(min_length=6, max_length=128)

from pydantic import BaseModel, constr

class LoginRequest(BaseModel):
    # Лёгкая валидация длины, без жёсткого regex (чтобы payload с "admin'-- " не падал раньше времени)
    username: constr(strip_whitespace=False, min_length=1, max_length=64)
    password: constr(min_length=1, max_length=128)

class Item(BaseModel):
    id: int
    name: constr(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
