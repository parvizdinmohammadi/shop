from decimal import Decimal

from pydantic import BaseModel, Field

from app.schemas.base import TimestampSchema


class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=200)
    slug: str = Field(..., min_length=2, max_length=220)
    description: str | None = None
    price: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    category_id: int = Field(..., gt=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class ProductResponse(TimestampSchema):
    name: str
    slug: str
    description: str | None
    price: Decimal
    stock: int
    category_id: int
    is_active: bool