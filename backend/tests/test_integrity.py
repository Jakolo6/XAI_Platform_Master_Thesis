"""
Backend Integrity Tests
========================

Validates that the unified backend architecture maintains data consistency.

Tests:
- Every model in DB has all required metrics
- All endpoints return valid responses
- No missing or inconsistent schema fields
- DAL operations work correctly
"""

import pytest
from typing import Dict, Any
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from app.core.data_access import dal
from app.services.metrics_service import metrics_service
from app.core.config import settings


class TestDataIntegrity:
    """Test data integrity across the platform."""
    
    def test_dal_connection(self):
        """Test that DAL can connect to Supabase."""
        assert dal.db.is_available(), "DAL should have Supabase connection"
    
    def test_models_have_metrics(self):
        """Test that all completed models have metrics."""
        models = dal.list_models(status='completed', include_metrics=False)
        
        for model in models:
            model_id = model['id']
            metrics = dal.get_model_metrics(model_id)
            
            # Completed models should have metrics
            assert metrics is not None, f"Model {model_id} missing metrics"
            
            # Validate required metric fields
            required_fields = ['auc_roc', 'f1_score', 'accuracy', 'precision', 'recall']
            for field in required_fields:
                assert field in metrics, f"Model {model_id} missing metric field: {field}"
    
    def test_metrics_schema_consistency(self):
        """Test that all metrics follow the same schema."""
        models = dal.list_models(include_metrics=True)
        
        if not models:
            pytest.skip("No models in database")
        
        # Get schema from first model with metrics
        reference_schema = None
        for model in models:
            if 'auc_roc' in model:
                reference_schema = set(model.keys())
                break
        
        if not reference_schema:
            pytest.skip("No models with metrics found")
        
        # Check all other models have same schema
        for model in models:
            if 'auc_roc' in model:  # Has metrics
                model_schema = set(model.keys())
                missing = reference_schema - model_schema
                extra = model_schema - reference_schema
                
                assert not missing, f"Model {model['id']} missing fields: {missing}"
                # Extra fields are OK (models can have additional metadata)
    
    def test_model_metadata_fields(self):
        """Test that all models have required metadata fields."""
        models = dal.list_models(include_metrics=False)
        
        required_fields = ['id', 'name', 'model_type', 'status', 'dataset_id']
        
        for model in models:
            for field in required_fields:
                assert field in model, f"Model {model.get('id', 'unknown')} missing field: {field}"
    
    def test_dataset_integrity(self):
        """Test that all datasets have required fields."""
        datasets = dal.list_datasets()
        
        required_fields = ['id', 'name', 'status']
        
        for dataset in datasets:
            for field in required_fields:
                assert field in dataset, f"Dataset {dataset.get('id', 'unknown')} missing field: {field}"
    
    def test_explanation_model_linkage(self):
        """Test that all explanations link to valid models."""
        # This would require querying all explanations
        # For now, test a sample
        models = dal.list_models(include_metrics=False)
        
        if not models:
            pytest.skip("No models in database")
        
        # Check first model's explanations
        model_id = models[0]['id']
        shap_exp = dal.get_explanation(model_id, method='shap')
        
        if shap_exp:
            assert shap_exp['model_id'] == model_id, "Explanation model_id mismatch"


