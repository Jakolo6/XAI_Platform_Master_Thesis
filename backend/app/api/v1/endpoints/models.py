"""
Model training and management endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
import uuid
import structlog

from app.core.database import get_db
from app.api.dependencies import get_current_researcher
from app.models.model import Model, ModelMetrics, ModelStatus
from app.tasks.training_tasks import train_model

router = APIRouter()
logger = structlog.get_logger()


# Pydantic schemas
class ModelTrainRequest(BaseModel):
    """Model training request schema."""
    name: str
    model_type: str
    dataset_id: str
    hyperparameters: Optional[Dict[str, Any]] = None
    optimize: bool = False


class ModelResponse(BaseModel):
    """Model response schema."""
    id: str
    name: str
    model_type: str
    dataset_id: str
    status: str
    version: str
    created_at: str
    completed_at: Optional[str] = None


class ModelMetricsResponse(BaseModel):
    """Model metrics response schema."""
    model_id: str
    auc_roc: Optional[float]
    auc_pr: Optional[float]
    f1_score: Optional[float]
    precision: Optional[float]
    recall: Optional[float]
    accuracy: Optional[float]
    log_loss: Optional[float]
    brier_score: Optional[float]


@router.post("/train", response_model=Dict[str, Any])
async def train_new_model(
    request: ModelTrainRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_researcher)
):
    """
    Train a new model.
    """
    # Validate dataset exists
    from app.datasets.registry import get_dataset_registry
    registry = get_dataset_registry()
    dataset_config = registry.get_dataset_config(request.dataset_id)
    
    if not dataset_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset not found: {request.dataset_id}"
        )
    
    # Check if dataset is processed
    from app.datasets.loaders import get_loader
    loader = get_loader(request.dataset_id, dataset_config)
    
    if not loader.splits_exist():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Dataset not processed. Run: python scripts/process_dataset.py {request.dataset_id}"
        )
    
    # Create model entry
    model_id = str(uuid.uuid4())
    new_model = Model(
        id=model_id,
        name=request.name,
        model_type=request.model_type,
        version="1.0",
        dataset_id=request.dataset_id,
        status=ModelStatus.PENDING,
        hyperparameters=request.hyperparameters or {},
    )
    
    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)
    
    # Queue training task
    task = train_model.delay(
        model_id=model_id,
        dataset_id=request.dataset_id,
        model_type=request.model_type,
        hyperparameters=request.hyperparameters,
        optimize=request.optimize
    )
    
    logger.info("Model training task queued",
               model_id=model_id,
               model_type=request.model_type,
               task_id=task.id)
    
    return {
        "message": "Model training started",
        "model_id": model_id,
        "task_id": task.id,
        "status": "pending"
    }


@router.get("/", response_model=List[ModelResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    model_type: Optional[str] = None,
    dataset_id: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_researcher)
):
    """
    List all models with optional filters.
    """
    query = select(Model)
    
    if model_type:
        query = query.where(Model.model_type == model_type)
    if dataset_id:
        query = query.where(Model.dataset_id == dataset_id)
    if status:
        query = query.where(Model.status == status)
    
    query = query.offset(skip).limit(limit).order_by(desc(Model.created_at))
    
    result = await db.execute(query)
    models = result.scalars().all()
    
    return [
        ModelResponse(
            id=model.id,
            name=model.name,
            model_type=model.model_type,
            dataset_id=model.dataset_id,
            status=model.status.value,
            version=model.version,
            created_at=model.created_at.isoformat(),
            completed_at=model.completed_at.isoformat() if model.completed_at else None
        )
        for model in models
    ]


@router.get("/{model_id}", response_model=Dict[str, Any])
async def get_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_researcher)
):
    """
    Get model details.
    """
    result = await db.execute(select(Model).where(Model.id == model_id))
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    return {
        "id": model.id,
        "name": model.name,
        "model_type": model.model_type,
        "dataset_id": model.dataset_id,
        "status": model.status.value,
        "version": model.version,
        "hyperparameters": model.hyperparameters,
        "training_config": model.training_config,
        "feature_importance": model.feature_importance,
        "model_path": model.model_path,
        "model_hash": model.model_hash,
        "model_size_mb": model.model_size_mb,
        "training_time_seconds": model.training_time_seconds,
        "error_message": model.error_message,
        "created_at": model.created_at.isoformat(),
        "completed_at": model.completed_at.isoformat() if model.completed_at else None
    }


@router.get("/{model_id}/metrics", response_model=ModelMetricsResponse)
async def get_model_metrics(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_researcher)
):
    """
    Get model performance metrics.
    """
    result = await db.execute(
        select(ModelMetrics).where(ModelMetrics.model_id == model_id)
    )
    metrics = result.scalar_one_or_none()
    
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model metrics not found"
        )
    
    return {
        "model_id": metrics.model_id,
        "auc_roc": metrics.auc_roc,
        "auc_pr": metrics.auc_pr,
        "f1_score": metrics.f1_score,
        "precision": metrics.precision,
        "recall": metrics.recall,
        "accuracy": metrics.accuracy,
        "log_loss": metrics.log_loss,
        "brier_score": metrics.brier_score,
        "confusion_matrix": metrics.confusion_matrix,
        "expected_calibration_error": metrics.expected_calibration_error,
        "maximum_calibration_error": metrics.maximum_calibration_error,
        "roc_curve": metrics.roc_curve,
        "pr_curve": metrics.pr_curve
    }


@router.get("/leaderboard/performance", response_model=List[Dict[str, Any]])
async def get_leaderboard(
    metric: str = "auc_roc",
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_researcher)
):
    """
    Get model performance leaderboard.
    """
    # Join models with metrics
    query = (
        select(Model, ModelMetrics)
        .join(ModelMetrics, Model.id == ModelMetrics.model_id)
        .where(Model.status == ModelStatus.COMPLETED)
        .limit(limit)
    )
    
    # Order by requested metric
    if metric == "auc_roc":
        query = query.order_by(desc(ModelMetrics.auc_roc))
    elif metric == "f1_score":
        query = query.order_by(desc(ModelMetrics.f1_score))
    elif metric == "accuracy":
        query = query.order_by(desc(ModelMetrics.accuracy))
    else:
        query = query.order_by(desc(ModelMetrics.auc_roc))
    
    result = await db.execute(query)
    rows = result.all()
    
    leaderboard = []
    for model, metrics in rows:
        leaderboard.append({
            "rank": len(leaderboard) + 1,
            "model_id": model.id,
            "model_name": model.name,
            "model_type": model.model_type,
            "auc_roc": metrics.auc_roc,
            "auc_pr": metrics.auc_pr,
            "f1_score": metrics.f1_score,
            "accuracy": metrics.accuracy,
            "training_time_seconds": model.training_time_seconds
        })
    
    return leaderboard


@router.delete("/{model_id}")
async def delete_model(
    model_id: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_researcher)
):
    """
    Delete a model.
    """
    result = await db.execute(select(Model).where(Model.id == model_id))
    model = result.scalar_one_or_none()
    
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found"
        )
    
    await db.delete(model)
    await db.commit()
    
    logger.info("Model deleted", model_id=model_id)
    
    return {
        "message": "Model deleted successfully",
        "model_id": model_id
    }
