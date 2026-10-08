from pydantic import BaseModel, Field

from app.schemas.base import TimestampSchema


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    slug: str = Field(..., min_length=2, max_length=120)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    slug: str | None = Field(default=None, min_length=2, max_length=120)
    is_active: bool | None = None


class CategoryResponse(TimestampSchema):
    name: str
    slug: str
    is_active: bool