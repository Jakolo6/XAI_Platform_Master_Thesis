"""
Celery tasks for dataset processing.
"""

from datetime import datetime, timedelta
from typing import Dict, Any
import structlog

from workers import celery_app
from app.utils.kaggle_client import KaggleClient
from app.utils.preprocessing import DataPreprocessor
from app.core.config import settings

logger = structlog.get_logger()


@celery_app.task(bind=True, name="app.tasks.dataset_tasks.download_ieee_cis_dataset")
def download_ieee_cis_dataset(self, dataset_id: str, output_dir: str) -> Dict[str, Any]:
    """
    Download IEEE-CIS fraud detection dataset from Kaggle.
    
    Args:
        dataset_id: Dataset ID in database
        output_dir: Directory to save downloaded files
        
    Returns:
        Dictionary with download results
    """
    logger.info("Starting IEEE-CIS dataset download",
               dataset_id=dataset_id,
               output_dir=output_dir,
               task_id=self.request.id)
    
    try:
        # Initialize Kaggle client
        kaggle_client = KaggleClient()
        
        # Verify credentials
        if not kaggle_client.verify_credentials():
            raise ValueError("Invalid Kaggle API credentials")
        
        # Download dataset
        result = kaggle_client.download_ieee_cis_dataset(output_dir)
        
        if result['status'] == 'error':
            raise Exception(result.get('message', 'Download failed'))
        
        logger.info("IEEE-CIS dataset download complete",
                   dataset_id=dataset_id,
                   task_id=self.request.id)
        
        return {
            'status': 'success',
            'dataset_id': dataset_id,
            'transaction_file': result['transaction_file'],
            'identity_file': result['identity_file'],
            'task_id': self.request.id,
        }
        
    except Exception as e:
        logger.error("Dataset download failed",
                    dataset_id=dataset_id,
                    task_id=self.request.id,
                    exc_info=e)
        
        return {
            'status': 'error',
            'dataset_id': dataset_id,
            'error': str(e),
            'task_id': self.request.id,
        }


@celery_app.task(bind=True, name="app.tasks.dataset_tasks.preprocess_dataset")
def preprocess_dataset(
    self,
    dataset_id: str,
    transaction_path: str,
    identity_path: str,
    output_dir: str,
    apply_sampling: bool = True
) -> Dict[str, Any]:
    """
    Preprocess IEEE-CIS dataset.
    
    Args:
        dataset_id: Dataset ID in database
        transaction_path: Path to transaction CSV
        identity_path: Path to identity CSV
        output_dir: Directory to save processed data
        apply_sampling: Whether to apply balanced sampling
        
    Returns:
        Dictionary with preprocessing results
    """
    logger.info("Starting dataset preprocessing",
               dataset_id=dataset_id,
               task_id=self.request.id)
    
    try:
        # Initialize preprocessor
        preprocessor = DataPreprocessor(
            max_size_mb=settings.MAX_DATASET_SIZE_MB,
            sample_size=settings.DEFAULT_SAMPLE_SIZE
        )
        
        # Run preprocessing pipeline
        result = preprocessor.preprocess_pipeline(
            transaction_path=transaction_path,
            identity_path=identity_path,
            output_dir=output_dir,
            apply_sampling=apply_sampling
        )
        
        logger.info("Dataset preprocessing complete",
                   dataset_id=dataset_id,
                   task_id=self.request.id,
                   train_size=result['train_size'],
                   val_size=result['val_size'],
                   test_size=result['test_size'])
        
        # Convert numpy types to Python native types for JSON serialization
        serializable_result = {
            'train_size': int(result['train_size']),
            'val_size': int(result['val_size']),
            'test_size': int(result['test_size']),
            'output_dir': result['output_dir'],
            'status': result['status']
        }
        
        return {
            'status': 'success',
            'dataset_id': dataset_id,
            'result': serializable_result,
            'task_id': self.request.id,
        }
        
    except Exception as e:
        logger.error("Dataset preprocessing failed",
                    dataset_id=dataset_id,
                    task_id=self.request.id,
                    exc_info=e)
        
        return {
            'status': 'error',
            'dataset_id': dataset_id,
            'error': str(e),
            'task_id': self.request.id,
        }


@celery_app.task(name="app.tasks.dataset_tasks.cleanup_expired_sessions")
def cleanup_expired_sessions() -> Dict[str, Any]:
    """
    Cleanup expired study sessions (scheduled task).
    
    Returns:
        Dictionary with cleanup results
    """
    logger.info("Starting cleanup of expired study sessions")
    
    try:
        # TODO: Implement database cleanup logic
        # This will be implemented when we add the database service layer
        
        logger.info("Expired sessions cleanup complete")
        
        return {
            'status': 'success',
            'message': 'Expired sessions cleaned up',
            'cleaned_count': 0,  # Placeholder
        }
        
    except Exception as e:
        logger.error("Session cleanup failed", exc_info=e)
        
        return {
            'status': 'error',
            'error': str(e),
        }


@celery_app.task(bind=True, name="app.tasks.dataset_tasks.calculate_dataset_statistics")
def calculate_dataset_statistics(
    self,
    dataset_id: str,
    file_path: str
) -> Dict[str, Any]:
    """
    Calculate statistics for a dataset.
    
    Args:
        dataset_id: Dataset ID in database
        file_path: Path to dataset file
        
    Returns:
        Dictionary with statistics
    """
    logger.info("Calculating dataset statistics",
               dataset_id=dataset_id,
               task_id=self.request.id)
    
    try:
        import pandas as pd
        
        # Load dataset
        df = pd.read_csv(file_path)
        
        # Initialize preprocessor for statistics calculation
        preprocessor = DataPreprocessor()
        
        # Calculate statistics
        stats = preprocessor.get_dataset_statistics(df)
        
        logger.info("Dataset statistics calculated",
                   dataset_id=dataset_id,
                   task_id=self.request.id)
        
        return {
            'status': 'success',
            'dataset_id': dataset_id,
            'statistics': stats,
            'task_id': self.request.id,
        }
        
    except Exception as e:
        logger.error("Statistics calculation failed",
                    dataset_id=dataset_id,
                    task_id=self.request.id,
                    exc_info=e)
        
        return {
            'status': 'error',
            'dataset_id': dataset_id,
            'error': str(e),
            'task_id': self.request.id,
        }
