"""
Explanation generation service for SHAP and LIME.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import uuid
import structlog
import pandas as pd
import numpy as np
import json

from app.utils.r2_storage import r2_storage_client
from app.utils.supabase_client import supabase_db

logger = structlog.get_logger()


class ExplanationService:
    """Service for generating and managing model explanations."""
    
    def generate_explanation(
        self,
        model_id: str,
        method: str = "shap",
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Generate explanation for a model using SHAP or LIME.
        
        Args:
            model_id: ID of the trained model
            method: Explanation method ('shap' or 'lime')
            sample_size: Number of samples to use for explanation
            
        Returns:
            Dictionary with explanation results
        """
        explanation_id = f"{model_id}_{method}_{uuid.uuid4().hex[:8]}"
        
        try:
            logger.info("Starting explanation generation",
                       explanation_id=explanation_id,
                       model_id=model_id,
                       method=method)
            
            # 1. Get model from database
            model = supabase_db.get_model(model_id)
            if not model:
                raise ValueError(f"Model {model_id} not found")
            
            if model['status'] != 'completed':
                raise ValueError(f"Model {model_id} is not completed")
            
            # 2. Get dataset
            dataset_id = model['dataset_id']
            dataset = supabase_db.get_dataset(dataset_id)
            if not dataset:
                raise ValueError(f"Dataset {dataset_id} not found")
            
            # 3. Download model and test data from R2
            temp_dir = Path(f"/tmp/{explanation_id}")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                model_path = temp_dir / "model.pkl"
                test_data_path = temp_dir / "test.parquet"
                
                # Download model
                r2_storage_client.download_file(
                    model['model_path'],
                    str(model_path)
                )
                
                # Download test data
                r2_storage_client.download_file(
                    f"{dataset['file_path']}/test.parquet",
                    str(test_data_path)
                )
                
                # Load test data
                test_df = pd.read_parquet(test_data_path)
                
                # Sample data if needed
                if len(test_df) > sample_size:
                    test_df = test_df.sample(n=sample_size, random_state=42)
                
                # Separate features and target
                X_test = test_df.iloc[:, :-1]  # All columns except last
                y_test = test_df.iloc[:, -1]   # Last column is target
                
                # 4. Generate explanation based on method
                if method.lower() == "shap":
                    explanation_data = self._generate_shap(
                        model_path, X_test, model['model_type']
                    )
                elif method.lower() == "lime":
                    explanation_data = self._generate_lime(
                        model_path, X_test, model['model_type']
                    )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # 5. Save explanation to Supabase
                explanation_record = {
                    'id': explanation_id,
                    'model_id': model_id,
                    'method': method.lower(),
                    'status': 'completed',
                    'sample_size': len(X_test),
                    'feature_importance': explanation_data.get('feature_importance'),
                    'explanation_data': explanation_data,
                    'completed_at': pd.Timestamp.now().isoformat()
                }
                
                supabase_db.create_explanation(explanation_record)
                
                logger.info("Explanation generated successfully",
                           explanation_id=explanation_id)
                
                return {
                    'status': 'success',
                    'explanation_id': explanation_id,
                    'method': method,
                    'feature_importance': explanation_data.get('feature_importance')
                }
                
            finally:
                # Cleanup
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
        
        except Exception as e:
            logger.error("Explanation generation failed",
                        explanation_id=explanation_id,
                        error=str(e),
                        exc_info=e)
            
            # Save error to database
            try:
                supabase_db.create_explanation({
                    'id': explanation_id,
                    'model_id': model_id,
                    'method': method.lower(),
                    'status': 'failed',
                    'error_message': str(e)
                })
            except:
                pass
            
            raise
    
    def _generate_shap(
        self,
        model_path: Path,
        X_test: pd.DataFrame,
        model_type: str
    ) -> Dict[str, Any]:
        """Generate SHAP explanations."""
        import pickle
        import shap
        
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Create explainer
        if model_type in ['xgboost', 'lightgbm', 'catboost']:
            explainer = shap.TreeExplainer(model)
        else:
            # Use KernelExplainer for other models (slower)
            background = shap.sample(X_test, min(100, len(X_test)))
            explainer = shap.KernelExplainer(model.predict_proba, background)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_test)
        
        # For binary classification, take positive class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Calculate feature importance (mean absolute SHAP values)
        feature_importance = {}
        for i, col in enumerate(X_test.columns):
            feature_importance[col] = float(np.abs(shap_values[:, i]).mean())
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            'feature_importance': feature_importance,
            'shap_values': shap_values.tolist(),
            'base_value': float(explainer.expected_value) if hasattr(explainer, 'expected_value') else 0.0,
            'feature_names': list(X_test.columns)
        }
    
    def _generate_lime(
        self,
        model_path: Path,
        X_test: pd.DataFrame,
        model_type: str
    ) -> Dict[str, Any]:
        """Generate LIME explanations."""
        import pickle
        from lime.lime_tabular import LimeTabularExplainer
        
        # Load model
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Create LIME explainer
        explainer = LimeTabularExplainer(
            X_test.values,
            feature_names=list(X_test.columns),
            class_names=['Non-Fraud', 'Fraud'],
            mode='classification'
        )
        
        # Generate explanations for a sample of instances
        sample_indices = np.random.choice(len(X_test), min(10, len(X_test)), replace=False)
        
        feature_importance = {}
        explanations = []
        
        for idx in sample_indices:
            exp = explainer.explain_instance(
                X_test.iloc[idx].values,
                model.predict_proba,
                num_features=10
            )
            
            # Aggregate feature importance
            for feature, weight in exp.as_list():
                feature_name = feature.split()[0]  # Extract feature name
                if feature_name in feature_importance:
                    feature_importance[feature_name] += abs(weight)
                else:
                    feature_importance[feature_name] = abs(weight)
            
            explanations.append({
                'instance_id': int(idx),
                'explanation': exp.as_list()
            })
        
        # Normalize feature importance
        total = sum(feature_importance.values())
        if total > 0:
            feature_importance = {k: v/total for k, v in feature_importance.items()}
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        return {
            'feature_importance': feature_importance,
            'explanations': explanations,
            'feature_names': list(X_test.columns)
        }


# Global service instance
explanation_service = ExplanationService()
