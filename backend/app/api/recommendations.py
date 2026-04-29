"""
Recommendations API Routes
"""

from fastapi import APIRouter, Depends
from app.services.recommendation_service import recommendation_service

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("/products")
async def get_product_recommendations(limit: int = 5):
    """Get high-margin product recommendations."""
    products = await recommendation_service.get_product_recommendations(limit=limit)
    return products

@router.get("/actions")
async def get_customer_actions(limit: int = 5):
    """Get prioritized business actions for customers."""
    actions = await recommendation_service.get_customer_actions(limit=limit)
    return actions
