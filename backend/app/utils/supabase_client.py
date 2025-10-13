"""
Supabase client for database operations.
"""

from typing import Optional, Dict, Any, List
import structlog
from datetime import datetime

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from app.core.config import settings

logger = structlog.get_logger()


class SupabaseClient:
    """Supabase client for database operations."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase client not available")
            self.client = None
            return
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            logger.warning("Supabase credentials not configured")
            self.client = None
            return
        
        try:
            self.client: Optional[Client] = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
            logger.info("Supabase client initialized")
        except Exception as e:
            logger.error("Failed to initialize Supabase client", exc_info=e)
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Supabase is available."""
        return self.client is not None
    
    # ============================================================
    # DATASETS
    # ============================================================
    
    def create_dataset(self, dataset_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new dataset record."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('datasets').insert(dataset_data).execute()
            logger.info("Dataset created", dataset_id=dataset_data.get('id'))
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to create dataset", error=str(e))
            return None
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset by ID."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('datasets').select('*').eq('id', dataset_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to get dataset", dataset_id=dataset_id, error=str(e))
            return None
    
    def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> Optional[Dict]:
        """Update dataset record."""
        if not self.is_available():
            return None
        
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('datasets').update(updates).eq('id', dataset_id).execute()
            logger.info("Dataset updated", dataset_id=dataset_id)
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to update dataset", dataset_id=dataset_id, error=str(e))
            return None
    
    def list_datasets(self) -> List[Dict]:
        """List all datasets."""
        if not self.is_available():
            return []
        
        try:
            result = self.client.table('datasets').select('*').execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error("Failed to list datasets", error=str(e))
            return []
    
    # ============================================================
    # MODELS
    # ============================================================
    
    def create_model(self, model_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new model record."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('models').insert(model_data).execute()
            logger.info("Model created", model_id=model_data.get('id'))
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to create model", error=str(e))
            return None
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """Get model by model_id or id."""
        if not self.is_available():
            return None
        
        try:
            # Try to find by id field first (which may have _metrics suffix)
            # The model_id parameter from the URL doesn't have _metrics suffix
            # So we need to search for records where id starts with model_id
            result = self.client.table('models').select('*').execute()
            
            if result.data:
                # Filter in Python to find matching model
                for model in result.data:
                    # Check if id matches exactly or if id starts with model_id
                    if model.get('id') == model_id or model.get('id', '').startswith(model_id):
                        return model
            
            return None
        except Exception as e:
            logger.error("Failed to get model", model_id=model_id, error=str(e))
            return None
    
    def list_models(self, dataset_id: Optional[str] = None) -> List[Dict]:
        """List models, optionally filtered by dataset."""
        if not self.is_available():
            return []
        
        try:
            query = self.client.table('models').select('*')
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error("Failed to list models", error=str(e))
            return []
    
    def update_model(self, model_id: str, updates: Dict[str, Any]) -> Optional[Dict]:
        """Update model record."""
        if not self.is_available():
            return None
        
        try:
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.client.table('models').update(updates).eq('id', model_id).execute()
            logger.info("Model updated", model_id=model_id)
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to update model", model_id=model_id, error=str(e))
            return None
    
    def create_model_metrics(self, metrics_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new model metrics record."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('model_metrics').insert(metrics_data).execute()
            logger.info("Model metrics created", model_id=metrics_data.get('model_id'))
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to create model metrics", error=str(e))
            return None
    
    def get_model_metrics(self, model_id: str) -> Optional[Dict]:
        """Get model metrics by model_id."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('model_metrics').select('*').eq('model_id', model_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to get model metrics", model_id=model_id, error=str(e))
            return None
    
    # ============================================================
    # EXPLANATIONS
    # ============================================================
    
    def create_explanation(self, explanation_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new explanation record."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('explanations').insert(explanation_data).execute()
            logger.info("Explanation created", explanation_id=explanation_data.get('id'))
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to create explanation", error=str(e))
            return None
    
    def get_explanation(self, explanation_id: str) -> Optional[Dict]:
        """Get explanation by ID."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('explanations').select('*').eq('id', explanation_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to get explanation", explanation_id=explanation_id, error=str(e))
            return None
    
    def list_explanations(self, model_id: Optional[str] = None) -> List[Dict]:
        """List explanations, optionally filtered by model."""
        if not self.is_available():
            return []
        
        try:
            query = self.client.table('explanations').select('*')
            if model_id:
                query = query.eq('model_id', model_id)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error("Failed to list explanations", error=str(e))
            return []
    
    # ============================================================
    # BENCHMARKS
    # ============================================================
    
    def create_benchmark(self, benchmark_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new benchmark record."""
        if not self.is_available():
            return None
        
        try:
            result = self.client.table('benchmarks').insert(benchmark_data).execute()
            logger.info("Benchmark created", benchmark_id=benchmark_data.get('id'))
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error("Failed to create benchmark", error=str(e))
            return None
    
    def list_benchmarks(self, dataset_id: Optional[str] = None) -> List[Dict]:
        """List benchmarks, optionally filtered by dataset."""
        if not self.is_available():
            return []
        
        try:
            query = self.client.table('benchmarks').select('*')
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            result = query.execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error("Failed to list benchmarks", error=str(e))
            return []


# Global Supabase client instance
supabase_db = SupabaseClient()
