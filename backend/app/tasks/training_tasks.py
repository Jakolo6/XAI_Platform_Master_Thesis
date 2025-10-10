"""
Celery tasks for model training.
"""

from typing import Dict, Any, Optional
import pandas as pd
import structlog
import asyncio
from pathlib import Path

from workers import celery_app
from app.utils.training import ModelTrainer
from app.utils.storage import storage_client
from app.core.config import settings

logger = structlog.get_logger()


@celery_app.task(bind=True, name="app.tasks.training_tasks.train_model")
def train_model(
    self,
    model_id: str,
    dataset_id: str,
    model_type: str,
    hyperparameters: Optional[Dict[str, Any]] = None,
    optimize: bool = False
) -> Dict[str, Any]:
    """
    Train a machine learning model.
    
    Args:
        model_id: Model ID in database
        dataset_id: Dataset ID to use for training
        model_type: Type of model (e.g., 'xgboost', 'random_forest')
        hyperparameters: Model hyperparameters
        optimize: Whether to run hyperparameter optimization
        
    Returns:
        Dictionary with training results
    """
    logger.info("Starting model training",
               model_id=model_id,
               model_type=model_type,
               task_id=self.request.id)
    
    try:
        # Update model status to training
        # Note: Using sync database operations to avoid event loop conflicts in Celery
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.models.model import Model, ModelStatus, ModelMetrics
        import uuid
        
        # Create sync engine for Celery tasks
        sync_engine = create_engine(settings.DATABASE_URL.replace('+asyncpg', ''))
        SyncSession = sessionmaker(bind=sync_engine)
        
        def update_status_sync(status: ModelStatus, error_msg: Optional[str] = None):
            with SyncSession() as db:
                model = db.query(Model).filter(Model.id == model_id).first()
                if model:
                    model.status = status
                    if error_msg:
                        model.error_message = error_msg
                    db.commit()
        
        update_status_sync(ModelStatus.TRAINING)
        
        # Load dataset using dataset loader
        from app.datasets.registry import get_dataset_registry
        from app.datasets.loaders import get_loader
        
        # Get dataset configuration
        registry = get_dataset_registry()
        dataset_config = registry.get_dataset_config(dataset_id)
        
        if not dataset_config:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        # Get loader and load splits
        loader = get_loader(dataset_id, dataset_config)
        
        if not loader.splits_exist():
            raise ValueError(f"Dataset splits not found. Run: python scripts/process_dataset.py {dataset_id}")
        
        train_df, val_df, test_df = loader.load_splits()
        
        # Get target column from config
        target_col = loader.get_target_column()
        
        # Separate features and target
        X_train = train_df.drop(columns=[target_col])
        y_train = train_df[target_col]
        X_val = val_df.drop(columns=[target_col])
        y_val = val_df[target_col]
        X_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]
        
        logger.info("Dataset loaded",
                   train_size=len(X_train),
                   val_size=len(X_val),
                   test_size=len(X_test))
        
        # Initialize trainer
        trainer = ModelTrainer(model_type, hyperparameters)
        
        # Optimize hyperparameters if requested
        optimization_results = None
        if optimize:
            logger.info("Running hyperparameter optimization")
            optimization_results = trainer.optimize_hyperparameters(
                X_train, y_train, X_val, y_val
            )
        
        # Train model
        training_results = trainer.train(X_train, y_train, X_val, y_val)
        
        # Evaluate model
        metrics = trainer.evaluate(X_test, y_test)
        
        # Save model locally
        model_dir = Path(f"data/models/{model_id}")
        model_dir.mkdir(parents=True, exist_ok=True)
        model_path = str(model_dir / "model.pkl")
        model_hash = trainer.save_model(model_path)
        
        # Upload to Supabase (if configured)
        storage_path = f"{model_id}/model.pkl"
        storage_client.upload_file(
            bucket=settings.STORAGE_BUCKET_MODELS,
            file_path=model_path,
            destination_path=storage_path,
            content_type="application/octet-stream"
        )
        
        # Get model file size
        model_size_mb = Path(model_path).stat().st_size / (1024 * 1024)
        
        # Update database (PostgreSQL)
        def save_results_sync():
            with SyncSession() as db:
                # Update model
                model = db.query(Model).filter(Model.id == model_id).first()
                
                if model:
                    model.status = ModelStatus.COMPLETED
                    model.model_path = storage_path
                    model.model_hash = model_hash
                    model.model_size_mb = model_size_mb
                    model.training_time_seconds = training_results["training_time_seconds"]
                    model.hyperparameters = trainer.hyperparameters
                    
                    if optimization_results:
                        model.training_config = {
                            "optimized": True,
                            "optimization_results": optimization_results
                        }
                    
                    # Save metrics
                    model_metrics = ModelMetrics(
                        id=str(uuid.uuid4()),
                        model_id=model_id,
                        **metrics
                    )
                    db.add(model_metrics)
                    db.commit()
        
        save_results_sync()
        
        # Also save to Supabase
        try:
            from app.supabase.client import get_supabase_client
            supabase = get_supabase_client()
            
            # Insert model
            supabase.insert_model({
                'id': model_id,
                'name': f"{model_type}_{dataset_id}",
                'model_type': model_type,
                'version': '1.0.0',
                'dataset_id': dataset_id,
                'hyperparameters': trainer.hyperparameters,
                'training_config': {
                    'optimized': optimize,
                    'optimization_results': optimization_results
                } if optimization_results else None,
                'model_path': storage_path,
                'model_hash': model_hash,
                'model_size_mb': model_size_mb,
                'training_time_seconds': training_results["training_time_seconds"],
                'status': 'completed',
            })
            
            # Insert metrics
            supabase.insert_model_metrics({
                'model_id': model_id,
                **metrics
            })
            
            logger.info("Results saved to Supabase", model_id=model_id)
        except Exception as e:
            logger.warning("Failed to save to Supabase", error=str(e))
        
        logger.info("Model training complete",
                   model_id=model_id,
                   model_type=model_type,
                   auc_roc=metrics["auc_roc"],
                   task_id=self.request.id)
        
        return {
            'status': 'success',
            'model_id': model_id,
            'model_type': model_type,
            'metrics': metrics,
            'training_time_seconds': training_results["training_time_seconds"],
            'task_id': self.request.id,
        }
        
    except Exception as e:
        logger.error("Model training failed",
                    model_id=model_id,
                    task_id=self.request.id,
                    exc_info=e)
        
        # Update model status to failed
        try:
            update_status_sync(ModelStatus.FAILED, str(e))
        except:
            pass
        
        return {
            'status': 'error',
            'model_id': model_id,
            'error': str(e),
            'task_id': self.request.id,
        }
