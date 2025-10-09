"""
SHAP (SHapley Additive exPlanations) explainer for model interpretability.
"""

import shap
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import Dict, List, Any, Optional
import structlog

logger = structlog.get_logger()


class ShapExplainer:
    """
    SHAP explainer for generating feature importance and explanations.
    Supports tree-based models (XGBoost, LightGBM, CatBoost, Random Forest).
    """
    
    def __init__(self, model_path: str, model_type: str):
        """
        Initialize SHAP explainer.
        
        Args:
            model_path: Path to the trained model file
            model_type: Type of model (xgboost, lightgbm, catboost, random_forest, etc.)
        """
        self.model_path = Path(model_path)
        self.model_type = model_type
        self.model = None
        self.explainer = None
        self.feature_names = None
        
        self._load_model()
        
    def _load_model(self):
        """Load the trained model from disk."""
        try:
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            logger.info("Model loaded successfully", model_path=str(self.model_path))
        except Exception as e:
            logger.error("Failed to load model", error=str(e))
            raise
    
    def initialize_explainer(self, background_data: pd.DataFrame):
        """
        Initialize SHAP explainer with background data.
        
        Args:
            background_data: Sample of training data for background distribution
        """
        self.feature_names = background_data.columns.tolist()
        
        try:
            if self.model_type in ['xgboost', 'lightgbm', 'catboost', 'random_forest']:
                # Use TreeExplainer for tree-based models (faster and more accurate)
                self.explainer = shap.TreeExplainer(self.model)
                logger.info("TreeExplainer initialized", model_type=self.model_type)
            else:
                # Use KernelExplainer for other models (slower but model-agnostic)
                self.explainer = shap.KernelExplainer(
                    self.model.predict_proba,
                    background_data.sample(min(100, len(background_data)))
                )
                logger.info("KernelExplainer initialized", model_type=self.model_type)
        except Exception as e:
            logger.error("Failed to initialize explainer", error=str(e))
            raise
    
    def explain_instance(self, instance: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate SHAP explanation for a single instance.
        
        Args:
            instance: Single row DataFrame with features
            
        Returns:
            Dictionary containing SHAP values and explanation data
        """
        if self.explainer is None:
            raise ValueError("Explainer not initialized. Call initialize_explainer first.")
        
        try:
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(instance)
            
            # Handle different output formats
            if isinstance(shap_values, list):
                # Binary classification - take positive class
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # Get base value (expected value)
            if hasattr(self.explainer, 'expected_value'):
                base_value = self.explainer.expected_value
                if isinstance(base_value, (list, np.ndarray)):
                    base_value = base_value[1] if len(base_value) > 1 else base_value[0]
            else:
                base_value = 0.0
            
            # Get prediction
            if hasattr(self.model, 'predict_proba'):
                prediction = self.model.predict_proba(instance)[0]
                predicted_class = int(np.argmax(prediction))
                predicted_proba = float(prediction[predicted_class])
            else:
                prediction = self.model.predict(instance)[0]
                predicted_class = int(prediction)
                predicted_proba = 1.0
            
            # Create feature contributions
            feature_contributions = []
            for i, feature_name in enumerate(self.feature_names):
                contribution = {
                    'feature': feature_name,
                    'value': float(instance[feature_name].iloc[0]),
                    'shap_value': float(shap_values[0][i]),
                    'abs_shap_value': abs(float(shap_values[0][i]))
                }
                feature_contributions.append(contribution)
            
            # Sort by absolute SHAP value (most important first)
            feature_contributions.sort(key=lambda x: x['abs_shap_value'], reverse=True)
            
            return {
                'prediction': {
                    'class': predicted_class,
                    'probability': predicted_proba,
                    'label': 'Fraud' if predicted_class == 1 else 'Legitimate'
                },
                'base_value': float(base_value),
                'feature_contributions': feature_contributions,
                'top_features': feature_contributions[:10],  # Top 10 most important
                'shap_values': shap_values[0].tolist(),
                'feature_values': instance.iloc[0].tolist(),
                'feature_names': self.feature_names
            }
            
        except Exception as e:
            logger.error("Failed to generate explanation", error=str(e))
            raise
    
    def get_global_feature_importance(self, data: pd.DataFrame, max_samples: int = 1000) -> Dict[str, Any]:
        """
        Calculate global feature importance across multiple samples.
        
        Args:
            data: DataFrame with features
            max_samples: Maximum number of samples to use
            
        Returns:
            Dictionary with global feature importance
        """
        if self.explainer is None:
            raise ValueError("Explainer not initialized. Call initialize_explainer first.")
        
        try:
            # Sample data if too large
            if len(data) > max_samples:
                data_sample = data.sample(max_samples, random_state=42)
            else:
                data_sample = data
            
            # Calculate SHAP values
            shap_values = self.explainer.shap_values(data_sample)
            
            # Handle different output formats
            if isinstance(shap_values, list):
                shap_values = shap_values[1] if len(shap_values) > 1 else shap_values[0]
            
            # Calculate mean absolute SHAP values
            mean_abs_shap = np.abs(shap_values).mean(axis=0)
            
            # Create feature importance list
            feature_importance = []
            for i, feature_name in enumerate(self.feature_names):
                feature_importance.append({
                    'feature': feature_name,
                    'importance': float(mean_abs_shap[i]),
                    'rank': i + 1
                })
            
            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            # Update ranks
            for i, item in enumerate(feature_importance):
                item['rank'] = i + 1
            
            return {
                'feature_importance': feature_importance,
                'top_features': feature_importance[:20],  # Top 20
                'num_samples': len(data_sample),
                'num_features': len(self.feature_names)
            }
            
        except Exception as e:
            logger.error("Failed to calculate global importance", error=str(e))
            raise
    
    def explain_batch(self, instances: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Generate explanations for multiple instances.
        
        Args:
            instances: DataFrame with multiple rows
            
        Returns:
            List of explanation dictionaries
        """
        explanations = []
        for idx in range(len(instances)):
            instance = instances.iloc[[idx]]
            explanation = self.explain_instance(instance)
            explanation['instance_id'] = idx
            explanations.append(explanation)
        
        return explanations
