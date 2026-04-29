from pydantic import BaseModel, Field
from datetime import datetime

class CustomerBase(BaseModel):
    name: str
    email: str
    city: str | None = None
    country: str | None = None
    segment: str | None = None

class CustomerListItem(CustomerBase):
    id: int
    lifetime_value: float
    total_orders: int
    avg_order_value: float
    churn_probability: float | None = None
    last_purchase_date: datetime | None = None

class CustomerDetail(CustomerListItem):
    created_at: datetime
    # We can add order history here if needed
    
class CustomerListResponse(BaseModel):
    customers: list[CustomerListItem]
    total: int
    page: int
    page_size: int
