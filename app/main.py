from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import settings
from app.controllers import (
    auth_controller,
    cart_controller,
    category_controller,
    order_controller,
    product_controller,
    user_controller,
)
from app.database import Base, engine


# === Rate Limiter ===
limiter = Limiter(key_func=get_remote_address)


# === Lifespan (startup/shutdown) ===
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        # در production از Alembic استفاده کن، این فقط برای dev است
        if settings.debug:
            await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


# === App ===
app = FastAPI(
    title=settings.app_name,
    description="فروشگاه آنلاین با FastAPI + MVC",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)


# === Rate Limit ===
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Global Exception Handler (بدون افشای جزئیات) ===
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # در debug جزئیات رو نشون بده، در production پیام عمومی
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": "خطای داخلی سرور."},
    )


# === Routers ===
app.include_router(auth_controller.router)
app.include_router(user_controller.router)
app.include_router(category_controller.router)
app.include_router(product_controller.router)
app.include_router(cart_controller.router)
app.include_router(order_controller.router)


# === Health Check ===
@app.get("/", tags=["Health"])
async def root():
    return {"app": settings.app_name, "status": "ok"}


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}