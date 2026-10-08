from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> User:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="کاربر یافت نشد.",
        )
    return user


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit))
    return list(result.scalars().all())


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.email is not None and data.email != user.email:
        # بررسی یکتا بودن
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="این ایمیل قبلاً ثبت شده است.",
            )
        user.email = data.email

    if data.password is not None:
        user.hashed_password = hash_password(data.password)

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user: User) -> User:
    """غیرفعال‌سازی کاربر (soft)."""
    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user


async def promote_to_admin(db: AsyncSession, user: User) -> User:
    user.role = UserRole.ADMIN
    await db.commit()
    await db.refresh(user)
    return user