"""
Analytics API Routes
KPI metrics, revenue trends, top products, cohort analysis, RFM.
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract

from app.database import get_db
from app.models import Customer, Order, Product
from app.schemas.analytics import (
    KPIResponse, KPIMetric,
    RevenueTrendResponse, RevenueTrendPoint,
    TopProductsResponse, TopProductItem,
    SegmentResponse, CustomerSegmentSummary,
    RFMDistribution,
)

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


def _parse_period(period: str) -> tuple[datetime, datetime]:
    """Convert period string to date range."""
    end = datetime.utcnow()
    mapping = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "1y": 365}
    days = mapping.get(period, 30)
    start = end - timedelta(days=days)
    return start, end


@router.get("/kpi", response_model=KPIResponse)
async def get_kpis(
    period: str = Query(default="30d", regex="^(7d|30d|90d|180d|1y)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get key performance indicators with period comparison."""
    start, end = _parse_period(period)
    delta = end - start
    prev_start = start - delta
    prev_end = start

    # Current period metrics
    current_orders = await db.execute(
        select(
            func.count(Order.id).label("count"),
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
            func.coalesce(func.avg(Order.total), 0).label("aov"),
        ).where(and_(Order.order_date >= start, Order.order_date <= end, Order.status == "completed"))
    )
    curr = current_orders.one()

    current_customers = await db.execute(
        select(func.count(func.distinct(Order.customer_id)))
        .where(and_(Order.order_date >= start, Order.order_date <= end, Order.status == "completed"))
    )
    curr_cust = current_customers.scalar() or 0

    # Previous period metrics
    prev_orders = await db.execute(
        select(
            func.count(Order.id).label("count"),
            func.coalesce(func.sum(Order.total), 0).label("revenue"),
            func.coalesce(func.avg(Order.total), 0).label("aov"),
        ).where(and_(Order.order_date >= prev_start, Order.order_date <= prev_end, Order.status == "completed"))
    )
    prev = prev_orders.one()

    prev_customers = await db.execute(
        select(func.count(func.distinct(Order.customer_id)))
        .where(and_(Order.order_date >= prev_start, Order.order_date <= prev_end, Order.status == "completed"))
    )
    prev_cust = prev_customers.scalar() or 0

    def calc_change(current, previous):
        if previous and previous > 0:
            return round(((current - previous) / previous) * 100, 1)
        return None

    def calc_trend(change):
        if change is None:
            return "neutral"
        return "up" if change > 0 else ("down" if change < 0 else "neutral")

    rev_change = calc_change(float(curr.revenue), float(prev.revenue))
    ord_change = calc_change(float(curr.count), float(prev.count))
    cust_change = calc_change(curr_cust, prev_cust)
    aov_change = calc_change(float(curr.aov), float(prev.aov))

    return KPIResponse(
        revenue=KPIMetric(
            label="Revenue", value=round(float(curr.revenue), 2),
            previous_value=round(float(prev.revenue), 2),
            change_pct=rev_change, trend=calc_trend(rev_change),
        ),
        orders=KPIMetric(
            label="Orders", value=float(curr.count),
            previous_value=float(prev.count),
            change_pct=ord_change, trend=calc_trend(ord_change),
        ),
        customers=KPIMetric(
            label="Active Customers", value=float(curr_cust),
            previous_value=float(prev_cust),
            change_pct=cust_change, trend=calc_trend(cust_change),
        ),
        avg_order_value=KPIMetric(
            label="Avg Order Value", value=round(float(curr.aov), 2),
            previous_value=round(float(prev.aov), 2),
            change_pct=aov_change, trend=calc_trend(aov_change),
        ),
        period=period,
        start_date=start.isoformat(),
        end_date=end.isoformat(),
    )


