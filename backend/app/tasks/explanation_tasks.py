"""
Celery tasks for XAI explanation generation.
"""

from typing import Dict, Any
import structlog
import pandas as pd
import json
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from workers import celery_app
from app.core.config import settings
from app.utils.explainers import ShapExplainer

logger = structlog.get_logger()

# Lazy initialization of sync engine
_sync_engine = None
_SyncSession = None

def get_sync_session():
    """Get or create sync session for Celery tasks."""
    global _sync_engine, _SyncSession
    if _sync_engine is None:
        # Replace asyncpg with psycopg2
        sync_db_url = settings.DATABASE_URL.replace('+asyncpg', '').replace('postgresql://', 'postgresql+psycopg2://')
        _sync_engine = create_engine(sync_db_url)
        _SyncSession = sessionmaker(bind=_sync_engine)
    return _SyncSession()


@celery_app.task(bind=True, name="app.tasks.explanation_tasks.generate_explanation")
def generate_explanation(
    self,
    explanation_id: str,
    model_id: str,
    method: str,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate XAI explanation for a model.
    
    Args:
        explanation_id: Explanation ID in database
        model_id: Model ID to explain
        method: XAI method (e.g., 'shap_tree', 'lime')
        config: Method configuration
        
    Returns:
        Dictionary with explanation results
    """
    logger.info("Starting explanation generation",
               explanation_id=explanation_id,
               method=method,
               task_id=self.request.id)
    
    try:
        from app.models.model import Model
        import redis
        
        # Connect to Redis
        redis_client = redis.Redis(host='redis', port=6379, db=2, decode_responses=True)
        
        # Update status in Redis
        data = redis_client.get(f"explanation:{explanation_id}")
        if data:
            explanation_data = json.loads(data)
            explanation_data["status"] = "processing"
            redis_client.setex(
                f"explanation:{explanation_id}",
                3600,
                json.dumps(explanation_data)
            )
        
        # Get model from database
        db = get_sync_session()
        model = db.query(Model).filter(Model.id == model_id).first()
        if not model:
            db.close()
            raise ValueError(f"Model {model_id} not found")
        
        dataset_id = model.dataset_id
        db.close()
        
        # Load model file
        model_path = Path(f"data/models/{model_id}/model.pkl")
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        # Load background data (sample from validation set)
        dataset_id = model.dataset_id
        val_data_path = Path(f"data/processed/{dataset_id}/validation.csv")
        
        if not val_data_path.exists():
            raise FileNotFoundError(f"Validation data not found: {val_data_path}")
        
        # Load validation data
        val_df = pd.read_csv(val_data_path)
        
        # Separate features and target
        if 'isFraud' in val_df.columns:
            X_val = val_df.drop('isFraud', axis=1)
        else:
            X_val = val_df
        
        # Sample background data (100 samples for efficiency)
        background_data = X_val.sample(min(100, len(X_val)), random_state=42)
        
        # Initialize SHAP explainer
        explainer = ShapExplainer(str(model_path), model.model_type)
        explainer.initialize_explainer(background_data)
        
        # Get instance to explain from config
        instance_data = config.get('instance_data')
        if instance_data:
            # Explain single instance
            instance_df = pd.DataFrame([instance_data])
            explanation_result = explainer.explain_instance(instance_df)
        else:
            # Generate global feature importance
            sample_data = X_val.sample(min(1000, len(X_val)), random_state=42)
            explanation_result = explainer.get_global_feature_importance(sample_data)
        
        # Save explanation results to Redis
        data = redis_client.get(f"explanation:{explanation_id}")
        if data:
            explanation_data = json.loads(data)
            explanation_data["status"] = "completed"
            explanation_data["result"] = json.dumps(explanation_result)
            redis_client.setex(
                f"explanation:{explanation_id}",
                3600,
                json.dumps(explanation_data)
            )
        
        logger.info("Explanation generation complete",
                   explanation_id=explanation_id,
                   task_id=self.request.id)
        
        return {
            'status': 'success',
            'explanation_id': explanation_id,
            'result': explanation_result,
            'task_id': self.request.id,
        }
        
    except Exception as e:
        logger.error("Explanation generation failed",
                    explanation_id=explanation_id,
                    task_id=self.request.id,
                    exc_info=e)
        
        return {
            'status': 'error',
            'explanation_id': explanation_id,
            'error': str(e),
            'task_id': self.request.id,
        }


@celery_app.task(name="app.tasks.explanation_tasks.cleanup_cache")
def cleanup_cache() -> Dict[str, Any]:
    """
    Cleanup old explanation cache (scheduled task).
    
    Returns:
        Dictionary with cleanup results
    """
    logger.info("Starting explanation cache cleanup")
    
    try:
        # TODO: Implement cache cleanup logic
        
        logger.info("Explanation cache cleanup complete")
        
        return {
            'status': 'success',
            'message': 'Cache cleaned up',
            'cleaned_count': 0,  # Placeholder
        }
        
    except Exception as e:
        logger.error("Cache cleanup failed", exc_info=e)
        
        return {
            'status': 'error',
            'error': str(e),
        }
