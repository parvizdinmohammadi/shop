from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.database import get_db
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.services import category_service

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("", response_model=list[CategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    """لیست دسته‌بندی‌های فعال (public)."""
    return await category_service.list_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت یک دسته‌بندی (public)."""
    return await category_service.get_category(db, category_id)


# === Admin ===

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """ساخت دسته‌بندی (admin)."""
    return await category_service.create_category(db, data)


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """ویرایش دسته‌بندی (admin)."""
    return await category_service.update_category(db, category_id, data)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """حذف نرم دسته‌بندی (admin)."""
    await category_service.delete_category(db, category_id)