@router.get("/revenue-trend", response_model=RevenueTrendResponse)
async def get_revenue_trend(
    period: str = Query(default="30d"),
    granularity: str = Query(default="daily", regex="^(daily|weekly|monthly)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get revenue trend over time."""
    start, end = _parse_period(period)

    orders = await db.execute(
        select(Order).where(
            and_(Order.order_date >= start, Order.order_date <= end, Order.status == "completed")
        ).order_by(Order.order_date)
    )
    order_list = orders.scalars().all()

    # Group by date
    from collections import defaultdict
    daily = defaultdict(lambda: {"revenue": 0.0, "orders": 0})
    for o in order_list:
        if granularity == "daily":
            key = o.order_date.strftime("%Y-%m-%d")
        elif granularity == "weekly":
            key = o.order_date.strftime("%Y-W%W")
        else:
            key = o.order_date.strftime("%Y-%m")
        daily[key]["revenue"] += o.total
        daily[key]["orders"] += 1

    data = [
        RevenueTrendPoint(
            date=k,
            revenue=round(v["revenue"], 2),
            orders=v["orders"],
            avg_order_value=round(v["revenue"] / v["orders"], 2) if v["orders"] > 0 else 0,
        )
        for k, v in sorted(daily.items())
    ]

    return RevenueTrendResponse(data=data, granularity=granularity, period=period)


@router.get("/top-products", response_model=TopProductsResponse)
async def get_top_products(
    period: str = Query(default="30d"),
    limit: int = Query(default=10, ge=1, le=50),
    sort_by: str = Query(default="revenue", regex="^(revenue|quantity)$"),
    db: AsyncSession = Depends(get_db),
):
    """Get top-performing products."""
    start, end = _parse_period(period)

    query = (
        select(
            Product.id,
            Product.name,
            Product.category,
            Product.margin,
            func.sum(Order.total).label("revenue"),
            func.sum(Order.quantity).label("quantity_sold"),
        )
        .join(Order, Order.product_id == Product.id)
        .where(and_(Order.order_date >= start, Order.order_date <= end, Order.status == "completed"))
        .group_by(Product.id, Product.name, Product.category, Product.margin)
        .order_by(func.sum(Order.total).desc() if sort_by == "revenue" else func.sum(Order.quantity).desc())
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()

    data = [
        TopProductItem(
            id=r.id, name=r.name, category=r.category,
            revenue=round(float(r.revenue), 2),
            quantity_sold=int(r.quantity_sold),
            margin=r.margin,
        )
        for r in rows
    ]

    return TopProductsResponse(data=data, period=period, sort_by=sort_by)


@router.get("/segments", response_model=SegmentResponse)
async def get_segments(db: AsyncSession = Depends(get_db)):
    """Get customer segment summary."""
    total_result = await db.execute(select(func.count(Customer.id)))
    total = total_result.scalar() or 0

    segments_result = await db.execute(
        select(
            Customer.segment,
            func.count(Customer.id).label("count"),
            func.avg(Customer.lifetime_value).label("avg_ltv"),
            func.avg(Customer.total_orders).label("avg_orders"),
            func.avg(Customer.churn_probability).label("avg_churn"),
        )
        .where(Customer.segment.isnot(None))
        .group_by(Customer.segment)
    )
    rows = segments_result.all()

    segments = [
        CustomerSegmentSummary(
            segment=r.segment or "Unknown",
            count=r.count,
            percentage=round((r.count / total) * 100, 1) if total > 0 else 0,
            avg_lifetime_value=round(float(r.avg_ltv or 0), 2),
            avg_order_count=round(float(r.avg_orders or 0), 1),
            avg_churn_probability=round(float(r.avg_churn or 0), 3) if r.avg_churn else None,
        )
        for r in rows
    ]

    return SegmentResponse(segments=segments, total_customers=total)


@router.get("/rfm")
async def get_rfm_distribution(db: AsyncSession = Depends(get_db)):
    """Get RFM score distribution."""
    customers = await db.execute(
        select(Customer.rfm_recency, Customer.rfm_frequency, Customer.rfm_monetary)
        .where(Customer.rfm_recency.isnot(None))
    )
    rows = customers.all()

    if not rows:
        return {"recency_bins": [], "frequency_bins": [], "monetary_bins": []}

    import numpy as np
    recency = [r[0] for r in rows if r[0] is not None]
    frequency = [r[1] for r in rows if r[1] is not None]
    monetary = [r[2] for r in rows if r[2] is not None]

    def make_bins(values, name, n_bins=5):
        if not values:
            return []
        arr = np.array(values)
        bins = np.linspace(arr.min(), arr.max(), n_bins + 1)
        counts, _ = np.histogram(arr, bins=bins)
        return [
            {"bin": f"{bins[i]:.0f}-{bins[i+1]:.0f}", "count": int(counts[i])}
            for i in range(len(counts))
        ]

    return {
        "recency_bins": make_bins(recency, "recency"),
        "frequency_bins": make_bins(frequency, "frequency"),
        "monetary_bins": make_bins(monetary, "monetary"),
    }
