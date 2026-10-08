from decimal import Decimal

from pydantic import BaseModel

from app.models.order import OrderStatus
from app.schemas.base import TimestampSchema


class OrderItemResponse(TimestampSchema):
    product_id: int
    quantity: int
    unit_price: Decimal


class OrderResponse(TimestampSchema):
    user_id: int
    total: Decimal
    status: OrderStatus
    items: list[OrderItemResponse] = []


class CheckoutResponse(BaseModel):
    """پاسخ ثبت سفارش."""
    message: str
    order_id: int