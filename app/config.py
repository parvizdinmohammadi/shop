from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    تنظیمات برنامه - همه از .env خوانده می‌شوند.
    هیچ مقدار حساسی در کد hardcode نمی‌شود.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # === App ===
    app_name: str = Field(default="Shop", alias="APP_NAME")
    debug: bool = Field(default=False, alias="DEBUG")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # === Security ===
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = Field(default="HS256", alias="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_token_expire_days: int = Field(default=7, alias="REFRESH_TOKEN_EXPIRE_DAYS")

    # === Database ===
    database_url: str = Field(..., alias="DATABASE_URL")

    # === CORS ===
    allowed_origins: str = Field(default="", alias="ALLOWED_ORIGINS")

    # === Initial Admin (اختیاری) ===
    admin_email: str | None = Field(default=None, alias="ADMIN_EMAIL")
    admin_password: str | None = Field(default=None, alias="ADMIN_PASSWORD")

    @property
    def allowed_origins_list(self) -> List[str]:
        """ALLOWED_ORIGINS را به لیست تبدیل می‌کند."""
        if not self.allowed_origins:
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v or v.startswith("CHANGE_ME"):
            raise ValueError(
                "SECRET_KEY باید در .env مقداردهی شود (نه مقدار پیش‌فرض)."
            )
        if len(v) < 32:
            raise ValueError("SECRET_KEY باید حداقل ۳۲ کاراکتر باشد.")
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL الزامی است.")
        return v


@lru_cache
def get_settings() -> Settings:
    """تنظیمات را یک بار می‌سازد و کش می‌کند."""
    return Settings()


settings = get_settings()