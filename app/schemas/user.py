from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole
from app.schemas.base import TimestampSchema


class UserBase(BaseModel):
    email: EmailStr = Field(..., max_length=255)


class UserCreate(UserBase):
    """برای ثبت‌نام."""
    password: str = Field(..., min_length=8, max_length=128)


class UserResponse(TimestampSchema):
    """خروجی - بدون پسورد."""
    email: EmailStr
    role: UserRole
    is_active: bool


class UserUpdate(BaseModel):
    """برای آپدیت کاربر."""
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserLogin(BaseModel):
    """برای ورود."""
    email: EmailStr
    password: str = Field(..., min_length=1)