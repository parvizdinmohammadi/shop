from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    result = await db.execute(select(Category).where(Category.slug == data.slug))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این slug قبلاً استفاده شده است.",
        )

    category = Category(name=data.name, slug=data.slug, is_active=True)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


async def list_categories(
    db: AsyncSession, skip: int = 0, limit: int = 100, only_active: bool = True
) -> list[Category]:
    stmt = select(Category)
    if only_active:
        stmt = stmt.where(Category.is_active.is_(True))
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_category(db: AsyncSession, category_id: int) -> Category:
    result = await db.execute(select(Category).where(Category.id == category_id))
    category = result.scalar_one_or_none()
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="دسته‌بندی یافت نشد.",
        )
    return category


async def update_category(
    db: AsyncSession, category_id: int, data: CategoryUpdate
) -> Category:
    category = await get_category(db, category_id)

    if data.slug is not None and data.slug != category.slug:
        result = await db.execute(select(Category).where(Category.slug == data.slug))
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این slug قبلاً استفاده شده است.",
            )
        category.slug = data.slug

    if data.name is not None:
        category.name = data.name
    if data.is_active is not None:
        category.is_active = data.is_active

    await db.commit()
    await db.refresh(category)
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    """حذف نرم (soft delete)."""
    category = await get_category(db, category_id)
    category.is_active = False
    await db.commit()