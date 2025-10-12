"""
API endpoints for Home Credit dataset management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import structlog

from app.services.kaggle_service import kaggle_service
from app.services.r2_service import r2_service
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


@router.get("/status")
async def get_dataset_status():
    """
    Check dataset status in R2 and Supabase.
    """
    try:
        # Check if files exist in R2
        files_in_r2 = False
        r2_configured = r2_service.is_configured()
        logger.info("Checking R2 status", r2_configured=r2_configured)
        
        if r2_configured:
            files_in_r2 = r2_service.file_exists("home-credit/raw/application_train.csv")
            logger.info("R2 file check result", files_in_r2=files_in_r2)
        else:
            logger.warning("R2 not configured!")
            files_in_r2 = False
        
        # Check if processed in Supabase
        processed_in_supabase = False
        try:
            if supabase_db.is_available():
                result = supabase_db.client.table('datasets').select('id').eq('id', 'home-credit-default-risk').execute()
                processed_in_supabase = result.data and len(result.data) > 0
                logger.info("Supabase check result", processed_in_supabase=processed_in_supabase)
        except Exception as e:
            logger.warning("Supabase check failed", error=str(e))
        
        status_response = {
            "files_in_r2": files_in_r2,
            "processed_in_supabase": processed_in_supabase,
            "needs_download": not files_in_r2,
            "needs_preprocessing": files_in_r2 and not processed_in_supabase,
            "ready": processed_in_supabase
        }
        
        logger.info("Status response", status=status_response)
        return status_response
        
    except Exception as e:
        logger.error("Failed to check status", error=str(e))
        return {
            "files_in_r2": False,
            "processed_in_supabase": False,
            "needs_download": True,
            "needs_preprocessing": False,
            "ready": False
        }


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
        
        # Check if dataset files exist locally or in R2
        from pathlib import Path
        from app.services.r2_service import r2_service
        
        data_dir = Path("data/raw/home_credit")
        train_file = data_dir / "application_train.csv"
        
        # Priority: Local > R2 > Kaggle
        if not train_file.exists():
            logger.info("Dataset files not found locally, checking R2...")
            
            # Try to download from R2 first (much faster!)
            if r2_service.is_configured() and r2_service.file_exists("home-credit/raw/application_train.csv"):
                logger.info("Dataset found in R2, downloading from there (fast!)")
                # Files will be downloaded by load_and_preprocess when needed
            else:
                logger.info("Dataset not in R2, downloading from Kaggle (first time only)...")
                kaggle_service.download_dataset()
        
        result = kaggle_service.load_and_preprocess()
        
        # Save metadata to Supabase (matching schema columns)
        from datetime import datetime
        
        dataset_metadata = {
            "id": result["dataset_id"],  # Primary key
            "name": "Home Credit Default Risk",
            "description": "Kaggle Home Credit Default Risk Competition Dataset",
            "source": "Kaggle",
            "source_identifier": "home-credit-default-risk",
            "status": "completed",
            "file_path": "home-credit/processed",  # R2 path
            "total_rows": result["n_samples"],
            "total_columns": result["n_features"],
            "train_rows": result["train_size"],
            "val_rows": result["val_size"],
            "test_rows": result["test_size"],
            "fraud_count": result["target_distribution"]["class_1"],
            "non_fraud_count": result["target_distribution"]["class_0"],
            "fraud_percentage": (result["target_distribution"]["class_1"] / result["n_samples"]) * 100,
            "statistics": result["eda_stats"],  # Store EDA stats in statistics column
            "completed_at": datetime.utcnow().isoformat()
        }
        
        # Insert or update in Supabase
        logger.info("Saving to Supabase", dataset_id=result["dataset_id"])
        try:
            if supabase_db.is_available():
                response = supabase_db.client.table('datasets').upsert(dataset_metadata, on_conflict="id").execute()
                logger.info("Successfully saved to Supabase!", response=response)
            else:
                logger.warning("Supabase not available, skipping save")
        except Exception as db_error:
            logger.error("FAILED to save to Supabase!", error=str(db_error), error_type=type(db_error).__name__)
            # Re-raise so we know it failed
            raise HTTPException(
                status_code=500,
                detail=f"Preprocessing succeeded but failed to save to Supabase: {str(db_error)}"
            )
        
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
            if supabase_db.is_available():
                result = supabase_db.client.table('datasets').select('*').eq('id', dataset_id).execute()
                
                if result.data and len(result.data) > 0:
                    dataset = result.data[0]
                
                return {
                    "dataset_id": dataset_id,
                    "eda_stats": dataset.get("statistics", {}),  # EDA stats stored in statistics column
                    "target_distribution": {
                        "class_0": dataset.get("non_fraud_count", 0),
                        "class_1": dataset.get("fraud_count", 0)
                    },
                    "n_samples": dataset.get("total_rows", 0),
                    "n_features": dataset.get("total_columns", 0),
                    "train_size": dataset.get("train_rows", 0),
                    "val_size": dataset.get("val_rows", 0),
                    "test_size": dataset.get("test_rows", 0)
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
