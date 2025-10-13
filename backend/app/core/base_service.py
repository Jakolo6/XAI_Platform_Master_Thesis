"""
Base Service Class
==================

All XAI platform services inherit from this base class to ensure:
- Consistent logging
- Standardized error handling
- Unified data access through DAL
- Supabase and R2 sync management
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import structlog
from app.core.data_access import dal
from app.core.config import settings

logger = structlog.get_logger()


class XAIService(ABC):
    """
    Base service class for all XAI platform services.
    
    Provides:
    - Standardized logging with service name
    - Error handling and recovery
    - Data access through unified DAL
    - Configuration validation
    """
    
    def __init__(self, service_name: str):
        """
        Initialize base service.
        
        Args:
            service_name: Name of the service (e.g., "model_service", "dataset_service")
        """
        self.service_name = service_name
        self.logger = logger.bind(service=service_name)
        self.dal = dal
        self.config = settings
        
        self.logger.info(f"{service_name} initialized")
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration for this service."""
        # Base validation - can be overridden by subclasses
        if not self.config.SUPABASE_URL:
            self.logger.warning("Supabase URL not configured")
        
        if not self.config.R2_BUCKET_NAME:
            self.logger.warning("R2 bucket not configured")
    
    def _log_operation(self, operation: str, **kwargs):
        """Log service operation with context."""
        self.logger.info(f"{self.service_name}.{operation}", **kwargs)
    
    def _log_error(self, operation: str, error: Exception, **kwargs):
        """Log service error with context."""
        self.logger.error(
            f"{self.service_name}.{operation} failed",
            error=str(error),
            error_type=type(error).__name__,
            **kwargs
        )
    
    def _handle_error(
        self,
        operation: str,
        error: Exception,
        default_return: Any = None,
        **context
    ) -> Any:
        """
        Standardized error handling.
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
            default_return: Value to return on error
            **context: Additional context for logging
            
        Returns:
            default_return value
        """
        self._log_error(operation, error, **context)
        return default_return
    
    @abstractmethod
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get current status of the service.
        
        Must be implemented by all services.
        
        Returns:
            Dictionary with service status information
        """
        pass


class ModelServiceBase(XAIService):
    """Base class for model-related services."""
    
    def __init__(self, service_name: str = "model_service"):
        super().__init__(service_name)
    
    def _validate_config(self):
        """Validate model service specific configuration."""
        super()._validate_config()
        
        # Model services need R2 for model storage
        if not self.config.R2_ACCESS_KEY_ID:
            self.logger.warning("R2 credentials not configured - model storage unavailable")
    
    def get_model(self, model_id: str, include_metrics: bool = True) -> Optional[Dict[str, Any]]:
        """Get model through DAL."""
        return self.dal.get_model(model_id, include_metrics=include_metrics)
    
    def save_metrics(self, model_id: str, metrics: Dict[str, Any]) -> bool:
        """Save model metrics through DAL."""
        return self.dal.save_model_metrics(model_id, metrics, source_module=self.service_name)


class DatasetServiceBase(XAIService):
    """Base class for dataset-related services."""
    
    def __init__(self, service_name: str = "dataset_service"):
        super().__init__(service_name)
    
    def _validate_config(self):
        """Validate dataset service specific configuration."""
        super()._validate_config()
        
        # Dataset services may need Kaggle credentials
        if not self.config.KAGGLE_USERNAME:
            self.logger.info("Kaggle credentials not configured - some datasets unavailable")
    
    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Get dataset through DAL."""
        return self.dal.get_dataset(dataset_id)
    
    def update_status(self, dataset_id: str, status: str, processed: bool = False) -> bool:
        """Update dataset status through DAL."""
        return self.dal.update_dataset_status(
            dataset_id, 
            status, 
            processed, 
            source_module=self.service_name
        )


class ExplanationServiceBase(XAIService):
    """Base class for explanation-related services."""
    
    def __init__(self, service_name: str = "explanation_service"):
        super().__init__(service_name)
    
    def get_explanation(
        self,
        model_id: str,
        method: str = 'shap'
    ) -> Optional[Dict[str, Any]]:
        """Get explanation through DAL."""
        return self.dal.get_explanation(model_id, method=method)
    
    def save_explanation(
        self,
        model_id: str,
        method: str,
        explanation_data: Dict[str, Any]
    ) -> Optional[str]:
        """Save explanation through DAL."""
        return self.dal.save_explanation(
            model_id,
            method,
            explanation_data,
            source_module=self.service_name
        )


class InterpretationServiceBase(XAIService):
    """Base class for interpretation-related services."""
    
    def __init__(self, service_name: str = "interpretation_service"):
        super().__init__(service_name)
    
    def _validate_config(self):
        """Validate interpretation service specific configuration."""
        super()._validate_config()
        
        # Interpretation services need OpenAI for LLM mode
        if not self.config.OPENAI_API_KEY:
            self.logger.warning("OpenAI API key not configured - LLM mode unavailable")
    
    def save_feedback(self, feedback_data: Dict[str, Any]) -> bool:
        """Save interpretation feedback through DAL."""
        return self.dal.save_interpretation_feedback(
            feedback_data,
            source_module=self.service_name
        )
