"""Supabase client for metadata storage."""

from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class SupabaseClient:
    """Supabase client wrapper for XAI platform."""
    
    def __init__(self):
        """Initialize Supabase client."""
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise ValueError("Supabase credentials not configured. Check .env file.")
        
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_KEY  # Use service key for backend operations
        )
        logger.info("Supabase client initialized", url=settings.SUPABASE_URL)
    
    # ========== DATASETS ==========
    
    def get_datasets(self, is_active: bool = True) -> List[Dict]:
        """Get all datasets."""
        try:
            query = self.client.table('datasets').select('*')
            if is_active:
                query = query.eq('is_active', True)
            response = query.execute()
            logger.info("Fetched datasets", count=len(response.data))
            return response.data
        except Exception as e:
            logger.error("Failed to get datasets", error=str(e))
            raise
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset by ID."""
        try:
            response = self.client.table('datasets').select('*').eq('id', dataset_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error("Failed to get dataset", dataset_id=dataset_id, error=str(e))
            raise
    
    def insert_dataset(self, dataset_data: Dict[str, Any]) -> Dict:
        """Insert new dataset."""
        try:
            response = self.client.table('datasets').insert(dataset_data).execute()
            logger.info("Dataset inserted", dataset_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert dataset", error=str(e))
            raise
    
    def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> Dict:
        """Update dataset."""
        try:
            response = self.client.table('datasets').update(updates).eq('id', dataset_id).execute()
            logger.info("Dataset updated", dataset_id=dataset_id)
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error("Failed to update dataset", dataset_id=dataset_id, error=str(e))
            raise
    
    # ========== MODELS ==========
    
    def get_models(self, dataset_id: Optional[str] = None) -> List[Dict]:
        """Get models, optionally filtered by dataset."""
        try:
            query = self.client.table('models').select('*')
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            response = query.execute()
            logger.info("Fetched models", count=len(response.data))
            return response.data
        except Exception as e:
            logger.error("Failed to get models", error=str(e))
            raise
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """Get model by ID."""
        try:
            response = self.client.table('models').select('*').eq('id', model_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error("Failed to get model", model_id=model_id, error=str(e))
            raise
    
    def insert_model(self, model_data: Dict[str, Any]) -> Dict:
        """Insert new model."""
        try:
            response = self.client.table('models').insert(model_data).execute()
            logger.info("Model inserted", model_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert model", error=str(e))
            raise
    
    def update_model(self, model_id: str, updates: Dict[str, Any]) -> Dict:
        """Update model."""
        try:
            response = self.client.table('models').update(updates).eq('id', model_id).execute()
            logger.info("Model updated", model_id=model_id)
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error("Failed to update model", model_id=model_id, error=str(e))
            raise
    
    def insert_model_metrics(self, metrics_data: Dict[str, Any]) -> Dict:
        """Insert model metrics."""
        try:
            response = self.client.table('model_metrics').insert(metrics_data).execute()
            logger.info("Model metrics inserted", model_id=metrics_data.get('model_id'))
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert metrics", error=str(e))
            raise
    
    # ========== EXPLANATIONS ==========
    
    def insert_explanation(self, explanation_data: Dict[str, Any]) -> Dict:
        """Insert explanation summary."""
        try:
            response = self.client.table('explanations').insert(explanation_data).execute()
            logger.info("Explanation inserted", explanation_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert explanation", error=str(e))
            raise
    
    def get_explanations(
        self, 
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        method: Optional[str] = None
    ) -> List[Dict]:
        """Get explanations with optional filters."""
        try:
            query = self.client.table('explanations').select('*')
            if model_id:
                query = query.eq('model_id', model_id)
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            if method:
                query = query.eq('method', method)
            response = query.execute()
            logger.info("Fetched explanations", count=len(response.data))
            return response.data
        except Exception as e:
            logger.error("Failed to get explanations", error=str(e))
            raise
    
    # ========== EXPERIMENTS ==========
    
    def insert_experiment(self, experiment_data: Dict[str, Any]) -> Dict:
        """Insert experiment."""
        try:
            response = self.client.table('experiments').insert(experiment_data).execute()
            logger.info("Experiment inserted", experiment_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert experiment", error=str(e))
            raise
    
    def get_experiments(self, dataset_id: Optional[str] = None) -> List[Dict]:
        """Get experiments, optionally filtered by dataset."""
        try:
            query = self.client.table('experiments').select('*')
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error("Failed to get experiments", error=str(e))
            raise
    
    # ========== BENCHMARKS ==========
    
    def insert_benchmark(self, benchmark_data: Dict[str, Any]) -> Dict:
        """Insert benchmark results."""
        try:
            response = self.client.table('benchmarks').insert(benchmark_data).execute()
            logger.info("Benchmark inserted", benchmark_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert benchmark", error=str(e))
            raise
    
    def get_benchmarks(self) -> List[Dict]:
        """Get all benchmarks."""
        try:
            response = self.client.table('benchmarks').select('*').execute()
            return response.data
        except Exception as e:
            logger.error("Failed to get benchmarks", error=str(e))
            raise
    
    # ========== HEALTH CHECK ==========
    
    def health_check(self) -> bool:
        """Check if Supabase connection is healthy."""
        try:
            # Try to query datasets table
            self.client.table('datasets').select('id').limit(1).execute()
            logger.info("Supabase health check passed")
            return True
        except Exception as e:
            logger.error("Supabase health check failed", error=str(e))
            return False


# Singleton instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
