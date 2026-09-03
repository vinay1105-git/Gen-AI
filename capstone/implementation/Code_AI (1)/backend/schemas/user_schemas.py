from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Annotated

NameStr = Annotated[str, Field(min_length=2, max_length=128)]
PasswordStr = Annotated[str, Field(min_length=8)]


class UserCreate(BaseModel):
    email: EmailStr
    name: NameStr
    password: PasswordStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)