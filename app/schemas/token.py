from pydantic import BaseModel, Field


class Token(BaseModel):
    """پاسخ ورود."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """محتوای JWT."""
    sub: str | None = None
    type: str | None = None       # "access" یا "refresh"
    exp: int | None = None


class RefreshTokenRequest(BaseModel):
    """درخواست refresh."""
    refresh_token: str = Field(..., min_length=10)