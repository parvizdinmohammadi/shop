from fastapi import HTTPException, status

from app.models.user import User, UserRole


def require_role(user: User, *allowed_roles: UserRole) -> None:
    """
    بررسی می‌کند کاربر یکی از نقش‌های مجاز را دارد یا نه.
    در صورت نداشتن، 403 می‌دهد.
    """
    if user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="شما به این بخش دسترسی ندارید.",
        )


def require_admin(user: User) -> None:
    """فقط admin."""
    require_role(user, UserRole.ADMIN)


def require_customer_or_admin(user: User) -> None:
    """customer یا admin."""
    require_role(user, UserRole.CUSTOMER, UserRole.ADMIN)