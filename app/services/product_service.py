from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.category_service import get_category


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    # بررسی وجود دسته‌بندی
    await get_category(db, data.category_id)

    # بررسی slug
    result = await db.execute(select(Product).where(Product.slug == data.slug))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این slug قبلاً استفاده شده است.",
        )

    product = Product(
        name=data.name,
        slug=data.slug,
        description=data.description,
        price=data.price,
        stock=data.stock,
        category_id=data.category_id,
        is_active=True,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def list_products(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    search: str | None = None,
    category_id: int | None = None,
    only_active: bool = True,
) -> list[Product]:
    stmt = select(Product)
    if only_active:
        stmt = stmt.where(Product.is_active.is_(True))
    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Product.name.ilike(pattern), Product.description.ilike(pattern))
        )
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_product(db: AsyncSession, product_id: int) -> Product:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="محصول یافت نشد.",
        )
    return product


async def update_product(
    db: AsyncSession, product_id: int, data: ProductUpdate
) -> Product:
    product = await get_product(db, product_id)

    if data.category_id is not None:
        await get_category(db, data.category_id)
        product.category_id = data.category_id

    if data.name is not None:
        product.name = data.name
    if data.description is not None:
        product.description = data.description
    if data.price is not None:
        product.price = data.price
    if data.stock is not None:
        product.stock = data.stock
    if data.is_active is not None:
        product.is_active = data.is_active

    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(db: AsyncSession, product_id: int) -> None:
    """soft delete."""
    product = await get_product(db, product_id)
    product.is_active = False
    await db.commit()