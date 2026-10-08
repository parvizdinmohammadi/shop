from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel


class Product(BaseModel):
    """محصول فروشگاه."""
    __tablename__ = "products"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(220), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # قیمت با Decimal (نه Float)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    stock: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id"), nullable=False, index=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # روابط
    category: Mapped["Category"] = relationship(
        "Category", back_populates="products"
    )
    cart_items: Mapped[list["CartItem"]] = relationship(
        "CartItem", back_populates="product"
    )
    order_items: Mapped[list["OrderItem"]] = relationship(
        "OrderItem", back_populates="product"
    )