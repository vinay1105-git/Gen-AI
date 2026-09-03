from pydantic import BaseModel


class TokenData(BaseModel):
    email: str | None = None


class TokenPayload(BaseModel):
    sub: str
    exp: int
