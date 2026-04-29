"""
Anomaly Detection Service
Identifies unusual patterns in revenue and order volume.
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.database import async_session
from app.models import Order

logger = logging.getLogger(__name__)

class AnomalyService:
    async def detect_revenue_anomalies(self, days: int = 30):
        """Detect revenue anomalies using Z-score method."""
        async with async_session() as db:
            # Get daily revenue for the last N days
            start_date = datetime.utcnow() - timedelta(days=days + 60) # Look back further for baseline
            result = await db.execute(
                select(
                    func.date(Order.order_date).label("date"),
                    func.sum(Order.total).label("revenue")
                )
                .where(Order.order_date >= start_date, Order.status == "completed")
                .group_by(func.date(Order.order_date))
                .order_by(func.date(Order.order_date))
            )
            rows = result.all()
            if not rows or len(rows) < 14:
                return []

            df = pd.DataFrame(rows, columns=["date", "revenue"])
            df["revenue"] = df["revenue"].astype(float)
            
            # Simple Z-score detection
            mean = df["revenue"].mean()
            std = df["revenue"].std()
            
            if std == 0:
                return []

            df["z_score"] = (df["revenue"] - mean) / std
            
            # Detect anomalies in the most recent 'days'
            anomalies = df[(df["z_score"].abs() > 2) & (df["date"] >= (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d"))]
            
            results = []
            for _, row in anomalies.iterrows():
                results.append({
                    "date": str(row["date"]),
                    "value": row["revenue"],
                    "z_score": row["z_score"],
                    "severity": "critical" if abs(row["z_score"]) > 3 else "warning",
                    "type": "spike" if row["z_score"] > 0 else "drop"
                })
            
            return results

anomaly_service = AnomalyService()
