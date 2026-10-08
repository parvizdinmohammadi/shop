from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin, get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def read_me(current_user: User = Depends(get_current_user)):
    """پروفایل خودم."""
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ویرایش پروفایل خودم."""
    return await user_service.update_user(db, current_user, data)


# === Admin endpoints ===

@router.get("", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 50,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """لیست کاربران (admin)."""
    return await user_service.list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """دریافت کاربر (admin)."""
    return await user_service.get_user_by_id(db, user_id)


@router.post("/{user_id}/promote", response_model=UserResponse)
async def promote_user(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """ارتقا به admin."""
    user = await user_service.get_user_by_id(db, user_id)
    return await user_service.promote_to_admin(db, user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """غیرفعال‌سازی کاربر (admin)."""
    user = await user_service.get_user_by_id(db, user_id)
    await user_service.deactivate_user(db, user)