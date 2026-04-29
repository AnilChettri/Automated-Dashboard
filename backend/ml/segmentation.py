"""
Customer Segmentation Model (K-Means)
Computes RFM clusters and assigns segments based on cluster centroids.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models import Customer
from app.database import engine, async_session

settings = get_settings()

MODEL_PATH = os.path.join(settings.ml_models_dir, "segmentation.pkl")
SCALER_PATH = os.path.join(settings.ml_models_dir, "segmentation_scaler.pkl")


async def load_data() -> pd.DataFrame:
    """Load RFM data from database."""
    async with async_session() as db:
        result = await db.execute(
            select(Customer.id, Customer.rfm_recency, Customer.rfm_frequency, Customer.rfm_monetary)
            .where(Customer.rfm_recency.isnot(None))
        )
        rows = result.all()
        return pd.DataFrame(rows, columns=["id", "recency", "frequency", "monetary"])


def train_model(df: pd.DataFrame, n_clusters: int = 5):
    """Train K-Means model on RFM data."""
    if df.empty or len(df) < n_clusters:
        return

    # Extract features
    features = df[["recency", "frequency", "monetary"]].copy()

    # Log transform monetary and frequency to handle skewness
    features["monetary"] = np.log1p(features["monetary"])
    features["frequency"] = np.log1p(features["frequency"])

    # Scale features
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(features)

    # Train
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    kmeans.fit(scaled_data)

    # Save artifacts
    os.makedirs(settings.ml_models_dir, exist_ok=True)
    joblib.dump(kmeans, MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    # Identify segment labels based on centroids
    # Centroids [recency, frequency, monetary]
    centroids = scaler.inverse_transform(kmeans.cluster_centers_)
    
    label_map = {}
    for i in range(n_clusters):
        r, f, m = centroids[i]
        # Heuristics for naming clusters based on centers
        if r < np.median(df.recency) and f > np.median(df.frequency) and m > np.median(df.monetary):
            label = "Champions"
        elif r > np.percentile(df.recency, 75) and f < np.median(df.frequency):
            label = "At Risk"
        elif m > np.percentile(df.monetary, 75):
            label = "High Value"
        elif r < np.median(df.recency) and f <= np.median(df.frequency):
            label = "New Customers"
        else:
            label = "Regular"
        label_map[i] = label

    # Predict and update DB
    df["cluster"] = kmeans.labels_
    df["segment"] = df["cluster"].map(label_map)
    return df[["id", "segment"]]


async def update_database(segment_df: pd.DataFrame):
    """Update customer segments in SQLite."""
    async with async_session() as db:
        for _, row in segment_df.iterrows():
            customer_id = int(row["id"])
            segment = row["segment"]
            # Just an explicit update scalar
            result = await db.execute(select(Customer).where(Customer.id == customer_id))
            customer = result.scalar_one_or_none()
            if customer:
                customer.segment = segment
        await db.commit()


async def run_segmentation():
    """Main pipeline function."""
    df = await load_data()
    if df.empty:
        return {"success": False, "error": "No RFM data available"}
    
    segments = train_model(df)
    if segments is not None:
        await update_database(segments)
        return {"success": True, "updated": len(segments)}
    return {"success": False, "error": "Not enough data to train"}


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_segmentation())
    print("Segmentation completed.")
