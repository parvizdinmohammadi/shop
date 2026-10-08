from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    """کلاس پایه برای schema هایی که از مدل‌ها ساخته می‌شوند."""
    model_config = ConfigDict(from_attributes=True)


class TimestampSchema(ORMModel):
    """Schema پایه با فیلدهای زمانی."""
    id: int
    created_at: datetime
    updated_at: datetime