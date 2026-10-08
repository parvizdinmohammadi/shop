from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_token,
    verify_password,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User, UserRole
from app.schemas.token import Token
from app.schemas.user import UserCreate


async def register_user(db: AsyncSession, data: UserCreate) -> User:
    """ثبت‌نام کاربر جدید."""
    # بررسی تکراری نبودن email
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="این ایمیل قبلاً ثبت شده است.",
        )

    user = User(
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def _create_refresh_record(db: AsyncSession, user_id: int, token: str) -> None:
    """refresh token را به‌صورت hash در DB ذخیره می‌کند."""
    expires = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )
    record = RefreshToken(
        user_id=user_id,
        token_hash=hash_token(token),
        expires_at=expires,
        revoked=False,
    )
    db.add(record)


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Token:
    """ورود کاربر و صدور توکن‌ها."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # پیام عمومی (بدون افشای اینکه ایمیل وجود دارد یا نه)
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="ایمیل یا رمز عبور اشتباه است.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None:
        raise invalid
    if not verify_password(password, user.hashed_password):
        raise invalid
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="حساب کاربری غیرفعال است.",
        )

    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    await _create_refresh_record(db, user.id, refresh)
    await db.commit()

    return Token(access_token=access, refresh_token=refresh)


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> Token:
    """
    توکن جدید می‌سازد و توکن قدیمی را revoke می‌کند (rotation).
    """
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="refresh token نامعتبر است.",
    )

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise invalid

    if payload.get("type") != "refresh":
        raise invalid

    user_id = payload.get("sub")
    if user_id is None:
        raise invalid

    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()

    if record is None or record.revoked:
        raise invalid
    if record.expires_at < datetime.now(timezone.utc):
        raise invalid

    # revoke قدیمی
    record.revoked = True

    # بررسی کاربر
    user_result = await db.execute(select(User).where(User.id == int(user_id)))
    user = user_result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise invalid

    access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)
    await _create_refresh_record(db, user.id, new_refresh)
    await db.commit()

    return Token(access_token=access, refresh_token=new_refresh)


async def logout_user(db: AsyncSession, refresh_token: str) -> None:
    """خروج: refresh token را revoke می‌کند."""
    token_hash = hash_token(refresh_token)
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    )
    record = result.scalar_one_or_none()
    if record is not None:
        record.revoked = True
        await db.commit()