import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings


# === Password Hashing ===
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,          # cost factor
)


def hash_password(plain_password: str) -> str:
    """
    پسورد را با bcrypt hash می‌کند.
    - salt خودکار
    - cost factor: 12
    """
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """پسورد را با hash مقایسه می‌کند."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return False


# === JWT ===
def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    """
    یک JWT می‌سازد.
    - subject: معمولاً user id
    - token_type: "access" یا "refresh"
    """
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(subject),
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
        "jti": secrets.token_urlsafe(16),   # شناسه یکتا
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def create_access_token(subject: str | int) -> str:
    """access token با انقضای کوتاه."""
    return _create_token(
        subject=str(subject),
        token_type="access",
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str | int) -> str:
    """refresh token با انقضای بلند."""
    return _create_token(
        subject=str(subject),
        token_type="refresh",
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str) -> dict[str, Any]:
    """
    توکن را decode و اعتبارسنجی می‌کند.
    در صورت خطا JWTError می‌دهد.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
    )


# === Token Hashing (برای refresh در DB) ===
def hash_token(token: str) -> str:
    """
    refresh token را با SHA256 hash می‌کند تا در DB ذخیره شود.
    (خود توکن هرگز در DB ذخیره نمی‌شود)
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()