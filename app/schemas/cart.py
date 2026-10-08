from pydantic import BaseModel, Field

from app.schemas.base import TimestampSchema


class CartItemBase(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=1000)


class CartItemCreate(CartItemBase):
    pass


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0, le=1000)


class CartItemResponse(TimestampSchema):
    product_id: int
    quantity: int


class CartResponse(TimestampSchema):
    user_id: int
    items: list[CartItemResponse] = []