"""
Revenue Forecasting Model (Prophet)
Predicts future daily revenue.
"""

import os
import joblib
import pandas as pd
from prophet import Prophet
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Order
from app.database import async_session

settings = get_settings()

MODEL_PATH = os.path.join(settings.ml_models_dir, "forecasting_model.pkl")


async def load_revenue_data() -> pd.DataFrame:
    """Load daily revenue for forecasting."""
    async with async_session() as db:
        # Get completed orders
        result = await db.execute(
            select(
                func.date(Order.order_date).label('ds'),
                func.sum(Order.total).label('y')
            )
            .where(Order.status == "completed")
            .group_by(func.date(Order.order_date))
            .order_by(func.date(Order.order_date))
        )
        rows = result.all()
        df = pd.DataFrame(rows, columns=["ds", "y"])
        # Prophet expects 'ds' (datetime) and 'y' (numeric)
        df['ds'] = pd.to_datetime(df['ds'])
        df['y'] = pd.to_numeric(df['y'])
        return df


def train_forecaster(df: pd.DataFrame):
    """Train Prophet model."""
    if df.empty or len(df) < 30:  # Need at least 30 days
        return None

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05
    )
    
    # Add holidays (US as default)
    model.add_country_holidays(country_name='US')
    
    model.fit(df)
    
    os.makedirs(settings.ml_models_dir, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    
    return model


def generate_forecast(model: Prophet, horizon: int = 30):
    """Generate future predictions."""
    future = model.make_future_dataframe(periods=horizon)
    forecast = model.predict(future)
    
    # Return just the future window
    future_forecast = forecast.tail(horizon)[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return future_forecast


async def run_forecasting_pipeline():
    df = await load_revenue_data()
    if df.empty:
        return {"success": False, "error": "No data"}
        
    model = train_forecaster(df)
    if model is not None:
        return {"success": True, "message": "Forecaster trained"}
        
    return {"success": False, "error": "Training failed"}


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_forecasting_pipeline())
    print("Forecasting training completed.")
