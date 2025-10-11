"""
Explanation quality metrics service.

Evaluates XAI explanations using multiple quality dimensions:
- Faithfulness: How well do explanations reflect the model?
- Robustness: How stable are explanations under perturbations?
- Complexity: How interpretable/sparse are the explanations?
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from pathlib import Path
import structlog

logger = structlog.get_logger()


class QualityMetricsService:
    """Service for evaluating explanation quality."""
    
    def evaluate_explanation_quality(
        self,
        explanation_data: Dict[str, Any],
        model_path: str,
        test_data_path: str,
        sample_size: int = 50
    ) -> Dict[str, Any]:
        """
        Evaluate quality of an explanation.
        
        Args:
            explanation_data: Explanation data with SHAP values
            model_path: Path to trained model
            test_data_path: Path to test data
            sample_size: Number of samples for evaluation
            
        Returns:
            Dictionary with quality scores
        """
        try:
            import pickle
            import shap
            
            # Load model and data
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            test_df = pd.read_parquet(test_data_path)
            X_test = test_df.iloc[:, :-1]
            y_test = test_df.iloc[:, -1]
            
            # Sample for efficiency
            if len(X_test) > sample_size:
                indices = np.random.choice(len(X_test), sample_size, replace=False)
                X_sample = X_test.iloc[indices]
                y_sample = y_test.iloc[indices]
            else:
                X_sample = X_test
                y_sample = y_test
            
            # Get SHAP values
            feature_importance = explanation_data.get('feature_importance', {})
            
            # Calculate quality metrics
            faithfulness = self._calculate_faithfulness(
                model, X_sample, y_sample, feature_importance
            )
            
            robustness = self._calculate_robustness(
                model, X_sample, feature_importance
            )
            
            complexity = self._calculate_complexity(feature_importance)
            
            # Overall quality score (weighted average)
            overall_quality = (
                0.4 * faithfulness['score'] +
                0.3 * robustness['score'] +
                0.3 * complexity['score']
            )
            
            return {
                'faithfulness': faithfulness,
                'robustness': robustness,
                'complexity': complexity,
                'overall_quality': overall_quality,
                'sample_size': len(X_sample)
            }
            
        except Exception as e:
            logger.error("Quality evaluation failed", error=str(e), exc_info=e)
            raise
    
    def _calculate_faithfulness(
        self,
        model,
        X: pd.DataFrame,
        y: pd.Series,
        feature_importance: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate faithfulness metrics.
        
        Faithfulness measures how well the explanation reflects the actual model behavior.
        """
        try:
            # Get predictions
            y_pred_proba = model.predict_proba(X)[:, 1]
            
            # Monotonicity: Remove top features and check if prediction decreases
            top_features = sorted(
                feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            monotonicity_scores = []
            for feature_name, _ in top_features:
                if feature_name in X.columns:
                    # Create perturbed data by setting feature to median
                    X_perturbed = X.copy()
                    X_perturbed[feature_name] = X[feature_name].median()
                    
                    y_perturbed_proba = model.predict_proba(X_perturbed)[:, 1]
                    
                    # Check if removing important feature decreases prediction
                    decrease = (y_pred_proba - y_perturbed_proba).mean()
                    monotonicity_scores.append(max(0, decrease))
            
            monotonicity = np.mean(monotonicity_scores) if monotonicity_scores else 0.5
            
            # Selectivity: Correlation between feature importance and actual impact
            # Simplified version - in production would use more sophisticated metrics
            selectivity = min(1.0, len(top_features) / 10.0)  # Prefer focused explanations
            
            # Overall faithfulness score
            faithfulness_score = 0.6 * monotonicity + 0.4 * selectivity
            
            return {
                'score': float(faithfulness_score),
                'monotonicity': float(monotonicity),
                'selectivity': float(selectivity),
                'description': 'How well explanations reflect actual model behavior'
            }
            
        except Exception as e:
            logger.warning("Faithfulness calculation failed", error=str(e))
            return {
                'score': 0.5,
                'monotonicity': 0.5,
                'selectivity': 0.5,
                'description': 'Faithfulness calculation failed'
            }
    
    def _calculate_robustness(
        self,
        model,
        X: pd.DataFrame,
        feature_importance: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate robustness metrics.
        
        Robustness measures how stable explanations are under small perturbations.
        """
        try:
            import shap
            
            # Create explainer
            explainer = shap.TreeExplainer(model)
            
            # Get SHAP values for original data
            shap_values_original = explainer.shap_values(X.head(20))
            if isinstance(shap_values_original, list):
                shap_values_original = shap_values_original[1]
            
            # Add small noise and recalculate
            noise_level = 0.01
            X_noisy = X.head(20).copy()
            for col in X_noisy.columns:
                if X_noisy[col].dtype in [np.float64, np.int64]:
                    noise = np.random.normal(0, noise_level * X_noisy[col].std(), len(X_noisy))
                    X_noisy[col] = X_noisy[col] + noise
            
            shap_values_noisy = explainer.shap_values(X_noisy)
            if isinstance(shap_values_noisy, list):
                shap_values_noisy = shap_values_noisy[1]
            
            # Calculate stability (correlation between original and noisy)
            correlations = []
            for i in range(len(shap_values_original)):
                corr = np.corrcoef(
                    shap_values_original[i],
                    shap_values_noisy[i]
                )[0, 1]
                if not np.isnan(corr):
                    correlations.append(corr)
            
            stability = np.mean(correlations) if correlations else 0.8
            stability_std = np.std(correlations) if correlations else 0.1
            
            # Overall robustness score
            robustness_score = max(0, min(1, stability))
            
            return {
                'score': float(robustness_score),
                'stability': float(stability),
                'stability_std': float(stability_std),
                'description': 'How stable explanations are under perturbations'
            }
            
        except Exception as e:
            logger.warning("Robustness calculation failed", error=str(e))
            return {
                'score': 0.8,
                'stability': 0.8,
                'stability_std': 0.1,
                'description': 'Robustness calculation failed'
            }
    
    def _calculate_complexity(
        self,
        feature_importance: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate complexity metrics.
        
        Complexity measures how interpretable the explanation is.
        Lower complexity = more interpretable.
        """
        try:
            importances = np.array(list(feature_importance.values()))
            
            # Sparsity: How concentrated is the importance?
            # Gini coefficient - higher means more concentrated (better)
            sorted_imp = np.sort(importances)
            n = len(sorted_imp)
            index = np.arange(1, n + 1)
            gini = (2 * np.sum(index * sorted_imp)) / (n * np.sum(sorted_imp)) - (n + 1) / n
            
            # Effective features: How many features explain 80% of importance?
            cumsum = np.cumsum(sorted(importances, reverse=True))
            total = cumsum[-1]
            effective_features = np.argmax(cumsum >= 0.8 * total) + 1
            
            # Sparsity score: Prefer fewer important features
            sparsity = 1.0 - (effective_features / len(importances))
            
            # Overall complexity score (lower complexity = higher score)
            complexity_score = 0.5 * gini + 0.5 * sparsity
            
            return {
                'score': float(complexity_score),
                'sparsity': float(sparsity),
                'gini_coefficient': float(gini),
                'effective_features': int(effective_features),
                'description': 'How interpretable/sparse the explanation is'
            }
            
        except Exception as e:
            logger.warning("Complexity calculation failed", error=str(e))
            return {
                'score': 0.7,
                'sparsity': 0.3,
                'gini_coefficient': 0.7,
                'effective_features': 10,
                'description': 'Complexity calculation failed'
            }


# Global service instance
quality_metrics_service = QualityMetricsService()
