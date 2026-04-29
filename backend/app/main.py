"""
Decision Intelligence System — FastAPI Application Entry Point

Registers all routes, middleware, and lifecycle events.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("intelligence")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    logger.info("🚀 Starting Decision Intelligence System...")
    logger.info(f"   Environment: {settings.app_env}")
    logger.info(f"   Database: {settings.database_url}")
    logger.info(f"   OpenAI: {'✅ Configured' if settings.has_openai_key else '❌ Not configured'}")

    # Initialize database tables
    await init_db()
    logger.info("   Database: ✅ Tables created")

    yield

    # Shutdown
    logger.info("🛑 Shutting down...")
    await close_db()


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered business intelligence and decision support system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health Check ───────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    from app.schemas.common import HealthResponse
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.app_env,
        database="connected",
        ai_available=settings.has_openai_key,
    )


# ─── Register API Routers ──────────────────────────────────
from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router
from app.api.insights import router as insights_router
from app.api.forecasting import router as forecasting_router
from app.api.segments import router as segments_router
from app.api.ml import router as ml_router
from app.api.recommendations import router as recommendations_router

app.include_router(analytics_router)
app.include_router(chat_router)
app.include_router(insights_router)
app.include_router(forecasting_router)
app.include_router(segments_router)
app.include_router(ml_router)
app.include_router(recommendations_router)


# ─── Database Info Endpoint ─────────────────────────────────
@app.get("/api/db/stats", tags=["Database"])
async def db_stats():
    """Get database table row counts."""
    from sqlalchemy import select, func
    from app.database import async_session
    from app.models import Customer, Order, Product
    from app.models.insight import Insight

    async with async_session() as db:
        customers = (await db.execute(select(func.count(Customer.id)))).scalar() or 0
        orders = (await db.execute(select(func.count(Order.id)))).scalar() or 0
        products = (await db.execute(select(func.count(Product.id)))).scalar() or 0
        insights = (await db.execute(select(func.count(Insight.id)))).scalar() or 0

    return {
        "tables": {
            "customers": customers,
            "orders": orders,
            "products": products,
            "insights": insights,
        },
        "total_records": customers + orders + products + insights,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
