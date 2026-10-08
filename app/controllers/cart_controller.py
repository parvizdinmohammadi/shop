from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from app.services import cart_service

router = APIRouter(prefix="/api/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """سبد خرید من."""
    return await cart_service.get_cart(db, current_user.id)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    data: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """افزودن محصول به سبد."""
    return await cart_service.add_item(
        db, current_user.id, data.product_id, data.quantity
    )


@router.patch("/items/{product_id}", response_model=CartResponse)
async def update_item(
    product_id: int,
    data: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """تغییر تعداد یک محصول در سبد."""
    return await cart_service.update_item(
        db, current_user.id, product_id, data.quantity
    )


@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """حذف محصول از سبد."""
    return await cart_service.remove_item(db, current_user.id, product_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """خالی کردن سبد."""
    await cart_service.clear_cart(db, current_user.id)