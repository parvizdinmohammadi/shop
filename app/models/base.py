from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TimestampMixin:
    """Mixin برای اضافه کردن created_at و updated_at به همه مدل‌ها."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseModel(Base, TimestampMixin):
    """کلاس پایه برای همه مدل‌های پروژه."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)