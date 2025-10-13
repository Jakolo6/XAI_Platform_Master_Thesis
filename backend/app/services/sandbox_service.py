"""
Sandbox service for interactive XAI exploration.
Provides sample instances and explanations for the Explainability Sandbox.
"""

import numpy as np
import pandas as pd
import shap
import lime
import lime.lime_tabular
import joblib
import random
import structlog
import tempfile
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path

from app.utils.supabase_client import supabase_db
from app.utils.r2_storage import r2_storage_client

logger = structlog.get_logger()


class SandboxService:
    """Service for Explainability Sandbox operations"""
    
    @staticmethod
    def _load_test_data(dataset_id: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load test data for a dataset from R2 storage"""
        try:
            # Download from R2 storage
            with tempfile.TemporaryDirectory() as temp_dir:
                test_path = Path(temp_dir) / "test.parquet"
                r2_path = f"datasets/{dataset_id}/processed/test.parquet"
                
                logger.info("Downloading test data from R2", 
                           dataset_id=dataset_id,
                           r2_path=r2_path)
                
                if not r2_storage_client.download_file(r2_path, str(test_path)):
                    raise FileNotFoundError(f"Test data not found for model {dataset_id}. Please ensure dataset is processed.")
                
                # Load parquet file
                df = pd.read_parquet(test_path)
                
                # Separate features and target
                target_col = 'isFraud' if 'isFraud' in df.columns else 'target'
                if target_col not in df.columns:
                    # Try to find target column
                    possible_targets = ['label', 'class', 'y', 'TARGET']
                    for col in possible_targets:
                        if col in df.columns:
                            target_col = col
                            break
                
                if target_col not in df.columns:
                    raise ValueError(f"Could not find target column in test data. Columns: {df.columns.tolist()}")
                
                X_test = df.drop(columns=[target_col])
                y_test = df[target_col]
                
                logger.info("Test data loaded", 
                           n_samples=len(X_test), 
                           n_features=len(X_test.columns))
                
                return X_test, y_test
            
        except Exception as e:
            logger.error("Failed to load test data", 
                        dataset_id=dataset_id, 
                        error=str(e))
            raise
    
    @staticmethod
    def _load_model(model_id: str, model_path_r2: str) -> Any:
        """Load trained model from R2 storage"""
        try:
            # Download from R2 storage
            with tempfile.TemporaryDirectory() as temp_dir:
                model_path = Path(temp_dir) / f"{model_id}.pkl"
                
                logger.info("Downloading model from R2", 
                           model_id=model_id,
                           r2_path=model_path_r2)
                
                if not r2_storage_client.download_file(model_path_r2, str(model_path)):
                    raise FileNotFoundError(f"Model file not found: {model_id}")
                
                logger.info("Loading model", model_id=model_id)
                model = joblib.load(model_path)
                
                return model
            
        except Exception as e:
            logger.error("Failed to load model", model_id=model_id, error=str(e))
            raise
    
    @staticmethod
    def get_sample_instance(model_id: str) -> Dict[str, Any]:
        """Get a random test sample with prediction"""
        
        try:
            # Get model from database using the get_model method which handles _metrics suffix
            if not supabase_db.is_available():
                raise ValueError("Supabase not available")
            
            model_data = supabase_db.get_model(model_id)
            
            if not model_data:
                raise ValueError(f"Model {model_id} not found in database")
            
            dataset_id = model_data['dataset_id']
            model_path = model_data['model_path']
            
            logger.info("Getting sample instance", 
                       model_id=model_id, 
                       dataset_id=dataset_id)
            
            # Load test data
            X_test, y_test = SandboxService._load_test_data(dataset_id)
            
            # Select random sample
            random_idx = random.randint(0, len(X_test) - 1)
            sample = X_test.iloc[random_idx]
            true_label = y_test.iloc[random_idx]
            
            # Load trained model
            loaded_model = SandboxService._load_model(model_id, model_path)
            
            # Get prediction
            prediction_proba = loaded_model.predict_proba([sample.values])[0][1]
            prediction_class = 1 if prediction_proba > 0.5 else 0
            
            # Determine output label
            if 'fraud' in dataset_id.lower():
                model_output = "Fraud" if prediction_class == 1 else "Not Fraud"
                true_output = "Fraud" if true_label == 1 else "Not Fraud"
            else:
                model_output = f"Class {prediction_class}"
                true_output = f"Class {int(true_label)}"
            
            # Convert sample to dict, handling different data types
            features_dict = {}
            for key, value in sample.items():
                if pd.isna(value):
                    features_dict[key] = None
                elif isinstance(value, (np.integer, np.int64)):
                    features_dict[key] = int(value)
                elif isinstance(value, (np.floating, np.float64)):
                    features_dict[key] = float(value)
                else:
                    features_dict[key] = str(value)
            
            result = {
                "instance_id": f"sample_{random_idx}",
                "features": features_dict,
                "prediction": float(prediction_proba),
                "model_output": model_output,
                "true_label": true_output
            }
            
            logger.info("Sample instance created", 
                       instance_id=result["instance_id"],
                       prediction=result["prediction"])
            
            return result
            
        except Exception as e:
            logger.error("Failed to get sample instance", 
                        model_id=model_id, 
                        error=str(e))
            raise
    
    @staticmethod
    def generate_shap_explanation(
        model_id: str,
        instance_id: str
    ) -> Dict[str, Any]:
        """Generate SHAP explanation for a specific instance"""
        
        try:
            # Get model from database
            if not supabase_db.is_available():
                raise ValueError("Supabase not available")
            
            result = supabase_db.client.table('models').select('*').eq('id', model_id).execute()
            
            if not result.data or len(result.data) == 0:
                raise ValueError(f"Model {model_id} not found")
            
            model_data = result.data[0]
            dataset_id = model_data['dataset_id']
            model_path = model_data['model_path']
            
            logger.info("Generating SHAP explanation", 
                       model_id=model_id, 
                       instance_id=instance_id)
            
            # Load test data
            X_test, y_test = SandboxService._load_test_data(dataset_id)
            
            # Get sample
            sample_idx = int(instance_id.split("_")[1])
            sample = X_test.iloc[sample_idx]
            
            # Load trained model
            loaded_model = SandboxService._load_model(model_id, model_path)
            
            # Get prediction
            prediction_proba = loaded_model.predict_proba([sample.values])[0][1]
            
            # Generate SHAP explanation
            explainer = shap.TreeExplainer(loaded_model)
            shap_values = explainer.shap_values(sample.values.reshape(1, -1))
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                shap_values_class = shap_values[1][0]  # For binary classification
                base_value = float(explainer.expected_value[1])
            else:
                shap_values_class = shap_values[0]
                base_value = float(explainer.expected_value)
            
            # Create feature contributions
            features = []
            for i, (feature_name, feature_value) in enumerate(sample.items()):
                contribution = float(shap_values_class[i])
                
                # Handle different value types
                if pd.isna(feature_value):
                    value = None
                elif isinstance(feature_value, (np.integer, np.int64)):
                    value = int(feature_value)
                elif isinstance(feature_value, (np.floating, np.float64)):
                    value = float(feature_value)
                else:
                    value = str(feature_value)
                
                features.append({
                    "feature": feature_name,
                    "value": value,
                    "contribution": contribution,
                    "importance": abs(contribution)
                })
            
            # Sort by importance
            features.sort(key=lambda x: x["importance"], reverse=True)
            
            result = {
                "method": "shap",
                "prediction_proba": float(prediction_proba),
                "base_value": base_value,
                "features": features
            }
            
            logger.info("SHAP explanation generated", 
                       instance_id=instance_id,
                       n_features=len(features))
            
            return result
            
        except Exception as e:
            logger.error("Failed to generate SHAP explanation", 
                        model_id=model_id, 
                        instance_id=instance_id,
                        error=str(e))
            raise
    
    @staticmethod
    def generate_lime_explanation(
        model_id: str,
        instance_id: str
    ) -> Dict[str, Any]:
        """Generate LIME explanation for a specific instance"""
        
        try:
            # Get model from database
            if not supabase_db.is_available():
                raise ValueError("Supabase not available")
            
            result = supabase_db.client.table('models').select('*').eq('id', model_id).execute()
            
            if not result.data or len(result.data) == 0:
                raise ValueError(f"Model {model_id} not found")
            
            model_data = result.data[0]
            dataset_id = model_data['dataset_id']
            model_path = model_data['model_path']
            
            logger.info("Generating LIME explanation", 
                       model_id=model_id, 
                       instance_id=instance_id)
            
            # Load test data
            X_test, y_test = SandboxService._load_test_data(dataset_id)
            
            # Get sample
            sample_idx = int(instance_id.split("_")[1])
            sample = X_test.iloc[sample_idx]
            
            # Load trained model
            loaded_model = SandboxService._load_model(model_id, model_path)
            
            # Get prediction
            prediction_proba = loaded_model.predict_proba([sample.values])[0][1]
            
            # Generate LIME explanation
            explainer = lime.lime_tabular.LimeTabularExplainer(
                X_test.values,
                feature_names=X_test.columns.tolist(),
                class_names=['Not Fraud', 'Fraud'],
                mode='classification'
            )
            
            exp = explainer.explain_instance(
                sample.values,
                loaded_model.predict_proba,
                num_features=len(sample)
            )
            
            # Create feature contributions
            features = []
            lime_dict = dict(exp.as_list())
            
            for i, (feature_name, feature_value) in enumerate(sample.items()):
                # Find contribution in LIME output
                contribution = 0.0
                for lime_feature, lime_contrib in lime_dict.items():
                    if feature_name in lime_feature:
                        contribution = lime_contrib
                        break
                
                # Handle different value types
                if pd.isna(feature_value):
                    value = None
                elif isinstance(feature_value, (np.integer, np.int64)):
                    value = int(feature_value)
                elif isinstance(feature_value, (np.floating, np.float64)):
                    value = float(feature_value)
                else:
                    value = str(feature_value)
                
                features.append({
                    "feature": feature_name,
                    "value": value,
                    "contribution": float(contribution),
                    "importance": abs(float(contribution))
                })
            
            # Sort by importance
            features.sort(key=lambda x: x["importance"], reverse=True)
            
            result = {
                "method": "lime",
                "prediction_proba": float(prediction_proba),
                "features": features
            }
            
            logger.info("LIME explanation generated", 
                       instance_id=instance_id,
                       n_features=len(features))
            
            return result
            
        except Exception as e:
            logger.error("Failed to generate LIME explanation", 
                        model_id=model_id, 
                        instance_id=instance_id,
                        error=str(e))
            raise


# Create singleton instance
sandbox_service = SandboxService()
