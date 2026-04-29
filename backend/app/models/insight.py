"""
Insight Model
Stores AI-generated insights, alerts, and recommendations.
"""

from datetime import datetime
from sqlalchemy import String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Insight Content
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # auto, alert, recommendation, anomaly
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Classification
    severity: Mapped[str] = mapped_column(String(20), default="info")  # info, warning, critical
    category: Mapped[str] = mapped_column(String(100), nullable=True)  # revenue, churn, growth, etc.
    
    # Metadata
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # supporting data, metrics
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)  # 0.0 - 1.0
    
    # Feedback
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 1 (👎) to 5 (👍)
    is_dismissed: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Insight(id={self.id}, type='{self.type}', severity='{self.severity}')>"


class ChatHistory(Base):
    """Stores NL→SQL chat conversations."""
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    
    # Conversation
    user_query: Mapped[str] = mapped_column(Text, nullable=False)
    generated_sql: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Quality
    is_successful: Mapped[bool] = mapped_column(default=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_rating: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ChatHistory(id={self.id}, session='{self.session_id}')>"
