"""
Unified Data Access Layer (DAL)
================================

Central module for all data operations across the XAI platform.
Prevents regressions by providing a single source of truth for:
- Model metadata and metrics
- Dataset registry and preprocessing info
- SHAP/LIME artifacts
- Interpretation feedback storage

All endpoints should import from this layer instead of handling data separately.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import structlog
from app.utils.supabase_client import supabase_db
from app.core.config import settings

logger = structlog.get_logger(__name__)


class DataAccessLayer:
    """
    Unified data access layer for all XAI platform data.
    
    Provides consistent interface for:
    - Models and metrics
    - Datasets and preprocessing
    - Explanations (SHAP, LIME)
    - Interpretation feedback
    - Research data
    """
    
    def __init__(self):
        """Initialize DAL with Supabase client."""
        self.db = supabase_db
        self._validate_connection()
    
    def _validate_connection(self):
        """Validate database connection on initialization."""
        if not self.db.is_available():
            logger.warning("Supabase not available - DAL operating in degraded mode")
        else:
            logger.info("DAL initialized successfully")
    
    def _add_metadata(self, data: Dict[str, Any], source_module: str) -> Dict[str, Any]:
        """Add standard metadata fields to any data object."""
        data['last_updated'] = datetime.utcnow().isoformat()
        data['source_module'] = source_module
        return data
    
    # ==========================================
    # MODEL OPERATIONS
    # ==========================================
    
    def get_model(self, model_id: str, include_metrics: bool = True) -> Optional[Dict[str, Any]]:
        """
        Get model by ID with optional metrics enrichment.
        
        Args:
            model_id: Model identifier (with or without _metrics suffix)
            include_metrics: Whether to include metrics in response
            
        Returns:
            Model data with metrics if requested, None if not found
        """
        # Strip _metrics suffix if present
        base_model_id = model_id.replace('_metrics', '')
        
        try:
            model = self.db.get_model(base_model_id)
            
            if not model:
                logger.warning("Model not found", model_id=base_model_id)
                return None
            
            if include_metrics:
                metrics = self.get_model_metrics(base_model_id)
                if metrics:
                    model = {**model, **metrics}
            
            logger.debug("Model retrieved", model_id=base_model_id, has_metrics=include_metrics)
            return model
            
        except Exception as e:
            logger.error("Failed to get model", model_id=base_model_id, error=str(e))
            return None
    
    def list_models(
        self, 
        dataset_id: Optional[str] = None,
        include_metrics: bool = True,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all models with optional filtering.
        
        Args:
            dataset_id: Filter by dataset
            include_metrics: Include metrics in each model
            status: Filter by status (training, completed, failed)
            
        Returns:
            List of models with optional metrics
        """
        try:
            models = self.db.list_models(dataset_id=dataset_id)
            
            # Filter by status if provided
            if status:
                models = [m for m in models if m.get('status') == status]
            
            # Enrich with metrics if requested
            if include_metrics:
                enriched_models = []
                for model in models:
                    metrics = self.get_model_metrics(model['id'])
                    if metrics:
                        enriched_models.append({**model, **metrics})
                    else:
                        enriched_models.append(model)
                models = enriched_models
            
            logger.debug("Models listed", count=len(models), dataset_id=dataset_id)
            return models
            
        except Exception as e:
            logger.error("Failed to list models", error=str(e))
            return []
    
    def create_model(self, model_data: Dict[str, Any], source_module: str = "model_service") -> Optional[str]:
        """
        Create a new model entry.
        
        Args:
            model_data: Model metadata
            source_module: Module creating the model
            
        Returns:
            Model ID if successful, None otherwise
        """
        try:
            model_data = self._add_metadata(model_data, source_module)
            
            logger.debug("Creating model in database", 
                        model_id=model_data.get('id'),
                        model_name=model_data.get('name'))
            
            result = self.db.client.table('models').insert(model_data).execute()
            
            if result.data:
                model_id = result.data[0]['id']
                logger.info("Model created successfully", 
                           model_id=model_id, 
                           model_name=model_data.get('name'),
                           source=source_module)
                return model_id
            
            logger.error("Model creation returned no data", model_data=model_data)
            return None
            
        except Exception as e:
            logger.error("Failed to create model", 
                        error=str(e),
                        model_id=model_data.get('id'),
                        exc_info=True)
            return None
    
    def update_model(
        self, 
        model_id: str, 
        updates: Dict[str, Any],
        source_module: str = "model_service"
    ) -> bool:
        """
        Update model metadata.
        
        Args:
            model_id: Model to update
            updates: Fields to update
            source_module: Module making the update
            
        Returns:
            True if successful
        """
        try:
            base_model_id = model_id.replace('_metrics', '')
            updates = self._add_metadata(updates, source_module)
            
            self.db.client.table('models').update(updates).eq('id', base_model_id).execute()
            logger.info("Model updated", model_id=base_model_id, source=source_module)
            return True
            
        except Exception as e:
            logger.error("Failed to update model", model_id=model_id, error=str(e))
            return False
    
    def delete_model(self, model_id: str, source_module: str = "model_service") -> bool:
        """
        Delete model and all associated data.
        
        Args:
            model_id: Model to delete
            source_module: Module requesting deletion
            
        Returns:
            True if successful
        """
        try:
            base_model_id = model_id.replace('_metrics', '')
            
            # Delete explanations
            self.db.client.table('explanations').delete().eq('model_id', base_model_id).execute()
            
            # Delete metrics
            self.db.client.table('model_metrics').delete().eq('model_id', base_model_id).execute()
            
            # Delete model
            self.db.client.table('models').delete().eq('id', base_model_id).execute()
            
            logger.info("Model deleted", model_id=base_model_id, source=source_module)
            return True
            
        except Exception as e:
            logger.error("Failed to delete model", model_id=model_id, error=str(e))
            return False
    
    # ==========================================
    # METRICS OPERATIONS
    # ==========================================
    
    def get_model_metrics(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Metrics dictionary or None
        """
        try:
            base_model_id = model_id.replace('_metrics', '')
            metrics = self.db.get_model_metrics(base_model_id)
            
            if metrics:
                logger.debug("Metrics retrieved", model_id=base_model_id)
            
            return metrics
            
        except Exception as e:
            logger.error("Failed to get metrics", model_id=model_id, error=str(e))
            return None
    
    def save_model_metrics(
        self,
        model_id: str,
        metrics: Dict[str, Any],
        source_module: str = "model_service"
    ) -> bool:
        """
        Save or update model metrics.
        
        Args:
            model_id: Model identifier
            metrics: Metrics data
            source_module: Module saving metrics
            
        Returns:
            True if successful
        """
        try:
            base_model_id = model_id.replace('_metrics', '')
            metrics_data = {
                'model_id': base_model_id,
                **metrics,
                **self._add_metadata({}, source_module)
            }
            
            # Upsert metrics
            result = self.db.client.table('model_metrics').upsert(metrics_data).execute()
            
            logger.info("Metrics saved", model_id=base_model_id, source=source_module)
            return True
            
        except Exception as e:
            logger.error("Failed to save metrics", model_id=model_id, error=str(e))
            return False
    
    # ==========================================
    # DATASET OPERATIONS
    # ==========================================
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset by ID."""
        try:
            dataset = self.db.get_dataset(dataset_id)
            logger.debug("Dataset retrieved", dataset_id=dataset_id)
            return dataset
        except Exception as e:
            logger.error("Failed to get dataset", dataset_id=dataset_id, error=str(e))
            return None
    
    def list_datasets(self) -> List[Dict[str, Any]]:
        """List all datasets."""
        try:
            datasets = self.db.list_datasets()
            logger.debug("Datasets listed", count=len(datasets))
            return datasets
        except Exception as e:
            logger.error("Failed to list datasets", error=str(e))
            return []
    
    def update_dataset_status(
        self,
        dataset_id: str,
        status: str,
        processed: bool = False,
        source_module: str = "dataset_service"
    ) -> bool:
        """Update dataset processing status."""
        try:
            updates = {
                'status': status,
                'processed': processed,
                **self._add_metadata({}, source_module)
            }
            
            self.db.client.table('datasets').update(updates).eq('id', dataset_id).execute()
            logger.info("Dataset status updated", dataset_id=dataset_id, status=status)
            return True
            
        except Exception as e:
            logger.error("Failed to update dataset status", dataset_id=dataset_id, error=str(e))
            return False
    
    # ==========================================
    # EXPLANATION OPERATIONS
    # ==========================================
    
    def get_explanation(
        self,
        model_id: str,
        method: str = 'shap',
        status: str = 'completed'
    ) -> Optional[Dict[str, Any]]:
        """
        Get explanation for a model.
        
        Args:
            model_id: Model identifier
            method: Explanation method (shap, lime)
            status: Filter by status
            
        Returns:
            Explanation data or None
        """
        try:
            base_model_id = model_id.replace('_metrics', '')
            explanations = self.db.list_explanations(model_id=base_model_id)
            
            # Find matching explanation
            explanation = next(
                (exp for exp in explanations 
                 if exp.get('method') == method and exp.get('status') == status),
                None
            )
            
            if explanation:
                logger.debug("Explanation retrieved", model_id=base_model_id, method=method)
            
            return explanation
            
        except Exception as e:
            logger.error("Failed to get explanation", model_id=model_id, error=str(e))
            return None
    
    def save_explanation(
        self,
        model_id: str,
        method: str,
        explanation_data: Dict[str, Any],
        source_module: str = "explanation_service"
    ) -> Optional[str]:
        """
        Save explanation data.
        
        Args:
            model_id: Model identifier
            method: Explanation method
            explanation_data: Explanation data
            source_module: Module saving explanation
            
        Returns:
            Explanation ID if successful
        """
        try:
            base_model_id = model_id.replace('_metrics', '')
            
            data = {
                'model_id': base_model_id,
                'method': method,
                **explanation_data,
                **self._add_metadata({}, source_module)
            }
            
            result = self.db.client.table('explanations').insert(data).execute()
            
            if result.data:
                exp_id = result.data[0]['id']
                logger.info("Explanation saved", model_id=base_model_id, method=method)
                return exp_id
            
            return None
            
        except Exception as e:
            logger.error("Failed to save explanation", model_id=model_id, error=str(e))
            return None
    
    # ==========================================
    # INTERPRETATION FEEDBACK OPERATIONS
    # ==========================================
    
    def save_interpretation_feedback(
        self,
        feedback_data: Dict[str, Any],
        source_module: str = "interpretation_service"
    ) -> bool:
        """Save interpretation feedback for research."""
        try:
            data = {
                **feedback_data,
                **self._add_metadata({}, source_module)
            }
            
            self.db.client.table('interpretation_feedback').insert(data).execute()
            logger.info("Interpretation feedback saved", mode=feedback_data.get('mode'))
            return True
            
        except Exception as e:
            logger.error("Failed to save interpretation feedback", error=str(e))
            return False
    
    def get_interpretation_stats(self) -> Dict[str, Any]:
        """Get aggregated interpretation feedback statistics."""
        try:
            result = self.db.client.table('interpretation_feedback_summary').select('*').execute()
            
            if result.data:
                return {
                    'summary': result.data,
                    'total_ratings': sum(r.get('total_ratings', 0) for r in result.data)
                }
            
            return {'summary': [], 'total_ratings': 0}
            
        except Exception as e:
            logger.error("Failed to get interpretation stats", error=str(e))
            return {'summary': [], 'total_ratings': 0}


# Global DAL instance
dal = DataAccessLayer()
