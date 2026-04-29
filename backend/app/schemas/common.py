"""
Common Pydantic schemas used across the application.
"""

from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    environment: str
    database: str = "connected"
    ai_available: bool = False


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    data: list
    total: int
    page: int
    page_size: int
    total_pages: int


class DateRangeParams(BaseModel):
    start_date: datetime | None = None
    end_date: datetime | None = None
    period: str = "30d"  # 7d, 30d, 90d, 1y, all


class APIResponse(BaseModel):
    success: bool = True
    data: dict | list | None = None
    message: str | None = None
    error: str | None = None
