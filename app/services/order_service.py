from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.services.cart_service import get_or_create_cart


async def checkout(db: AsyncSession, user_id: int) -> Order:
    """
    ثبت سفارش از سبد خرید.
    - بررسی موجودی
    - کسر از stock
    - پاک کردن سبد
    """
    cart = await get_or_create_cart(db, user_id)

    if not cart.items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="سبد خرید خالی است.",
        )

    total = Decimal("0.00")
    order = Order(user_id=user_id, total=Decimal("0.00"), status=OrderStatus.PENDING)
    db.add(order)
    await db.flush()  # برای گرفتن order.id

    for cart_item in cart.items:
        # قفل کردن محصول برای جلوگیری از race condition
        result = await db.execute(
            select(Product).where(Product.id == cart_item.product_id).with_for_update()
        )
        product = result.scalar_one_or_none()
        if product is None or not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="یکی از محصولات موجود نیست.",
            )
        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"موجودی {product.name} کافی نیست.",
            )

        # کسر از موجودی
        product.stock -= cart_item.quantity

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            unit_price=product.price,
        )
        db.add(order_item)

        total += Decimal(product.price) * cart_item.quantity

    order.total = total

    # پاک کردن سبد
    for cart_item in cart.items:
        await db.delete(cart_item)

    await db.commit()

    # لود کامل سفارش
    result = await db.execute(
        select(Order).options(selectinload(Order.items)).where(Order.id == order.id)
    )
    return result.scalar_one()


async def list_user_orders(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 50
) -> list[Order]:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_order(db: AsyncSession, order_id: int, user_id: int | None = None) -> Order:
    stmt = select(Order).options(selectinload(Order.items)).where(Order.id == order_id)
    if user_id is not None:
        stmt = stmt.where(Order.user_id == user_id)
    result = await db.execute(stmt)
    order = result.scalar_one_or_none()
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="سفارش یافت نشد.",
        )
    return order


async def list_all_orders(
    db: AsyncSession, skip: int = 0, limit: int = 50
) -> list[Order]:
    """برای admin."""
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_order_status(
    db: AsyncSession, order_id: int, new_status: OrderStatus
) -> Order:
    """برای admin."""
    order = await get_order(db, order_id)
    order.status = new_status
    await db.commit()
    await db.refresh(order)
    return order