class TestMetricsService:
    """Test centralized metrics service."""
    
    def test_metrics_service_status(self):
        """Test that metrics service is operational."""
        status = metrics_service.get_service_status()
        
        assert status['service'] == 'metrics_service'
        assert status['status'] == 'operational'
    
    def test_metrics_validation(self):
        """Test metrics validation logic."""
        # Valid metrics
        valid_metrics = {
            'accuracy': 0.85,
            'precision': 0.80,
            'recall': 0.75,
            'f1_score': 0.77,
            'auc_roc': 0.88,
            'auc_pr': 0.82,
            'confusion_matrix': {'tn': 100, 'fp': 20, 'fn': 15, 'tp': 85}
        }
        
        is_valid, missing = metrics_service.validate_metrics(valid_metrics)
        assert is_valid, f"Valid metrics failed validation: {missing}"
        
        # Invalid metrics (missing fields)
        invalid_metrics = {
            'accuracy': 0.85,
            'precision': 0.80
        }
        
        is_valid, missing = metrics_service.validate_metrics(invalid_metrics)
        assert not is_valid, "Invalid metrics passed validation"
        assert len(missing) > 0, "Should have missing fields"
    
    def test_metrics_retrieval(self):
        """Test that metrics can be retrieved for existing models."""
        models = dal.list_models(status='completed', include_metrics=False)
        
        if not models:
            pytest.skip("No completed models in database")
        
        model_id = models[0]['id']
        metrics = metrics_service.get_metrics(model_id)
        
        assert metrics is not None, f"Failed to retrieve metrics for {model_id}"
        
        # Validate metrics
        is_valid, missing = metrics_service.validate_metrics(metrics)
        assert is_valid, f"Retrieved metrics invalid: {missing}"


class TestDALOperations:
    """Test Data Access Layer operations."""
    
    def test_get_model_with_metrics(self):
        """Test getting model with metrics enrichment."""
        models = dal.list_models(include_metrics=False)
        
        if not models:
            pytest.skip("No models in database")
        
        model_id = models[0]['id']
        
        # Get without metrics
        model_no_metrics = dal.get_model(model_id, include_metrics=False)
        assert model_no_metrics is not None
        
        # Get with metrics
        model_with_metrics = dal.get_model(model_id, include_metrics=True)
        assert model_with_metrics is not None
        
        # With metrics should have more fields
        if 'auc_roc' in model_with_metrics:
            assert 'auc_roc' not in model_no_metrics or model_with_metrics != model_no_metrics
    
    def test_model_id_suffix_handling(self):
        """Test that _metrics suffix is handled correctly."""
        models = dal.list_models(include_metrics=False)
        
        if not models:
            pytest.skip("No models in database")
        
        model_id = models[0]['id']
        
        # Both with and without suffix should work
        model1 = dal.get_model(model_id)
        model2 = dal.get_model(f"{model_id}_metrics")
        
        assert model1 is not None
        assert model2 is not None
        assert model1['id'] == model2['id']
    
    def test_list_models_filtering(self):
        """Test model listing with filters."""
        all_models = dal.list_models()
        completed_models = dal.list_models(status='completed')
        
        # Completed should be subset of all
        assert len(completed_models) <= len(all_models)
        
        # All completed models should have status='completed'
        for model in completed_models:
            assert model['status'] == 'completed'


class TestConfigValidation:
    """Test configuration validation."""
    
    def test_required_config_present(self):
        """Test that required configuration is present."""
        assert settings.SUPABASE_URL, "SUPABASE_URL not configured"
        assert settings.SUPABASE_SERVICE_KEY, "SUPABASE_SERVICE_KEY not configured"
        assert settings.R2_BUCKET_NAME, "R2_BUCKET_NAME not configured"
    
    def test_optional_config_handling(self):
        """Test that optional config is handled gracefully."""
        # These are optional - should not crash if missing
        _ = settings.OPENAI_API_KEY  # May be empty
        _ = settings.KAGGLE_USERNAME  # May be empty


class TestEndpointResponses:
    """Test that all endpoints return valid responses."""
    
    # This would require FastAPI TestClient
    # Placeholder for future implementation
    
    def test_models_endpoint_schema(self):
        """Test /models/ endpoint returns valid schema."""
        pytest.skip("Requires TestClient - implement in integration tests")
    
    def test_datasets_endpoint_schema(self):
        """Test /datasets/ endpoint returns valid schema."""
        pytest.skip("Requires TestClient - implement in integration tests")


# Run tests with: pytest backend/tests/test_integrity.py -v
