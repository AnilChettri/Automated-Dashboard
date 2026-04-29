"""
Insight Service
Generates automated business insights by running analytical queries and feeding them to GPT.
"""

import logging
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import async_session
from app.models import Order, Customer
from app.models.insight import Insight
from app.services.ai_service import ai_service

settings = get_settings()
logger = logging.getLogger(__name__)


class InsightService:
    async def run_analysis(self) -> dict:
        """Run daily pipeline to fetch raw metrics for the LLM to analyze."""
        now = datetime.utcnow()
        t30 = now - timedelta(days=30)
        t60 = now - timedelta(days=60)
        
        async with async_session() as db:
            # Revenue & Orders Last 30d
            res1 = await db.execute(
                select(func.sum(Order.total), func.count(Order.id))
                .where(and_(Order.order_date >= t30, Order.status == 'completed'))
            )
            r30 = res1.one()
            rev30, ord30 = float(r30[0] or 0), int(r30[1] or 0)
            
            # Revenue & Orders Prev 30d
            res2 = await db.execute(
                select(func.sum(Order.total), func.count(Order.id))
                .where(and_(Order.order_date >= t60, Order.order_date < t30, Order.status == 'completed'))
            )
            r60 = res2.one()
            rev60, ord60 = float(r60[0] or 0), int(r60[1] or 0)
            
            # Active Churned users
            churn_res = await db.execute(select(func.count(Customer.id)).where(Customer.is_churned == True))
            churn_cnt = churn_res.scalar() or 0
            
            # Total users
            tot_res = await db.execute(select(func.count(Customer.id)))
            tot_cnt = tot_res.scalar() or 1

            # Top Products
            from app.models import Product
            prod_res = await db.execute(
                select(Product.name, func.sum(Order.total).label("revenue"))
                .join(Order, Order.product_id == Product.id)
                .where(Order.status == "completed")
                .group_by(Product.name)
                .order_by(func.sum(Order.total).desc())
                .limit(3)
            )
            top_products = [{"name": r[0], "revenue": float(r[1])} for r in prod_res.all()]

            # Segments
            seg_res = await db.execute(
                select(Customer.segment, func.count(Customer.id))
                .group_by(Customer.segment)
            )
            segments = {r[0]: int(r[1]) for r in seg_res.all() if r[0]}

        return {
            "last_30_days": {"revenue": rev30, "orders": ord30},
            "previous_30_days": {"revenue": rev60, "orders": ord60},
            "revenue_growth": round(((rev30 - rev60) / rev60) * 100, 2) if rev60 > 0 else 0,
            "orders_growth": round(((ord30 - ord60) / ord60) * 100, 2) if ord60 > 0 else 0,
            "churn_rate": round(churn_cnt / tot_cnt * 100, 2),
            "top_products": top_products,
            "segments": segments
        }

    async def generate_insights(self):
        if not ai_service.enabled:
            return []
            
        data = await self.run_analysis()
        
        prompt = f"""
        You are an expert Business Analyst. Review the following metrics for an e-commerce platform:
        
        OVERALL PERFORMANCE:
        - Last 30 Days Revenue: ${data['last_30_days']['revenue']:,.2f} (Growth: {data['revenue_growth']}%)
        - Last 30 Days Orders: {data['last_30_days']['orders']} (Growth: {data['orders_growth']}%)
        - Current Churn Rate: {data['churn_rate']}%
        
        TOP PRODUCTS:
        {", ".join([f"{p['name']} (${p['revenue']:,.0f})" for p in data['top_products']])}
        
        CUSTOMER SEGMENTS:
        {", ".join([f"{k}: {v}" for k, v in data['segments'].items()])}
        
        Generate exactly 3 actionable insights based on these metrics. Return as a JSON array of objects.
        Each object must have exactly these keys:
        - "title": (string) Short catchy title
        - "body": (string) Detailed explanation and actionable recommendation (max 3 sentences)
        - "severity": (string) Choose either "info", "warning", or "critical"
        - "category": (string) e.g., "revenue", "churn", "growth", "product"
        
        IMPORTANT: Return ONLY valid JSON, no markdown blocks.
        """
        
        try:
            res = await ai_service.client.chat.completions.create(
                model=ai_service.model,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = res.choices[0].message.content.strip()
            
            # Trim markdown if exists
            if raw.startswith("```json"): raw = raw[7:]
            if raw.startswith("```"): raw = raw[3:]
            if raw.endswith("```"): raw = raw[:-3]
            
            import json
            insights_data = json.loads(raw.strip())
            
            async with async_session() as db:
                added = []
                for item in insights_data:
                    insight = Insight(
                        type="auto",
                        title=item["title"],
                        body=item["body"],
                        severity=item.get("severity", "info"),
                        category=item.get("category", "growth")
                    )
                    db.add(insight)
                    added.append(insight)
                await db.commit()
                
            return added
            
        except Exception as e:
            logger.error(f"Failed to generate auto-insights: {e}")
            return []

# Singleton
insight_service = InsightService()
