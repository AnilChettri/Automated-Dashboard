"""
Customer Model
Stores customer profiles, segments, and churn predictions.
"""

from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), default="US")
    
    # Segmentation
    segment: Mapped[str | None] = mapped_column(String(50), nullable=True)  # High Value, At Risk, etc.
    
    # RFM Scores (computed)
    rfm_recency: Mapped[float | None] = mapped_column(Float, nullable=True)
    rfm_frequency: Mapped[float | None] = mapped_column(Float, nullable=True)
    rfm_monetary: Mapped[float | None] = mapped_column(Float, nullable=True)
    rfm_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Churn Prediction
    churn_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_churned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Lifetime Value
    lifetime_value: Mapped[float] = mapped_column(Float, default=0.0)
    total_orders: Mapped[int] = mapped_column(Integer, default=0)
    avg_order_value: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Timestamps
    first_purchase_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_purchase_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    orders = relationship("Order", back_populates="customer", lazy="selectin")

    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', segment='{self.segment}')>"
