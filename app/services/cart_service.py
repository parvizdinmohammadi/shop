from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart import Cart, CartItem
from app.models.product import Product


async def get_or_create_cart(db: AsyncSession, user_id: int) -> Cart:
    result = await db.execute(
        select(Cart)
        .options(selectinload(Cart.items))
        .where(Cart.user_id == user_id)
    )
    cart = result.scalar_one_or_none()
    if cart is None:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
    return cart


async def get_cart(db: AsyncSession, user_id: int) -> Cart:
    return await get_or_create_cart(db, user_id)


async def add_item(db: AsyncSession, user_id: int, product_id: int, quantity: int) -> Cart:
    # بررسی محصول
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_active.is_(True))
    )
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد یا غیرفعال است.",
        )

    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="موجودی کافی نیست.",
        )

    cart = await get_or_create_cart(db, user_id)

    # آیا این آیتم قبلاً در سبد هست؟
    item_result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    item = item_result.scalar_one_or_none()

    if item is None:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(item)
    else:
        new_qty = item.quantity + quantity
        if product.stock < new_qty:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="موجودی کافی نیست.",
            )
        item.quantity = new_qty

    await db.commit()

    # دوباره با items لود کن
    result = await db.execute(
        select(Cart).options(selectinload(Cart.items)).where(Cart.id == cart.id)
    )
    return result.scalar_one()


async def update_item(
    db: AsyncSession, user_id: int, product_id: int, quantity: int
) -> Cart:
    cart = await get_or_create_cart(db, user_id)

    item_result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    item = item_result.scalar_one_or_none()
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="این محصول در سبد شما نیست.",
        )

    # بررسی موجودی
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None or product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="موجودی کافی نیست.",
        )

    item.quantity = quantity
    await db.commit()

    result = await db.execute(
        select(Cart).options(selectinload(Cart.items)).where(Cart.id == cart.id)
    )
    return result.scalar_one()


async def remove_item(db: AsyncSession, user_id: int, product_id: int) -> Cart:
    cart = await get_or_create_cart(db, user_id)

    item_result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id, CartItem.product_id == product_id
        )
    )
    item = item_result.scalar_one_or_none()
    if item is not None:
        await db.delete(item)
        await db.commit()

    result = await db.execute(
        select(Cart).options(selectinload(Cart.items)).where(Cart.id == cart.id)
    )
    return result.scalar_one()


async def clear_cart(db: AsyncSession, user_id: int) -> None:
    cart = await get_or_create_cart(db, user_id)
    for item in cart.items:
        await db.delete(item)
    await db.commit()