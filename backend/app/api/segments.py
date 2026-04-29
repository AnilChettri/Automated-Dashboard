"""
Segments API Routes
Customer segmentation endpoints.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models import Customer

router = APIRouter(prefix="/api/segments", tags=["Segments"])


@router.get("/{segment_name}/customers")
async def get_segment_customers(
    segment_name: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get customers in a specific segment."""
    offset = (page - 1) * page_size

    # Count total
    count_result = await db.execute(
        select(func.count(Customer.id)).where(Customer.segment == segment_name)
    )
    total = count_result.scalar() or 0

    # Get page
    result = await db.execute(
        select(Customer)
        .where(Customer.segment == segment_name)
        .order_by(Customer.lifetime_value.desc())
        .offset(offset)
        .limit(page_size)
    )
    customers = result.scalars().all()

    return {
        "segment": segment_name,
        "total": total,
        "page": page,
        "page_size": page_size,
        "customers": [
            {
                "id": c.id,
                "name": c.name,
                "email": c.email,
                "city": c.city,
                "lifetime_value": c.lifetime_value,
                "total_orders": c.total_orders,
                "avg_order_value": c.avg_order_value,
                "churn_probability": c.churn_probability,
                "last_purchase_date": c.last_purchase_date.isoformat() if c.last_purchase_date else None,
            }
            for c in customers
        ],
    }
