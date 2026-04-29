from pydantic import BaseModel

class ProductBase(BaseModel):
    name: str
    category: str
    price: float
    cost: float
    margin: float
    stock_quantity: int

class ProductListItem(ProductBase):
    id: int
    revenue_30d: float = 0.0
    units_sold_30d: int = 0
    performance_score: float | None = None

class ProductListResponse(BaseModel):
    products: list[ProductListItem]
    total: int
