"""
ML Pipeline Management Routes
Trigger and monitor training of churn and forecasting models.
"""

import os
import asyncio
from fastapi import APIRouter, BackgroundTasks, HTTPException
from app.config import get_settings
from ml.churn import run_churn_pipeline
from ml.forecasting import run_forecasting_pipeline

settings = get_settings()
router = APIRouter(prefix="/api/ml", tags=["ML Management"])

# In-memory status tracking (could be replaced by Redis/DB for prod)
training_status = {
    "is_training": False,
    "last_run": None,
    "last_result": None,
    "error": None
}


async def _run_training():
    global training_status
    training_status["is_training"] = True
    training_status["error"] = None
    
    try:
        # Run churn pipeline
        churn_res = await run_churn_pipeline()
        
        # Run forecasting pipeline
        forecast_res = await run_forecasting_pipeline()
        
        training_status["last_result"] = {
            "churn": churn_res,
            "forecasting": forecast_res
        }
    except Exception as e:
        training_status["error"] = str(e)
    finally:
        training_status["is_training"] = False
        from datetime import datetime
        training_status["last_run"] = datetime.utcnow().isoformat()


@router.post("/train")
async def trigger_training(background_tasks: BackgroundTasks):
    """Trigger the full ML pipeline training in the background."""
    if training_status["is_training"]:
        return {"message": "Training already in progress."}
    
    background_tasks.add_task(_run_training)
    return {"message": "Training started in background."}


@router.get("/status")
async def get_training_status():
    """Get the status of the last training run."""
    # Check if models exist on disk
    churn_path = os.path.join(settings.ml_models_dir, "churn_model.pkl")
    forecast_path = os.path.join(settings.ml_models_dir, "forecasting_model.pkl")
    
    return {
        "status": training_status,
        "models": {
            "churn": os.path.exists(churn_path),
            "forecasting": os.path.exists(forecast_path)
        }
    }
