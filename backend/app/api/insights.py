"""
Insights API Routes (stub — implemented in Phase 4)
AI-generated business insights.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models.insight import Insight

router = APIRouter(prefix="/api/insights", tags=["Insights"])


@router.get("/latest")
async def get_latest_insights(
    limit: int = Query(default=10, ge=1, le=50),
    severity: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Get latest AI-generated insights."""
    query = select(Insight).order_by(desc(Insight.generated_at)).limit(limit)
    if severity:
        query = query.where(Insight.severity == severity)

    result = await db.execute(query)
    insights = result.scalars().all()

    return {
        "insights": [
            {
                "id": i.id,
                "type": i.type,
                "title": i.title,
                "body": i.body,
                "severity": i.severity,
                "category": i.category,
                "confidence": i.confidence,
                "generated_at": i.generated_at.isoformat() if i.generated_at else None,
                "user_rating": i.user_rating,
            }
            for i in insights
        ],
        "total": len(insights),
    }


@router.post("/{insight_id}/rate")
async def rate_insight(
    insight_id: int,
    rating: int = Query(ge=1, le=5),
    db: AsyncSession = Depends(get_db),
):
    """Rate an insight for feedback loop."""
    result = await db.execute(select(Insight).where(Insight.id == insight_id))
    insight = result.scalar_one_or_none()
    if not insight:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Insight not found")
    
    insight.user_rating = rating
    await db.commit()
    return {"success": True, "message": f"Insight {insight_id} rated {rating}/5"}


@router.post("/generate")
async def generate_insights():
    """Trigger AI generation of new insights."""
    from app.services.insight_service import insight_service
    
    insights = await insight_service.generate_insights()
    
    return {
        "success": True,
        "message": f"Generated {len(insights)} new insights",
        "insights": [
            {
                "id": i.id,
                "title": i.title,
                "severity": i.severity
            } for i in insights
        ]
    }
