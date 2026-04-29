"""
Analytics Pydantic schemas for KPI and metrics endpoints.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class KPIMetric(BaseModel):
    label: str
    value: float
    previous_value: float | None = None
    change_pct: float | None = None
    trend: str = "neutral"  # up, down, neutral


class KPIResponse(BaseModel):
    revenue: KPIMetric
    orders: KPIMetric
    customers: KPIMetric
    avg_order_value: KPIMetric
    period: str
    start_date: str
    end_date: str


class RevenueTrendPoint(BaseModel):
    date: str
    revenue: float
    orders: int
    avg_order_value: float


class RevenueTrendResponse(BaseModel):
    data: list[RevenueTrendPoint]
    granularity: str  # daily, weekly, monthly
    period: str


class TopProductItem(BaseModel):
    id: int
    name: str
    category: str
    revenue: float
    quantity_sold: int
    margin: float | None = None


class TopProductsResponse(BaseModel):
    data: list[TopProductItem]
    period: str
    sort_by: str


class CustomerSegmentSummary(BaseModel):
    segment: str
    count: int
    percentage: float
    avg_lifetime_value: float
    avg_order_count: float
    avg_churn_probability: float | None = None


class SegmentResponse(BaseModel):
    segments: list[CustomerSegmentSummary]
    total_customers: int


class CohortRow(BaseModel):
    cohort: str  # e.g., "2025-01"
    periods: list[float | None]  # retention rates per period


class CohortResponse(BaseModel):
    cohorts: list[CohortRow]
    period_labels: list[str]


class RFMDistribution(BaseModel):
    recency_bins: list[dict]
    frequency_bins: list[dict]
    monetary_bins: list[dict]


class ForecastPoint(BaseModel):
    date: str
    actual: float | None = None
    predicted: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    metric: str
    data: list[ForecastPoint]
    horizon_days: int
    model_used: str
    accuracy_metrics: dict | None = None


class InsightItem(BaseModel):
    id: int
    type: str
    title: str
    body: str
    severity: str
    category: str | None = None
    confidence: float | None = None
    generated_at: str
    user_rating: int | None = None


class InsightsResponse(BaseModel):
    insights: list[InsightItem]
    total: int
