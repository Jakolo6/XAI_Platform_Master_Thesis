"""
API endpoints for Home Credit dataset management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import structlog

from app.services.kaggle_service import kaggle_service
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


@router.post("/download")
async def download_home_credit_dataset(background_tasks: BackgroundTasks):
    """
    Download Home Credit dataset from Kaggle.
    Requires KAGGLE_USERNAME and KAGGLE_KEY in environment.
    """
    try:
        logger.info("API: Downloading Home Credit dataset")
        
        # Run download
        result = kaggle_service.download_dataset()
        
        return {
            "status": "success",
            "message": "Dataset download initiated",
            "details": result
        }
        
    except Exception as e:
        logger.error("Failed to download dataset", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download dataset: {str(e)}"
        )


@router.post("/preprocess")
async def preprocess_home_credit_dataset():
    """
    Preprocess Home Credit dataset:
    - Check if files exist, download if not
    - Handle missing values
    - Encode categorical variables
    - Scale features
    - Train/val/test split
    - Generate EDA statistics
    """
    try:
        logger.info("API: Preprocessing Home Credit dataset")
        
        # Check if dataset files exist, download if not
        from pathlib import Path
        data_dir = Path("data/raw/home_credit")
        train_file = data_dir / "application_train.csv"
        
        if not train_file.exists():
            logger.info("Dataset files not found, downloading first...")
            kaggle_service.download_dataset()
        
        result = kaggle_service.load_and_preprocess()
        
        # Save metadata to Supabase
        dataset_metadata = {
            "dataset_id": result["dataset_id"],
            "name": "Home Credit Default Risk",
            "source": "Kaggle",
            "n_samples": result["n_samples"],
            "n_features": result["n_features"],
            "train_size": result["train_size"],
            "val_size": result["val_size"],
            "test_size": result["test_size"],
            "target_distribution": result["target_distribution"],
            "status": "processed",
            "eda_stats": result["eda_stats"]
        }
        
        # Insert or update in Supabase
        try:
            supabase_db.table('datasets').upsert(dataset_metadata).execute()
        except Exception as db_error:
            logger.warning("Failed to save to Supabase", error=str(db_error))
            # Continue even if Supabase fails
        
        logger.info("Dataset preprocessed and saved")
        
        return result
        
    except Exception as e:
        logger.error("Failed to preprocess dataset", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preprocess dataset: {str(e)}"
        )


@router.get("/eda/{dataset_id}")
async def get_eda_statistics(dataset_id: str):
    """
    Get EDA statistics for visualization.
    """
    try:
        logger.info("API: Getting EDA stats", dataset_id=dataset_id)
        
        # Get from Supabase
        try:
            result = supabase_db.table('datasets').select('*').eq('dataset_id', dataset_id).execute()
            
            if result.data and len(result.data) > 0:
                dataset = result.data[0]
                
                return {
                    "dataset_id": dataset_id,
                    "eda_stats": dataset.get("eda_stats", {}),
                    "target_distribution": dataset.get("target_distribution", {}),
                    "n_samples": dataset.get("n_samples", 0),
                    "n_features": dataset.get("n_features", 0)
                }
        except Exception as db_error:
            logger.warning("Failed to get from Supabase", error=str(db_error))
        
        # If not in Supabase, return 404
        raise HTTPException(status_code=404, detail="Dataset not found. Please preprocess the dataset first.")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get EDA stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get EDA statistics: {str(e)}"
        )
