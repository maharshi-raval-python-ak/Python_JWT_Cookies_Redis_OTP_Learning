from pydantic import BaseModel
from typing import TypeVar, List
from app.models.auth_user import Role

T = TypeVar("T")

class UserData(BaseModel):
    name: str
    password: str
    roles: List[Role]