"""
ML Service
Loads pre-trained artifacts for inference.
"""

import os
import joblib
from functools import lru_cache

from app.config import get_settings

settings = get_settings()


class MLModels:
    def __init__(self):
        self.models = {}

    def load_model(self, name: str, fallback_msg: str):
        if name in self.models:
            return self.models[name]
            
        path = os.path.join(settings.ml_models_dir, f"{name}.pkl")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model {name} not found. {fallback_msg}")
            
        model = joblib.load(path)
        self.models[name] = model
        return model

    def get_forecaster(self):
        return self.load_model("forecasting_model", "Run forecasting pipeline first.")


@lru_cache()
def get_ml_service() -> MLModels:
    """Singleton instance."""
    return MLModels()
