from pydantic import BaseModel

from app.models.user import UserPublic


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class TokenPayload(BaseModel):
    sub: str | None = None
    exp: int | None = None
