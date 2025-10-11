"""
Dataset processing service - synchronous processing without Celery.
"""

import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import structlog

from app.core.config import settings
from app.utils.kaggle_client import KaggleClient
from app.utils.r2_storage import r2_storage_client
from app.utils.supabase_client import supabase_db
from app.datasets.loaders import get_loader
from app.datasets.registry import get_dataset_registry

logger = structlog.get_logger()


class DatasetProcessingService:
    """Service for processing datasets without Celery."""
    
    def __init__(self):
        self.kaggle_client = KaggleClient()
        self.registry = get_dataset_registry()
    
    def process_dataset(self, dataset_id: str) -> Dict[str, Any]:
        """
        Process a dataset: download, preprocess, split, upload to R2.
        
        Args:
            dataset_id: Dataset identifier
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        logger.info("Starting dataset processing", dataset_id=dataset_id)
        
        try:
            # 1. Get dataset configuration
            config = self.registry.get_dataset_config(dataset_id)
            if not config:
                raise ValueError(f"Dataset {dataset_id} not found in registry")
            
            # 2. Update status to processing
            supabase_db.update_dataset(dataset_id, {'status': 'processing'})
            
            # 3. Create temp directory
            temp_dir = Path(f"/tmp/{dataset_id}_{uuid.uuid4().hex[:8]}")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # 4. Download from Kaggle
                logger.info("Downloading dataset from Kaggle", dataset_id=dataset_id)
                download_result = self._download_dataset(dataset_id, config, temp_dir)
                
                # 5. Load and preprocess
                logger.info("Loading and preprocessing dataset", dataset_id=dataset_id)
                loader = get_loader(dataset_id, config, data_dir=temp_dir)
                raw_df = loader.load_raw_data()
                processed_df = loader.preprocess(raw_df)
                
                # 6. Split into train/val/test
                logger.info("Splitting dataset", dataset_id=dataset_id)
                train_df, val_df, test_df = loader.split(processed_df)
                
                # 7. Save to temp files
                logger.info("Saving processed files", dataset_id=dataset_id)
                train_path = temp_dir / "train.parquet"
                val_path = temp_dir / "val.parquet"
                test_path = temp_dir / "test.parquet"
                
                train_df.to_parquet(train_path, index=False)
                val_df.to_parquet(val_path, index=False)
                test_df.to_parquet(test_path, index=False)
                
                # 8. Upload to R2
                logger.info("Uploading to R2", dataset_id=dataset_id)
                r2_base_path = f"datasets/{dataset_id}/processed"
                
                if not r2_storage_client.is_available():
                    raise RuntimeError("R2 storage is not available. Check R2 credentials in environment variables.")
                
                upload_success = True
                upload_success &= r2_storage_client.upload_file(
                    str(train_path),
                    f"{r2_base_path}/train.parquet"
                )
                upload_success &= r2_storage_client.upload_file(
                    str(val_path),
                    f"{r2_base_path}/val.parquet"
                )
                upload_success &= r2_storage_client.upload_file(
                    str(test_path),
                    f"{r2_base_path}/test.parquet"
                )
                
                if not upload_success:
                    raise RuntimeError("Failed to upload one or more files to R2 storage")
                
                # 9. Calculate statistics
                target_col = config.get('target_column', 'target')
                fraud_count = 0
                non_fraud_count = 0
                fraud_percentage = None
                
                if target_col in processed_df.columns:
                    value_counts = processed_df[target_col].value_counts().to_dict()
                    # Assuming binary classification: 1 = fraud, 0 = non-fraud
                    fraud_count = int(value_counts.get(1, 0))
                    non_fraud_count = int(value_counts.get(0, 0))
                    total = fraud_count + non_fraud_count
                    if total > 0:
                        fraud_percentage = (fraud_count / total) * 100
                
                processing_time = time.time() - start_time
                
                # 10. Update Supabase with results
                update_data = {
                    'status': 'completed',
                    'file_path': r2_base_path,
                    'total_rows': len(processed_df),
                    'total_columns': len(processed_df.columns) - 1,  # Exclude target
                    'train_rows': len(train_df),
                    'val_rows': len(val_df),
                    'test_rows': len(test_df),
                    'fraud_count': fraud_count,
                    'non_fraud_count': non_fraud_count,
                    'fraud_percentage': fraud_percentage,
                    'feature_names': list(processed_df.columns),
                    'completed_at': pd.Timestamp.now().isoformat()
                }
                
                supabase_db.update_dataset(dataset_id, update_data)
                
                logger.info("Dataset processing complete",
                           dataset_id=dataset_id,
                           processing_time=processing_time)
                
                return {
                    'status': 'success',
                    'dataset_id': dataset_id,
                    'total_rows': len(processed_df),
                    'total_columns': len(processed_df.columns) - 1,
                    'train_rows': len(train_df),
                    'val_rows': len(val_df),
                    'test_rows': len(test_df),
                    'fraud_count': fraud_count,
                    'non_fraud_count': non_fraud_count,
                    'fraud_percentage': fraud_percentage,
                    'file_path': r2_base_path
                }
                
            finally:
                # Cleanup temp directory
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    logger.debug("Temp directory cleaned up", path=str(temp_dir))
        
        except Exception as e:
            logger.error("Dataset processing failed",
                        dataset_id=dataset_id,
                        exc_info=e)
            
            # Update status to failed
            supabase_db.update_dataset(dataset_id, {
                'status': 'failed',
                'error_message': str(e)
            })
            
            return {
                'status': 'error',
                'dataset_id': dataset_id,
                'error': str(e)
            }
    
    def _download_dataset(self, dataset_id: str, config: Dict, temp_dir: Path) -> Dict[str, Any]:
        """Download dataset from Kaggle."""
        source = config.get('source', 'kaggle')
        
        if source != 'kaggle':
            raise ValueError(f"Unsupported source: {source}")
        
        # Check if it's a competition or dataset
        if 'kaggle_competition' in config:
            competition = config['kaggle_competition']
            logger.info("Downloading Kaggle competition", competition=competition)
            result = self.kaggle_client.download_competition(
                competition_name=competition,
                output_dir=str(temp_dir)
            )
        elif 'kaggle_dataset' in config:
            dataset = config['kaggle_dataset']
            logger.info("Downloading Kaggle dataset", dataset=dataset)
            result = self.kaggle_client.download_dataset(
                dataset_name=dataset,
                output_dir=str(temp_dir)
            )
        else:
            raise ValueError("No Kaggle source specified in config")
        
        if result.get('status') != 'success':
            raise RuntimeError(f"Kaggle download failed: {result.get('error')}")
        
        return result
    
    def check_dataset_status(self, dataset_id: str) -> Dict[str, Any]:
        """Check if dataset is processed and ready."""
        # Check Supabase
        dataset = supabase_db.get_dataset(dataset_id)
        
        if not dataset:
            return {
                'processed': False,
                'status': 'not_found',
                'message': 'Dataset not found in database'
            }
        
        if dataset['status'] == 'completed':
            # Verify files exist
            file_path = dataset.get('file_path')
            if file_path:
                # For now, assume files exist if file_path is set
                # TODO: Add actual file existence check if needed
                return {
                    'processed': True,
                    'status': 'completed',
                    'file_path': file_path,
                    'total_samples': dataset.get('total_rows', 0),
                    'num_features': dataset.get('total_columns', 0)
                }
        
        return {
            'processed': False,
            'status': dataset['status'],
            'message': f"Dataset status: {dataset['status']}"
        }


# Global service instance
dataset_service = DatasetProcessingService()
