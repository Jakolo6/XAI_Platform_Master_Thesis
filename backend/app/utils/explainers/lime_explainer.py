"""
LIME (Local Interpretable Model-agnostic Explanations) explainer for tabular data.
"""

from lime.lime_tabular import LimeTabularExplainer
import numpy as np
import pandas as pd
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


class LimeExplainer:
    """
    LIME explainer for tabular fraud detection models.
    
    LIME explains individual predictions by fitting interpretable models
    locally around the prediction.
    """
    
    def __init__(self, model, feature_names: List[str], training_data: pd.DataFrame):
        """
        Initialize LIME explainer.
        
        Args:
            model: Trained model with predict_proba method
            feature_names: List of feature names
            training_data: Training data for generating perturbations
        """
        self.model = model
        self.feature_names = feature_names
        
        logger.info("Initializing LIME explainer", 
                   num_features=len(feature_names),
                   training_samples=len(training_data))
        
        # Initialize LIME explainer
        self.explainer = LimeTabularExplainer(
            training_data=training_data.values,
            feature_names=feature_names,
            class_names=['Legitimate', 'Fraud'],
            mode='classification',
            discretize_continuous=True,
            random_state=42
        )
        
        logger.info("LIME explainer initialized successfully")
    
    def explain_instance(self, instance: pd.DataFrame, num_features: int = 20) -> Dict[str, Any]:
        """
        Explain a single instance using LIME.
        
        Args:
            instance: Single row DataFrame to explain
            num_features: Number of top features to return
            
        Returns:
            Dictionary with explanation results
        """
        logger.info("Generating LIME explanation for instance")
        
        # Generate explanation
        exp = self.explainer.explain_instance(
            instance.values[0],
            self.model.predict_proba,
            num_features=num_features,
            top_labels=1
        )
        
        # Get explanation for fraud class (class 1)
        exp_list = exp.as_list(label=1)
        
        # Convert to our format
        feature_importance = []
        for feature_desc, weight in exp_list:
            # Extract feature name (before <= or > symbol)
            feature_name = feature_desc.split('<=')[0].split('>')[0].strip()
            
            feature_importance.append({
                'feature': feature_name,
                'importance': abs(weight),
                'direction': 'positive' if weight > 0 else 'negative',
                'weight': float(weight),
                'description': feature_desc
            })
        
        # Get prediction probabilities
        prediction_proba = self.model.predict_proba(instance)[0]
        
        result = {
            'method': 'lime',
            'feature_importance': feature_importance,
            'prediction': {
                'class': int(np.argmax(prediction_proba)),
                'probability': float(prediction_proba[1]),  # Fraud probability
                'label': 'Fraud' if np.argmax(prediction_proba) == 1 else 'Legitimate'
            },
            'num_features': len(feature_importance)
        }
        
        logger.info("LIME explanation generated", 
                   num_features=len(feature_importance),
                   prediction=result['prediction']['label'])
        
        return result
    
    def get_global_feature_importance(
        self, 
        data: pd.DataFrame, 
        num_samples: int = 1000,
        num_features: int = 20
    ) -> Dict[str, Any]:
        """
        Aggregate LIME explanations across multiple samples to get global importance.
        
        Args:
            data: DataFrame of samples to explain
            num_samples: Number of samples to explain
            num_features: Number of features to consider per explanation
            
        Returns:
            Dictionary with global feature importance
        """
        logger.info("Generating global LIME feature importance",
                   num_samples=num_samples,
                   num_features=num_features)
        
        # Sample data
        sample_data = data.sample(min(num_samples, len(data)), random_state=42)
        
        # Initialize importance aggregation
        feature_importances = {f: [] for f in self.feature_names}
        feature_directions = {f: {'positive': 0, 'negative': 0} for f in self.feature_names}
        
        # Generate explanations for each sample
        for idx in range(len(sample_data)):
            if idx % 100 == 0:
                logger.info(f"Processing sample {idx}/{len(sample_data)}")
            
            instance = sample_data.iloc[[idx]]
            
            try:
                exp = self.explain_instance(instance, num_features=len(self.feature_names))
                
                # Aggregate importances
                for item in exp['feature_importance']:
                    feature = item['feature']
                    if feature in feature_importances:
                        feature_importances[feature].append(item['importance'])
                        if item['direction'] == 'positive':
                            feature_directions[feature]['positive'] += 1
                        else:
                            feature_directions[feature]['negative'] += 1
            except Exception as e:
                logger.warning(f"Failed to explain sample {idx}: {e}")
                continue
        
        # Calculate global importance
        global_importance = []
        for feature, importances in feature_importances.items():
            if importances:
                mean_importance = np.mean(importances)
                std_importance = np.std(importances)
                
                # Determine overall direction
                pos_count = feature_directions[feature]['positive']
                neg_count = feature_directions[feature]['negative']
                overall_direction = 'positive' if pos_count > neg_count else 'negative'
                
                global_importance.append({
                    'feature': feature,
                    'importance': float(mean_importance),
                    'std': float(std_importance),
                    'direction': overall_direction,
                    'positive_count': pos_count,
                    'negative_count': neg_count,
                    'rank': 0  # Will be set after sorting
                })
        
        # Sort by importance
        global_importance.sort(key=lambda x: x['importance'], reverse=True)
        
        # Add ranks
        for i, item in enumerate(global_importance):
            item['rank'] = i + 1
        
        result = {
            'method': 'lime',
            'feature_importance': global_importance,
            'num_samples': len(sample_data),
            'num_features': len(global_importance)
        }
        
        logger.info("Global LIME feature importance generated",
                   num_features=len(global_importance),
                   top_feature=global_importance[0]['feature'] if global_importance else None)
        
        return result
    
    def compare_with_shap(self, shap_importance: List[Dict], lime_importance: List[Dict]) -> Dict[str, Any]:
        """
        Compare LIME and SHAP feature importance rankings.
        
        Args:
            shap_importance: SHAP feature importance list
            lime_importance: LIME feature importance list
            
        Returns:
            Comparison metrics
        """
        # Create feature to rank mappings
        shap_ranks = {item['feature']: item['rank'] for item in shap_importance}
        lime_ranks = {item['feature']: item['rank'] for item in lime_importance}
        
        # Find common features
        common_features = set(shap_ranks.keys()) & set(lime_ranks.keys())
        
        # Calculate rank correlation (Spearman)
        shap_rank_list = [shap_ranks[f] for f in common_features]
        lime_rank_list = [lime_ranks[f] for f in common_features]
        
        from scipy.stats import spearmanr
        correlation, p_value = spearmanr(shap_rank_list, lime_rank_list)
        
        # Find top-k agreement
        top_k_values = [5, 10, 20]
        top_k_agreement = {}
        
        for k in top_k_values:
            shap_top_k = set([item['feature'] for item in shap_importance[:k]])
            lime_top_k = set([item['feature'] for item in lime_importance[:k]])
            agreement = len(shap_top_k & lime_top_k) / k
            top_k_agreement[f'top_{k}'] = float(agreement)
        
        return {
            'rank_correlation': float(correlation),
            'p_value': float(p_value),
            'top_k_agreement': top_k_agreement,
            'num_common_features': len(common_features)
        }
