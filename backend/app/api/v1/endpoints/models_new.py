"""
Model training endpoints - simplified without Celery.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
import structlog

from app.api.dependencies import get_current_researcher
from app.services.model_service import model_service
from app.services.dataset_service import dataset_service
from app.utils.supabase_client import supabase_db

logger = structlog.get_logger()
router = APIRouter()


class ModelTrainRequest(BaseModel):
    """Model training request schema."""
    dataset_id: str
    model_type: str  # 'xgboost', 'random_forest', etc.
    hyperparameters: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_models(
    dataset_id: Optional[str] = None,
    current_user: str = Depends(get_current_researcher)
):
    """List all trained models, optionally filtered by dataset."""
    try:
        models = supabase_db.list_models(dataset_id=dataset_id)
        return models
    except Exception as e:
        logger.error("Failed to list models", exc_info=e)
        return []


@router.get("/{model_id}")
async def get_model(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """Get detailed information about a specific model."""
    try:
        model = supabase_db.get_model(model_id)
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        return model
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get model", model_id=model_id, exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/train")
async def train_model(
    request: ModelTrainRequest,
    background_tasks: BackgroundTasks,
    current_user: str = Depends(get_current_researcher)
):
    """
    Train a new model on a processed dataset.
    Training happens in background to avoid timeout.
    """
    try:
        # Validate dataset is processed
        status_check = dataset_service.check_dataset_status(request.dataset_id)
        
        if not status_check['processed']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Dataset {request.dataset_id} is not processed. Status: {status_check['status']}. Please process the dataset first."
            )
        
        # Validate model type
        supported_models = ['xgboost', 'random_forest']
        if request.model_type not in supported_models:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported model type: {request.model_type}. Supported: {supported_models}"
            )
        
        # Add training to background tasks
        background_tasks.add_task(
            model_service.train_model,
            request.dataset_id,
            request.model_type,
            request.hyperparameters
        )
        
        logger.info("Model training queued",
                   dataset_id=request.dataset_id,
                   model_type=request.model_type)
        
        return {
            "message": "Model training started",
            "dataset_id": request.dataset_id,
            "model_type": request.model_type,
            "status": "training",
            "note": "Training may take 5-10 minutes. Check status with GET /models/"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start model training",
                    dataset_id=request.dataset_id,
                    exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/dataset/{dataset_id}")
async def list_models_for_dataset(
    dataset_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """List all models trained on a specific dataset."""
    try:
        models = supabase_db.list_models(dataset_id=dataset_id)
        return models
    except Exception as e:
        logger.error("Failed to list models for dataset",
                    dataset_id=dataset_id,
                    exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
