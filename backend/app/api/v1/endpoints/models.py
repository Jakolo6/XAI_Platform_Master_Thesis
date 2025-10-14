"""
Model training endpoints - simplified without Celery.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, ConfigDict
import structlog

from app.api.dependencies import get_current_researcher
from app.services.model_service import model_service
from app.services.dataset_service import dataset_service
from app.utils.supabase_client import supabase_db
from app.core.data_access import dal

logger = structlog.get_logger()
router = APIRouter()


class ModelTrainRequest(BaseModel):
    """Model training request schema."""
    model_config = ConfigDict(protected_namespaces=())
    
    dataset_id: str
    model_type: str  # 'xgboost', 'random_forest', etc.
    model_name: Optional[str] = None  # Custom name for the model
    hyperparameters: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_models(
    dataset_id: Optional[str] = None,
    current_user: str = Depends(get_current_researcher)
):
    """List all trained models with metrics, optionally filtered by dataset."""
    try:
        # Use DAL to get models with metrics automatically included
        models = dal.list_models(dataset_id=dataset_id, include_metrics=True)
        
        logger.info("Models listed with metrics", 
                   count=len(models),
                   dataset_id=dataset_id)
        
        return models
    except Exception as e:
        logger.error("Failed to list models", exc_info=e)
        return []


@router.get("/{model_id}")
async def get_model(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """Get detailed information about a specific model with metrics."""
    try:
        # Use DAL to get model with metrics automatically included
        model = dal.get_model(model_id, include_metrics=True)
        
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        logger.info("Model retrieved with metrics", 
                   model_id=model_id,
                   has_auc_roc='auc_roc' in model,
                   auc_roc=model.get('auc_roc'))
        
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
        
        # Wrapper to catch background task errors
        def train_with_error_handling():
            import sys
            import traceback
            try:
                print("=" * 80, flush=True)
                print("🚀 BACKGROUND TRAINING STARTED", flush=True)
                print(f"Dataset: {request.dataset_id}", flush=True)
                print(f"Model Type: {request.model_type}", flush=True)
                print(f"Model Name: {request.model_name}", flush=True)
                print("=" * 80, flush=True)
                sys.stdout.flush()
                sys.stderr.flush()
                
                logger.info("🚀 Background training started",
                           dataset_id=request.dataset_id,
                           model_type=request.model_type,
                           model_name=request.model_name)
                sys.stdout.flush()
                
                result = model_service.train_model(
                    request.dataset_id,
                    request.model_type,
                    request.hyperparameters,
                    request.model_name
                )
                
                print("=" * 80, flush=True)
                if result.get('status') == 'error':
                    print("❌ BACKGROUND TRAINING FAILED", flush=True)
                    print(f"Error: {result.get('error')}", flush=True)
                    print(f"Traceback:\n{result.get('traceback')}", flush=True)
                else:
                    print("✅ BACKGROUND TRAINING COMPLETED", flush=True)
                    print(f"Model ID: {result.get('model_id')}", flush=True)
                    print(f"Accuracy: {result.get('metrics', {}).get('accuracy')}", flush=True)
                print("=" * 80, flush=True)
                sys.stdout.flush()
                sys.stderr.flush()
                
                logger.info("✅ Background training completed",
                           dataset_id=request.dataset_id,
                           result_status=result.get('status'))
                sys.stdout.flush()
                
            except Exception as e:
                error_trace = traceback.format_exc()
                print("=" * 80, flush=True)
                print("❌ BACKGROUND TRAINING FAILED", flush=True)
                print(f"Error: {str(e)}", flush=True)
                print(f"Traceback:\n{error_trace}", flush=True)
                print("=" * 80, flush=True)
                sys.stdout.flush()
                sys.stderr.flush()
                
                logger.error("❌ Background training failed",
                           dataset_id=request.dataset_id,
                           error=str(e),
                           traceback=error_trace,
                           exc_info=True)
                sys.stdout.flush()
                sys.stderr.flush()
        
        # Add wrapped task to background
        background_tasks.add_task(train_with_error_handling)
        
        logger.info("📋 Model training queued",
                   dataset_id=request.dataset_id,
                   model_type=request.model_type,
                   model_name=request.model_name)
        
        return {
            "message": "Model training started",
            "dataset_id": request.dataset_id,
            "model_type": request.model_type,
            "model_name": request.model_name,
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


@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """
    Delete a model and all its associated data.
    
    This will delete:
    - Model metadata
    - Model metrics
    - Model explanations (SHAP, LIME)
    - Model file from R2 storage
    """
    try:
        # Strip _metrics suffix if present
        base_model_id = model_id.replace('_metrics', '')
        
        # Check if model exists
        model = supabase_db.get_model(base_model_id)
        if not model:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model {model_id} not found"
            )
        
        logger.info("Deleting model", model_id=base_model_id, user=current_user)
        
        # Delete explanations first
        try:
            explanations = supabase_db.list_explanations(model_id=base_model_id)
            for exp in explanations:
                supabase_db.client.table('explanations').delete().eq('id', exp['id']).execute()
            logger.info("Deleted explanations", model_id=base_model_id, count=len(explanations))
        except Exception as e:
            logger.warning("Failed to delete explanations", error=str(e))
        
        # Delete metrics
        try:
            supabase_db.client.table('model_metrics').delete().eq('model_id', base_model_id).execute()
            logger.info("Deleted metrics", model_id=base_model_id)
        except Exception as e:
            logger.warning("Failed to delete metrics", error=str(e))
        
        # Delete model metadata
        supabase_db.client.table('models').delete().eq('id', base_model_id).execute()
        logger.info("Deleted model metadata", model_id=base_model_id)
        
        # TODO: Delete model file from R2 storage if needed
        # This would require the R2 client and model file path
        
        return {
            "message": "Model deleted successfully",
            "model_id": base_model_id,
            "deleted_items": ["model", "metrics", "explanations"]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete model", model_id=model_id, error=str(e), exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete model: {str(e)}"
        )


@router.get("/dataset/{dataset_id}")
async def list_models_for_dataset(
    dataset_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """List all models trained on a specific dataset."""
    try:
        models = supabase_db.list_models(dataset_id=dataset_id)
        
        # Enrich each model with its metrics
        enriched_models = []
        for model in models:
            metrics = supabase_db.get_model_metrics(model['id'])
            if metrics:
                model_with_metrics = {**model, **metrics}
            else:
                model_with_metrics = model
            enriched_models.append(model_with_metrics)
        
        return enriched_models
    except Exception as e:
        logger.error("Failed to list models for dataset",
                    dataset_id=dataset_id,
                    exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
