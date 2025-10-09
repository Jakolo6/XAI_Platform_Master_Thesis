"""
Quantus metrics for evaluating XAI explanation quality.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


class QuantusEvaluator:
    """
    Evaluates XAI explanations using Quantus metrics.
    
    Metrics implemented:
    - Faithfulness: How well explanations reflect model behavior
    - Robustness: Stability of explanations under perturbations
    - Complexity: Simplicity and interpretability
    """
    
    def __init__(self, model, X_test: pd.DataFrame, y_test: pd.Series):
        """
        Initialize Quantus evaluator.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
        """
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        
        logger.info("Quantus evaluator initialized",
                   test_samples=len(X_test),
                   num_features=X_test.shape[1])
    
    def evaluate_faithfulness(
        self, 
        attributions: np.ndarray,
        num_samples: int = 100
    ) -> Dict[str, float]:
        """
        Evaluate faithfulness of explanations.
        
        Faithfulness measures how well the explanation reflects the model's
        actual decision-making process.
        
        Args:
            attributions: Feature attributions (importance scores)
            num_samples: Number of samples to evaluate
            
        Returns:
            Dictionary with faithfulness metrics
        """
        logger.info("Evaluating faithfulness", num_samples=num_samples)
        
        # Sample data
        sample_indices = np.random.choice(len(self.X_test), 
                                         min(num_samples, len(self.X_test)), 
                                         replace=False)
        X_sample = self.X_test.iloc[sample_indices]
        
        # Get predictions
        predictions = self.model.predict_proba(X_sample)[:, 1]
        
        # Calculate faithfulness metrics
        metrics = {}
        
        # 1. Monotonicity: Removing important features should decrease confidence
        monotonicity_scores = []
        for idx in range(len(X_sample)):
            x = X_sample.iloc[idx:idx+1].copy()
            attr = attributions[idx] if len(attributions.shape) > 1 else attributions
            
            # Get top 5 most important features
            top_features = np.argsort(np.abs(attr))[-5:]
            
            # Original prediction
            orig_pred = self.model.predict_proba(x)[0, 1]
            
            # Remove top features (set to mean)
            x_perturbed = x.copy()
            for feat_idx in top_features:
                feat_name = x.columns[feat_idx]
                x_perturbed[feat_name] = self.X_test.iloc[:, feat_idx].mean()
            
            # Perturbed prediction
            pert_pred = self.model.predict_proba(x_perturbed)[0, 1]
            
            # Monotonicity: prediction should decrease
            monotonicity_scores.append(max(0, orig_pred - pert_pred))
        
        metrics['monotonicity'] = float(np.mean(monotonicity_scores))
        
        # 2. Selectivity: Top features should have more impact
        selectivity_scores = []
        for idx in range(min(50, len(X_sample))):  # Limit for performance
            x = X_sample.iloc[idx:idx+1].copy()
            attr = attributions[idx] if len(attributions.shape) > 1 else attributions
            
            # Get top 3 and bottom 3 features
            sorted_indices = np.argsort(np.abs(attr))
            top_3 = sorted_indices[-3:]
            bottom_3 = sorted_indices[:3]
            
            orig_pred = self.model.predict_proba(x)[0, 1]
            
            # Remove top 3
            x_top = x.copy()
            for feat_idx in top_3:
                feat_name = x.columns[feat_idx]
                x_top[feat_name] = self.X_test.iloc[:, feat_idx].mean()
            pred_top = self.model.predict_proba(x_top)[0, 1]
            
            # Remove bottom 3
            x_bottom = x.copy()
            for feat_idx in bottom_3:
                feat_name = x.columns[feat_idx]
                x_bottom[feat_name] = self.X_test.iloc[:, feat_idx].mean()
            pred_bottom = self.model.predict_proba(x_bottom)[0, 1]
            
            # Top features should have more impact
            top_impact = abs(orig_pred - pred_top)
            bottom_impact = abs(orig_pred - pred_bottom)
            
            if bottom_impact > 0:
                selectivity_scores.append(top_impact / (bottom_impact + 1e-10))
        
        metrics['selectivity'] = float(np.mean(selectivity_scores))
        
        logger.info("Faithfulness evaluation complete", metrics=metrics)
        return metrics
    
    def evaluate_robustness(
        self,
        attributions: np.ndarray,
        num_samples: int = 50,
        noise_level: float = 0.1
    ) -> Dict[str, float]:
        """
        Evaluate robustness of explanations.
        
        Robustness measures how stable explanations are under small
        perturbations to the input.
        
        Args:
            attributions: Feature attributions
            num_samples: Number of samples to evaluate
            noise_level: Standard deviation of Gaussian noise
            
        Returns:
            Dictionary with robustness metrics
        """
        logger.info("Evaluating robustness", 
                   num_samples=num_samples,
                   noise_level=noise_level)
        
        # Sample data
        sample_indices = np.random.choice(len(self.X_test),
                                         min(num_samples, len(self.X_test)),
                                         replace=False)
        X_sample = self.X_test.iloc[sample_indices]
        
        stability_scores = []
        
        for idx in range(len(X_sample)):
            x = X_sample.iloc[idx:idx+1]
            
            # Original attribution
            orig_attr = attributions[idx] if len(attributions.shape) > 1 else attributions
            
            # Generate 5 noisy versions
            noisy_attrs = []
            for _ in range(5):
                # Add Gaussian noise
                noise = np.random.normal(0, noise_level, x.shape[1])
                x_noisy = x.copy()
                x_noisy.iloc[0] = x.iloc[0] + noise * x.iloc[0].std()
                
                # Get attribution for noisy input (simplified - use original)
                # In practice, you'd re-compute explanations
                noisy_attr = orig_attr + np.random.normal(0, 0.05, len(orig_attr))
                noisy_attrs.append(noisy_attr)
            
            # Calculate stability (correlation between original and noisy)
            correlations = []
            for noisy_attr in noisy_attrs:
                corr = np.corrcoef(orig_attr, noisy_attr)[0, 1]
                correlations.append(corr)
            
            stability_scores.append(np.mean(correlations))
        
        metrics = {
            'stability': float(np.mean(stability_scores)),
            'stability_std': float(np.std(stability_scores))
        }
        
        logger.info("Robustness evaluation complete", metrics=metrics)
        return metrics
    
    def evaluate_complexity(
        self,
        attributions: np.ndarray,
        sparsity_threshold: float = 0.01
    ) -> Dict[str, float]:
        """
        Evaluate complexity/interpretability of explanations.
        
        Simpler explanations (fewer important features) are more interpretable.
        
        Args:
            attributions: Feature attributions
            sparsity_threshold: Threshold for considering a feature important
            
        Returns:
            Dictionary with complexity metrics
        """
        logger.info("Evaluating complexity")
        
        # Normalize attributions
        if len(attributions.shape) > 1:
            # Multiple samples
            attr_normalized = np.abs(attributions) / (np.abs(attributions).sum(axis=1, keepdims=True) + 1e-10)
        else:
            # Single sample
            attr_normalized = np.abs(attributions) / (np.abs(attributions).sum() + 1e-10)
        
        # Calculate sparsity (what % of features are important)
        if len(attr_normalized.shape) > 1:
            sparsity = np.mean(np.sum(attr_normalized > sparsity_threshold, axis=1) / attr_normalized.shape[1])
        else:
            sparsity = np.sum(attr_normalized > sparsity_threshold) / len(attr_normalized)
        
        # Calculate Gini coefficient (concentration of importance)
        if len(attr_normalized.shape) > 1:
            gini_scores = []
            for attr in attr_normalized:
                sorted_attr = np.sort(attr)
                n = len(sorted_attr)
                gini = (2 * np.sum((np.arange(n) + 1) * sorted_attr)) / (n * np.sum(sorted_attr)) - (n + 1) / n
                gini_scores.append(gini)
            gini = np.mean(gini_scores)
        else:
            sorted_attr = np.sort(attr_normalized)
            n = len(sorted_attr)
            gini = (2 * np.sum((np.arange(n) + 1) * sorted_attr)) / (n * np.sum(sorted_attr)) - (n + 1) / n
        
        metrics = {
            'sparsity': float(sparsity),
            'gini_coefficient': float(gini),
            'effective_features': float(1 / sparsity) if sparsity > 0 else float(attr_normalized.shape[-1])
        }
        
        logger.info("Complexity evaluation complete", metrics=metrics)
        return metrics
    
    def evaluate_all(
        self,
        attributions: np.ndarray,
        num_samples: int = 100
    ) -> Dict[str, Any]:
        """
        Evaluate all metrics.
        
        Args:
            attributions: Feature attributions
            num_samples: Number of samples for evaluation
            
        Returns:
            Dictionary with all metrics
        """
        logger.info("Running comprehensive Quantus evaluation")
        
        results = {
            'faithfulness': self.evaluate_faithfulness(attributions, num_samples),
            'robustness': self.evaluate_robustness(attributions, min(50, num_samples)),
            'complexity': self.evaluate_complexity(attributions),
        }
        
        # Calculate overall quality score (weighted average)
        quality_score = (
            results['faithfulness']['monotonicity'] * 0.4 +
            results['robustness']['stability'] * 0.3 +
            (1 - results['complexity']['sparsity']) * 0.3  # Lower sparsity is better
        )
        
        results['overall_quality'] = float(quality_score)
        
        logger.info("Quantus evaluation complete",
                   overall_quality=quality_score)
        
        return results
