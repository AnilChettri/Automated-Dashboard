"""
Churn Prediction Model (XGBoost)
Predicts probability of a customer churning.
"""

import os
import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Customer
from app.database import async_session

settings = get_settings()

MODEL_PATH = os.path.join(settings.ml_models_dir, "churn_model.pkl")


async def load_churn_data() -> pd.DataFrame:
    """Load features and targets for churn modeling."""
    async with async_session() as db:
        result = await db.execute(
            select(
                Customer.id,
                Customer.rfm_recency, Customer.rfm_frequency, Customer.rfm_monetary,
                Customer.lifetime_value, Customer.avg_order_value, Customer.is_churned
            ).where(Customer.rfm_recency.isnot(None))
        )
        rows = result.all()
        return pd.DataFrame(rows, columns=[
            "id", "recency", "frequency", "monetary", 
            "ltv", "aov", "is_churned"
        ])


def train_churn_model(df: pd.DataFrame):
    """Train XGBoost churn classifier."""
    if df.empty or len(df) < 50:
        return None

    features = ["recency", "frequency", "monetary", "ltv", "aov"]
    X = df[features]
    y = df["is_churned"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        objective="binary:logistic",
        eval_metric="auc",
        use_label_encoder=False
    )

    model.fit(X_train, y_train, eval_set=[(X_test, y_test)], verbose=False)

    os.makedirs(settings.ml_models_dir, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    # Predict probabilities for all customers
    probs = model.predict_proba(X)[:, 1]
    df["churn_probability"] = probs
    
    return df[["id", "churn_probability"]]


async def update_churn_probs(df: pd.DataFrame):
    """Update churn probabilities in SQLite."""
    async with async_session() as db:
        for _, row in df.iterrows():
            cid = int(row["id"])
            prob = float(row["churn_probability"])
            
            result = await db.execute(select(Customer).where(Customer.id == cid))
            customer = result.scalar_one_or_none()
            if customer:
                customer.churn_probability = round(prob, 3)
                
        await db.commit()


async def run_churn_pipeline():
    df = await load_churn_data()
    if df.empty:
        return {"success": False, "error": "No data"}
        
    predictions = train_churn_model(df)
    if predictions is not None:
        await update_churn_probs(predictions)
        return {"success": True, "updated": len(predictions)}
        
    return {"success": False, "error": "Training failed"}


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_churn_pipeline())
    print("Churn training completed.")
