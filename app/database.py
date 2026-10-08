from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


# === Engine ===
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,          # فقط در حالت debug کوئری‌ها چاپ می‌شوند
    future=True,
    pool_pre_ping=True,
)


# === Session Factory ===
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


# === Base Class برای مدل‌ها ===
class Base(DeclarativeBase):
    """کلاس پایه برای همه مدل‌ها."""
    pass


# === Dependency برای FastAPI ===
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    یک session دیتابیس می‌دهد و پس از پایان درخواست می‌بندد.
    در صورت خطا، rollback می‌کند.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()