from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin, get_current_user
from app.database import get_db
from app.models.order import OrderStatus
from app.models.user import User
from app.schemas.order import CheckoutResponse, OrderResponse
from app.services import order_service

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """ثبت سفارش از سبد."""
    order = await order_service.checkout(db, current_user.id)
    return CheckoutResponse(message="سفارش با موفقیت ثبت شد.", order_id=order.id)


@router.get("/me", response_model=list[OrderResponse])
async def my_orders(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """سفارش‌های من."""
    return await order_service.list_user_orders(
        db, current_user.id, skip=skip, limit=limit
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_my_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """جزئیات سفارش من."""
    return await order_service.get_order(db, order_id, user_id=current_user.id)


# === Admin ===

@router.get("", response_model=list[OrderResponse])
async def list_all_orders(
    skip: int = 0,
    limit: int = 50,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """همه سفارش‌ها (admin)."""
    return await order_service.list_all_orders(db, skip=skip, limit=limit)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_status(
    order_id: int,
    new_status: OrderStatus,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """تغییر وضعیت سفارش (admin)."""
    return await order_service.update_order_status(db, order_id, new_status)