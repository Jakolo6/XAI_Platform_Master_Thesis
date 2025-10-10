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
        
        # Load background data using dataset loader
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
            raise ValueError(f"Dataset splits not found for {dataset_id}")
        
        train_df, val_df, test_df = loader.load_splits()
        
        # Get target column from config
        target_col = loader.get_target_column()
        
        # Separate features and target
        X_val = val_df.drop(columns=[target_col])
        y_val = val_df[target_col]
        
        # Sample background data (100 samples for efficiency)
        background_data = X_val.sample(min(100, len(X_val)), random_state=42)
        
        # Route to appropriate explainer based on method
        if method == 'shap':
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
        
        elif method == 'lime':
            # Initialize LIME explainer
            from app.utils.explainers.lime_explainer import LimeExplainer
            
            # Load the actual model for LIME (needs predict_proba)
            import pickle
            with open(model_path, 'rb') as f:
                loaded_model = pickle.load(f)
            
            logger.info("Model loaded successfully for LIME", model_path=str(model_path))
            
            explainer = LimeExplainer(
                model=loaded_model,
                feature_names=X_val.columns.tolist(),
                training_data=background_data
            )
            
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
        
        else:
            raise ValueError(f"Unsupported explanation method: {method}")
        
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
        
        # Also save to Supabase
        try:
            from app.supabase.client import get_supabase_client
            supabase = get_supabase_client()
            
            # Get dataset UUID from Supabase
            datasets = supabase.get_datasets(is_active=False)
            supabase_dataset = next((d for d in datasets if d['name'] == dataset_id), None)
            dataset_uuid = supabase_dataset['id'] if supabase_dataset else None
            
            # Extract summary data
            feature_importance = explanation_result.get('feature_importance', [])
            top_features = feature_importance[:10] if feature_importance else []
            
            # Save explanation to Supabase
            supabase.insert_explanation({
                'id': explanation_id,
                'model_id': model_id,
                'dataset_id': dataset_uuid,
                'method': method,
                'type': 'global' if not config.get('instance_data') else 'local',
                'summary_json': explanation_result,
                'top_features': top_features,
                'feature_importance': {f['feature']: f['importance'] for f in feature_importance} if feature_importance else {},
                'num_samples': len(X_val),
                'num_features': len(X_val.columns)
            })
            
            logger.info("Explanation saved to Supabase", explanation_id=explanation_id)
        except Exception as e:
            logger.warning("Failed to save explanation to Supabase", error=str(e))
        
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


@celery_app.task(bind=True, name="app.tasks.explanation_tasks.evaluate_explanation_quality_task")
def evaluate_explanation_quality_task(self, eval_id: str, explanation_id: str) -> Dict[str, Any]:
    """
    Evaluate explanation quality using Quantus metrics.
    
    Args:
        eval_id: Quality evaluation ID
        explanation_id: Explanation ID to evaluate
        
    Returns:
        Dictionary with evaluation results
    """
    import redis
    import pickle
    import numpy as np
    from pathlib import Path
    from app.utils.metrics.quantus_metrics import QuantusEvaluator
    
    logger.info("Starting quality evaluation",
               eval_id=eval_id,
               explanation_id=explanation_id,
               task_id=self.request.id)
    
    try:
        # Connect to Redis
        redis_client = redis.Redis(host='redis', port=6379, db=2, decode_responses=True)
        
        # Update status
        eval_data = redis_client.get(f"quality_eval:{eval_id}")
        if eval_data:
            eval_info = json.loads(eval_data)
            eval_info["status"] = "processing"
            redis_client.setex(f"quality_eval:{eval_id}", 3600, json.dumps(eval_info))
        
        # Get explanation data
        exp_data = redis_client.get(f"explanation:{explanation_id}")
        if not exp_data:
            raise ValueError(f"Explanation {explanation_id} not found")
        
        explanation = json.loads(exp_data)
        result = json.loads(explanation["result"])
        model_id = explanation["model_id"]
        
        # Get model from database
        db = get_sync_session()
        from app.models.model import Model
        model = db.query(Model).filter(Model.id == model_id).first()
        
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        db.close()
        
        # Load model file
        model_path = Path(f"data/models/{model_id}/model.pkl")
        with open(model_path, 'rb') as f:
            loaded_model = pickle.load(f)
        
        # Load test data using dataset loader
        from app.datasets.registry import get_dataset_registry
        from app.datasets.loaders import get_loader
        
        dataset_id = model.dataset_id
        registry = get_dataset_registry()
        dataset_config = registry.get_dataset_config(dataset_id)
        
        if not dataset_config:
            raise ValueError(f"Dataset not found: {dataset_id}")
        
        loader = get_loader(dataset_id, dataset_config)
        train_df, val_df, test_df = loader.load_splits()
        
        # Get target column
        target_col = loader.get_target_column()
        
        # Separate features and target
        X_test = test_df.drop(columns=[target_col])
        y_test = test_df[target_col]
        
        # Sample for evaluation (use 100 samples)
        sample_size = min(100, len(X_test))
        sample_indices = np.random.choice(len(X_test), sample_size, replace=False)
        X_sample = X_test.iloc[sample_indices]
        y_sample = y_test.iloc[sample_indices]
        
        # Extract attributions from explanation
        feature_importance = result.get('feature_importance', [])
        
        # Create attribution matrix (importance scores for each feature)
        feature_names = X_sample.columns.tolist()
        attributions = np.zeros((len(X_sample), len(feature_names)))
        
        # Map feature importance to attribution matrix
        for feat_info in feature_importance:
            feat_name = feat_info['feature']
            if feat_name in feature_names:
                feat_idx = feature_names.index(feat_name)
                # Use same importance for all samples (global explanation)
                attributions[:, feat_idx] = feat_info['importance']
        
        # Initialize Quantus evaluator
        evaluator = QuantusEvaluator(loaded_model, X_sample, y_sample)
        
        # Evaluate all metrics
        quality_results = evaluator.evaluate_all(attributions, num_samples=sample_size)
        
        # Save results to Redis
        eval_data = redis_client.get(f"quality_eval:{eval_id}")
        if eval_data:
            eval_info = json.loads(eval_data)
            eval_info["status"] = "completed"
            eval_info["result"] = json.dumps(quality_results)
            redis_client.setex(f"quality_eval:{eval_id}", 3600, json.dumps(eval_info))
        
        logger.info("Quality evaluation complete",
                   eval_id=eval_id,
                   overall_quality=quality_results.get('overall_quality'))
        
        return {
            'status': 'success',
            'eval_id': eval_id,
            'task_id': self.request.id,
            'quality_score': quality_results.get('overall_quality'),
        }
        
    except Exception as e:
        logger.error("Quality evaluation failed",
                    eval_id=eval_id,
                    task_id=self.request.id,
                    exc_info=e)
        
        # Update status to failed
        try:
            eval_data = redis_client.get(f"quality_eval:{eval_id}")
            if eval_data:
                eval_info = json.loads(eval_data)
                eval_info["status"] = "failed"
                eval_info["error"] = str(e)
                redis_client.setex(f"quality_eval:{eval_id}", 3600, json.dumps(eval_info))
        except:
            pass
        
        return {
            'status': 'error',
            'eval_id': eval_id,
            'error': str(e),
            'task_id': self.request.id,
        }
