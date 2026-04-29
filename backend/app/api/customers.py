from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from app.database import get_db
from app.models import Customer
from app.schemas.customers import CustomerListResponse, CustomerListItem

router = APIRouter(prefix="/api/customers", tags=["Customers"])

@router.get("", response_model=CustomerListResponse)
async def get_customers(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    segment: str | None = Query(default=None),
    sort_by: str = Query(default="ltv", regex="^(ltv|orders|churn|name)$"),
    db: AsyncSession = Depends(get_db)
):
    """List customers with pagination and sorting."""
    offset = (page - 1) * page_size
    
    query = select(Customer)
    if segment:
        query = query.where(Customer.segment == segment)
        
    # Sorting
    if sort_by == "ltv":
        query = query.order_by(desc(Customer.lifetime_value))
    elif sort_by == "orders":
        query = query.order_by(desc(Customer.total_orders))
    elif sort_by == "churn":
        query = query.order_by(desc(Customer.churn_probability))
    elif sort_by == "name":
        query = query.order_by(Customer.name)
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0
    
    # Get page
    result = await db.execute(query.offset(offset).limit(page_size))
    customers = result.scalars().all()
    
    return CustomerListResponse(
        customers=[
            CustomerListItem(
                id=c.id,
                name=c.name,
                email=c.email,
                city=c.city,
                country=c.country,
                segment=c.segment,
                lifetime_value=c.lifetime_value,
                total_orders=c.total_orders,
                avg_order_value=c.avg_order_value,
                churn_probability=c.churn_probability,
                last_purchase_date=c.last_purchase_date
            ) for c in customers
        ],
        total=total,
        page=page,
        page_size=page_size
    )

@router.get("/{customer_id}")
async def get_customer_detail(customer_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed customer profile."""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    if not customer:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
