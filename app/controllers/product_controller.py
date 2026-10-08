from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_admin
from app.database import get_db
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate
from app.services import product_service

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 50,
    search: str | None = Query(default=None, max_length=100),
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    """لیست محصولات با جستجو و فیلتر (public)."""
    return await product_service.list_products(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id,
        only_active=True,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    """دریافت محصول (public)."""
    return await product_service.get_product(db, product_id)


# === Admin ===

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product(
    data: ProductCreate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """ساخت محصول (admin)."""
    return await product_service.create_product(db, data)


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """ویرایش محصول (admin)."""
    return await product_service.update_product(db, product_id, data)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    _: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    """حذف نرم محصول (admin)."""
    await product_service.delete_product(db, product_id)