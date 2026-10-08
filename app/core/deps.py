from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import require_admin
from app.core.security import decode_token
from app.database import get_db
from app.models.user import User


# === OAuth2 Scheme ===
# توکن از هدر Authorization: Bearer <token> گرفته می‌شود
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    کاربر فعلی را از JWT می‌گیرد.
    - بررسی نوع توکن (access)
    - بررسی وجود کاربر و فعال بودن
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="اعتبارنامه نامعتبر است.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:
        payload = decode_token(token)
    except JWTError:
        raise credentials_exception

    if payload.get("type") != "access":
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال است.",
        )

    return user


async def get_current_admin(
    user: User = Depends(get_current_user),
) -> User:
    """فقط admin."""
    require_admin(user)
    return user


async def get_current_active_user(
    user: User = Depends(get_current_user),
) -> User:
    """کاربر فعال (customer یا admin)."""
    return user