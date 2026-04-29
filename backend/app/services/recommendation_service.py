"""
Recommendation Service
Hybrid engine (Rule-based + Simple ML) for business recommendations.
"""

import logging
from sqlalchemy import select, func, desc
from app.database import async_session
from app.models import Customer, Product, Order

logger = logging.getLogger(__name__)

class RecommendationService:
    async def get_product_recommendations(self, limit: int = 5):
        """Recommend products based on popularity and margins."""
        async with async_session() as db:
            # Top sellers with high margin
            result = await db.execute(
                select(Product)
                .where(Product.is_active == True)
                .order_by(desc(Product.margin), desc(Product.price))
                .limit(limit)
            )
            return result.scalars().all()

    async def get_customer_actions(self, limit: int = 5):
        """Recommend actions for specific customer segments."""
        async with async_session() as db:
            actions = []
            
            # 1. High Churn Risk (At Risk segment)
            at_risk = await db.execute(
                select(Customer)
                .where(Customer.segment == "At Risk")
                .order_by(desc(Customer.churn_probability))
                .limit(limit)
            )
            for c in at_risk.scalars().all():
                actions.append({
                    "type": "retention",
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "title": "High Churn Risk",
                    "action": f"Send personalized 'We Miss You' discount to {c.name}.",
                    "priority": "high" if c.churn_probability > 0.8 else "medium"
                })

            # 2. Upsell Opportunity (Loyal segment but lower AOV)
            upsell = await db.execute(
                select(Customer)
                .where(Customer.segment == "Loyal")
                .order_by(Customer.avg_order_value)
                .limit(limit)
            )
            for c in upsell.scalars().all():
                actions.append({
                    "type": "upsell",
                    "customer_id": c.id,
                    "customer_name": c.name,
                    "title": "Upsell Opportunity",
                    "action": f"Recommend premium bundles to increase AOV for {c.name}.",
                    "priority": "medium"
                })

            return actions

recommendation_service = RecommendationService()
