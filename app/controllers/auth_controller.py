from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["Auth"])

limiter = Limiter(key_func=get_remote_address)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("100/minute")
async def register(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """ثبت‌نام کاربر جدید."""
    user = await auth_service.register_user(db, data)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("100/minute")
async def login(
    request: Request,
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """ورود با email و password."""
    return await auth_service.authenticate_user(db, data.email, data.password)


@router.post("/refresh", response_model=Token)
async def refresh(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """گرفتن توکن جدید با refresh token."""
    return await auth_service.refresh_tokens(db, data.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """خروج: refresh token را revoke می‌کند."""
    await auth_service.logout_user(db, data.refresh_token)


@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """اطلاعات کاربر فعلی."""
    return current_user