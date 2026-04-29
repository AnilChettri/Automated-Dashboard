from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import Product, Order
from app.schemas.products import ProductListResponse, ProductListItem
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/products", tags=["Products"])

@router.get("", response_model=ProductListResponse)
async def get_products(db: AsyncSession = Depends(get_db)):
    """List all products with 30-day performance metrics."""
    # Last 30 days revenue/units per product
    start_date = datetime.utcnow() - timedelta(days=30)
    
    perf_query = (
        select(
            Order.product_id,
            func.sum(Order.total).label("revenue"),
            func.sum(Order.quantity).label("units")
        )
        .where(Order.order_date >= start_date)
        .group_by(Order.product_id)
    )
    perf_res = await db.execute(perf_query)
    performance = {r.product_id: (float(r.revenue), int(r.units)) for r in perf_res.all()}
    
    # Get all products
    result = await db.execute(select(Product).order_by(Product.name))
    products = result.scalars().all()
    
    return ProductListResponse(
        products=[
            ProductListItem(
                id=p.id,
                name=p.name,
                category=p.category,
                price=p.price,
                cost=p.cost,
                margin=p.margin,
                stock_quantity=p.stock_quantity,
                revenue_30d=performance.get(p.id, (0.0, 0))[0],
                units_sold_30d=performance.get(p.id, (0.0, 0))[1]
            ) for p in products
        ],
        total=len(products)
    )
