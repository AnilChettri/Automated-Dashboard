"""
Order Model
Stores individual order transactions linking customers and products.
"""

from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    # Foreign Keys
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    
    # Order Details
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount: Mapped[float] = mapped_column(Float, default=0.0)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="completed")  # completed, refunded, cancelled
    payment_method: Mapped[str | None] = mapped_column(String(50), nullable=True)
    
    # Location
    channel: Mapped[str] = mapped_column(String(50), default="online")  # online, in-store, mobile
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    order_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="orders", lazy="selectin")
    product = relationship("Product", back_populates="orders", lazy="selectin")

    def __repr__(self):
        return f"<Order(id={self.id}, order_number='{self.order_number}', total={self.total})>"
