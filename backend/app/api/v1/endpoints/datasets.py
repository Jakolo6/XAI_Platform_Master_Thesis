"""
Dataset management endpoints - simplified without Celery.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel
import structlog

from app.api.dependencies import get_current_researcher
from app.services.dataset_service import dataset_service
from app.utils.supabase_client import supabase_db
from app.datasets.registry import get_dataset_registry

logger = structlog.get_logger()
router = APIRouter()


class DatasetProcessRequest(BaseModel):
    """Dataset processing request schema."""
    apply_sampling: bool = True


@router.get("/")
async def list_datasets(
    skip: int = 0,
    limit: int = 100
):
    """
    List all datasets from registry and Supabase.
    Combines registry configuration with processing status.
    Public endpoint - no authentication required.
    """
    try:
        # Get datasets from registry
        registry = get_dataset_registry()
        datasets = []
        
        for dataset_id, config in registry.datasets.items():
            # Get processing status from Supabase (with error handling)
            db_dataset = None
            try:
                if supabase_db.is_available():
                    db_dataset = supabase_db.get_dataset(dataset_id)
            except Exception as e:
                logger.warning("Could not fetch dataset from Supabase", 
                             dataset_id=dataset_id, 
                             error=str(e))
            
            # Combine registry config with database status
            dataset_info = {
                "id": dataset_id,
                "name": dataset_id,
                "display_name": config.get("display_name", dataset_id),
                "description": config.get("description", ""),
                "tags": config.get("tags", []),
                "source": config.get("source", "kaggle"),
                
                # From database (if exists)
                "status": db_dataset.get("status", "pending") if db_dataset else "pending",
                "total_samples": db_dataset.get("total_rows", 0) if db_dataset else 0,
                "num_features": db_dataset.get("total_columns", 0) if db_dataset else 0,
                "train_samples": db_dataset.get("train_rows", 0) if db_dataset else 0,
                "val_samples": db_dataset.get("val_rows", 0) if db_dataset else 0,
                "test_samples": db_dataset.get("test_rows", 0) if db_dataset else 0,
                "fraud_count": db_dataset.get("fraud_count", 0) if db_dataset else 0,
                "non_fraud_count": db_dataset.get("non_fraud_count", 0) if db_dataset else 0,
                "fraud_percentage": db_dataset.get("fraud_percentage") if db_dataset else None,
                "completed_at": db_dataset.get("completed_at") if db_dataset else None,
                "file_path": db_dataset.get("file_path") if db_dataset else None
            }
            
            datasets.append(dataset_info)
        
        return datasets
    
    except Exception as e:
        logger.error("Failed to list datasets", exc_info=e)
        return []


@router.get("/{dataset_id}")
async def get_dataset(
    dataset_id: str
):
    """Get detailed information about a specific dataset. Public endpoint."""
    try:
        # Get from registry
        registry = get_dataset_registry()
        config = registry.get_dataset_config(dataset_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found"
            )
        
        # Get processing status from Supabase (with error handling)
        db_dataset = None
        try:
            if supabase_db.is_available():
                db_dataset = supabase_db.get_dataset(dataset_id)
        except Exception as e:
            logger.warning("Could not fetch dataset from Supabase", 
                         dataset_id=dataset_id, 
                         error=str(e))
        
        return {
            "id": dataset_id,
            "name": dataset_id,
            "display_name": config.get("display_name", dataset_id),
            "description": config.get("description", ""),
            "tags": config.get("tags", []),
            "source": config.get("source", "kaggle"),
            "target_column": config.get("target_column"),
            "preprocessing_pipeline": config.get("preprocessing_pipeline", []),
            
            # From database
            "status": db_dataset.get("status", "pending") if db_dataset else "pending",
            "total_samples": db_dataset.get("total_rows", 0) if db_dataset else 0,
            "num_features": db_dataset.get("total_columns", 0) if db_dataset else 0,
            "train_samples": db_dataset.get("train_rows", 0) if db_dataset else 0,
            "val_samples": db_dataset.get("val_rows", 0) if db_dataset else 0,
            "test_samples": db_dataset.get("test_rows", 0) if db_dataset else 0,
            "fraud_count": db_dataset.get("fraud_count", 0) if db_dataset else 0,
            "non_fraud_count": db_dataset.get("non_fraud_count", 0) if db_dataset else 0,
            "fraud_percentage": db_dataset.get("fraud_percentage") if db_dataset else None,
            "completed_at": db_dataset.get("completed_at") if db_dataset else None,
            "file_path": db_dataset.get("file_path") if db_dataset else None,
            "error_message": db_dataset.get("error_message") if db_dataset else None
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get dataset", dataset_id=dataset_id, exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{dataset_id}/preprocess")
async def process_dataset(
    dataset_id: str,
    background_tasks: BackgroundTasks,
    request: DatasetProcessRequest = DatasetProcessRequest(),
    current_user: str = Depends(get_current_researcher)
):
    """
    Trigger dataset preprocessing.
    Processing happens in background to avoid timeout.
    """
    try:
        # Check if dataset exists in registry
        registry = get_dataset_registry()
        config = registry.get_dataset_config(dataset_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Dataset {dataset_id} not found in registry"
            )
        
        # Check if already processed
        status_check = dataset_service.check_dataset_status(dataset_id)
        if status_check['processed']:
            return {
                "message": "Dataset already processed",
                "dataset_id": dataset_id,
                "status": "completed",
                "file_path": status_check.get('file_path')
            }
        
        # Ensure dataset exists in Supabase
        db_dataset = supabase_db.get_dataset(dataset_id)
        if not db_dataset:
            # Create initial record with all required fields
            supabase_db.create_dataset({
                'id': dataset_id,
                'name': dataset_id,
                'description': config.get('description', ''),
                'source': config.get('source', 'kaggle'),
                'source_identifier': config.get('kaggle_dataset') or config.get('kaggle_competition'),
                'status': 'pending'
            })
        
        # Add processing to background tasks
        background_tasks.add_task(
            dataset_service.process_dataset,
            dataset_id
        )
        
        logger.info("Dataset processing queued", dataset_id=dataset_id)
        
        return {
            "message": "Dataset processing started",
            "dataset_id": dataset_id,
            "status": "processing",
            "note": "Processing may take 2-5 minutes. Check status with GET /datasets/{dataset_id}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start dataset processing",
                    dataset_id=dataset_id,
                    exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{dataset_id}/status")
async def get_dataset_status(
    dataset_id: str,
    current_user: str = Depends(get_current_researcher)
):
    """Check dataset processing status."""
    try:
        status_info = dataset_service.check_dataset_status(dataset_id)
        return status_info
    except Exception as e:
        logger.error("Failed to check dataset status",
                    dataset_id=dataset_id,
                    exc_info=e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
