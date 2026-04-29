from fastapi import APIRouter, Query, HTTPException
from app.services.ml_service import get_ml_service
from app.schemas.analytics import ForecastResponse, ForecastPoint
from ml.forecasting import generate_forecast

router = APIRouter(prefix="/api/forecast", tags=["Forecasting"])


@router.get("/status")
async def forecast_status():
    """Check forecasting model status."""
    import os
    from app.config import get_settings
    settings = get_settings()
    
    model_path = os.path.join(settings.ml_models_dir, "forecasting_model.pkl")
    model_exists = os.path.exists(model_path)
    
    return {
        "available": model_exists,
        "model": "Prophet" if model_exists else None,
        "message": "Forecasting model ready" if model_exists else "Model not trained yet. Run /api/ml/train first.",
    }


@router.get("/revenue", response_model=ForecastResponse)
async def get_revenue_forecast(
    horizon: int = Query(default=30, ge=7, le=90)
):
    """Get revenue forecast for the next N days."""
    ml_service = get_ml_service()
    try:
        model = ml_service.get_forecaster()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    forecast_df = generate_forecast(model, horizon=horizon)
    
    data = [
        ForecastPoint(
            date=row["ds"].strftime("%Y-%m-%d"),
            predicted=round(float(row["yhat"]), 2),
            lower_bound=round(float(row["yhat_lower"]), 2),
            upper_bound=round(float(row["yhat_upper"]), 2)
        )
        for _, row in forecast_df.iterrows()
    ]
    
    return ForecastResponse(
        metric="Revenue",
        data=data,
        horizon_days=horizon,
        model_used="Prophet"
    )
