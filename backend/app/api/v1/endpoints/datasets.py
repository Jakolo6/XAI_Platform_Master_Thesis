"""
Dataset management endpoints.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import structlog

from app.core.database import get_db
from app.api.dependencies import get_current_researcher
from app.models.dataset import Dataset, DatasetStatus
from app.tasks.dataset_tasks import (
    download_ieee_cis_dataset,
    preprocess_dataset,
    calculate_dataset_statistics
)

logger = structlog.get_logger()
router = APIRouter()


class DatasetCreate(BaseModel):
    """Dataset creation schema."""
    name: str
    description: str = ""
    source: str = "upload"


class DatasetResponse(BaseModel):
    """Dataset response schema."""
    id: str
    name: str
    description: str
    source: str
    status: str
    total_rows: int = None
    total_columns: int = None
    created_at: str
    processed_at: str = None


@router.get("/", response_model=List[DatasetResponse])
async def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    List all datasets.
    """
    result = await db.execute(
        select(Dataset)
        .offset(skip)
        .limit(limit)
        .order_by(Dataset.created_at.desc())
    )
    datasets = result.scalars().all()
    
    return [
        DatasetResponse(
            id=str(dataset.id),
            name=dataset.name,
            description=dataset.description,
            source=dataset.source,
            status=dataset.status,
            total_rows=dataset.total_rows,
            total_columns=dataset.total_columns,
            created_at=dataset.created_at.isoformat(),
            processed_at=dataset.processed_at.isoformat() if dataset.processed_at else None
        )
        for dataset in datasets
    ]


@router.post("/", response_model=DatasetResponse)
async def create_dataset(
    dataset_data: DatasetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    Create a new dataset entry.
    """
    import uuid
    new_dataset = Dataset(
        id=str(uuid.uuid4()),
        name=dataset_data.name,
        description=dataset_data.description,
        source=dataset_data.source,
        status=DatasetStatus.PENDING
    )
    
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    
    logger.info("Dataset created", dataset_id=str(new_dataset.id), name=dataset_data.name)
    
    return DatasetResponse(
        id=str(new_dataset.id),
        name=new_dataset.name,
        description=new_dataset.description,
        source=new_dataset.source,
        status=new_dataset.status,
        created_at=new_dataset.created_at.isoformat()
    )


@router.get("/{dataset_id}", response_model=Dict[str, Any])
async def get_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    Get dataset details.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "source": dataset.source,
        "source_identifier": dataset.source_identifier,
        "status": dataset.status.value,
        "file_path": dataset.file_path,
        "file_size_mb": dataset.file_size_mb,
        "total_rows": dataset.total_rows,
        "total_columns": dataset.total_columns,
        "train_rows": dataset.train_rows,
        "val_rows": dataset.val_rows,
        "test_rows": dataset.test_rows,
        "fraud_count": dataset.fraud_count,
        "non_fraud_count": dataset.non_fraud_count,
        "fraud_percentage": dataset.fraud_percentage,
        "preprocessing_config": dataset.preprocessing_config,
        "feature_names": dataset.feature_names,
        "statistics": dataset.statistics,
        "error_message": dataset.error_message,
        "created_at": dataset.created_at.isoformat(),
        "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
        "completed_at": dataset.completed_at.isoformat() if dataset.completed_at else None
    }


@router.post("/{dataset_id}/preprocess")
async def trigger_preprocessing(
    dataset_id: str,
    apply_sampling: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    Trigger dataset preprocessing.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Update status to processing
    dataset.status = DatasetStatus.PROCESSING
    await db.commit()
    
    # Queue preprocessing task
    task = preprocess_dataset.delay(
        dataset_id=str(dataset.id),
        transaction_path=f"data/raw/train_transaction.csv",
        identity_path=f"data/raw/train_identity.csv",
        output_dir=f"data/processed/{dataset.id}",
        apply_sampling=apply_sampling
    )
    
    logger.info("Preprocessing task queued",
               dataset_id=dataset_id,
               task_id=task.id)
    
    return {
        "message": "Preprocessing started",
        "dataset_id": dataset_id,
        "task_id": task.id,
        "status": "processing"
    }


@router.post("/download-ieee-cis")
async def download_ieee_cis(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    Download IEEE-CIS fraud detection dataset from Kaggle.
    """
    # Create dataset entry
    import uuid
    new_dataset = Dataset(
        id=str(uuid.uuid4()),
        name="IEEE-CIS Fraud Detection",
        description="IEEE-CIS Fraud Detection dataset from Kaggle",
        source="kaggle",
        status=DatasetStatus.DOWNLOADING
    )
    
    db.add(new_dataset)
    await db.commit()
    await db.refresh(new_dataset)
    
    # Queue download task
    task = download_ieee_cis_dataset.delay(
        dataset_id=str(new_dataset.id),
        output_dir="data/raw"
    )
    
    logger.info("IEEE-CIS download task queued",
               dataset_id=str(new_dataset.id),
               task_id=task.id)
    
    return {
        "message": "Download started",
        "dataset_id": str(new_dataset.id),
        "task_id": task.id,
        "status": "downloading"
    }


@router.get("/{dataset_id}/statistics")
async def get_dataset_statistics(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    Get dataset statistics.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return {
        "dataset_id": dataset_id,
        "statistics": dataset.statistics,
        "total_rows": dataset.total_rows,
        "total_columns": dataset.total_columns,
        "fraud_percentage": dataset.fraud_percentage
    }


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_researcher)
):
    """
    Delete a dataset.
    """
    result = await db.execute(
        select(Dataset).where(Dataset.id == dataset_id)
    )
    dataset = result.scalar_one_or_none()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    await db.delete(dataset)
    await db.commit()
    
    logger.info("Dataset deleted", dataset_id=dataset_id)
    
    return {
        "message": "Dataset deleted successfully",
        "dataset_id": dataset_id
    }
