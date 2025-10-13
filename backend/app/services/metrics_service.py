"""
Centralized Metrics Service
============================

Single source of truth for all model metrics.
Ensures model retraining, display pages, and reports use the same data.
"""

from typing import Dict, Any, List, Optional, Tuple
import numpy as np
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
    log_loss,
    brier_score_loss,
    confusion_matrix,
    roc_curve,
    precision_recall_curve
)
import structlog

from app.core.base_service import ModelServiceBase

logger = structlog.get_logger(__name__)


class MetricsService(ModelServiceBase):
    """
    Centralized service for computing and storing model metrics.
    
    All metric computation goes through this service to ensure consistency.
    """
    
    def __init__(self):
        super().__init__(service_name="metrics_service")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get metrics service status."""
        return {
            "service": self.service_name,
            "status": "operational",
            "dal_available": self.dal.db.is_available()
        }
    
    def compute_all_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Compute all standard metrics for a model.
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            y_pred_proba: Predicted probabilities (optional, for probabilistic metrics)
            
        Returns:
            Dictionary with all computed metrics
        """
        self._log_operation("compute_all_metrics", samples=len(y_true))
        
        try:
            metrics = {}
            
            # Basic classification metrics
            metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
            metrics['precision'] = float(precision_score(y_true, y_pred, average='binary', zero_division=0))
            metrics['recall'] = float(recall_score(y_true, y_pred, average='binary', zero_division=0))
            metrics['f1_score'] = float(f1_score(y_true, y_pred, average='binary', zero_division=0))
            
            # Confusion matrix
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
            metrics['confusion_matrix'] = {
                'tn': int(tn),
                'fp': int(fp),
                'fn': int(fn),
                'tp': int(tp)
            }
            
            # Probabilistic metrics (if probabilities provided)
            if y_pred_proba is not None:
                try:
                    metrics['auc_roc'] = float(roc_auc_score(y_true, y_pred_proba))
                    metrics['auc_pr'] = float(average_precision_score(y_true, y_pred_proba))
                    metrics['log_loss'] = float(log_loss(y_true, y_pred_proba))
                    metrics['brier_score'] = float(brier_score_loss(y_true, y_pred_proba))
                    
                    # Calibration metrics
                    calibration_metrics = self._compute_calibration_metrics(y_true, y_pred_proba)
                    metrics.update(calibration_metrics)
                    
                    # ROC curve data
                    fpr, tpr, roc_thresholds = roc_curve(y_true, y_pred_proba)
                    metrics['roc_curve'] = {
                        'fpr': fpr.tolist(),
                        'tpr': tpr.tolist(),
                        'thresholds': roc_thresholds.tolist()
                    }
                    
                    # PR curve data
                    precision_vals, recall_vals, pr_thresholds = precision_recall_curve(y_true, y_pred_proba)
                    metrics['pr_curve'] = {
                        'precision': precision_vals.tolist(),
                        'recall': recall_vals.tolist(),
                        'thresholds': pr_thresholds.tolist()
                    }
                    
                except Exception as e:
                    self.logger.warning("Failed to compute probabilistic metrics", error=str(e))
                    # Set defaults
                    metrics['auc_roc'] = 0.0
                    metrics['auc_pr'] = 0.0
                    metrics['log_loss'] = 0.0
                    metrics['brier_score'] = 0.0
            else:
                # No probabilities - set defaults
                metrics['auc_roc'] = 0.0
                metrics['auc_pr'] = 0.0
                metrics['log_loss'] = 0.0
                metrics['brier_score'] = 0.0
            
            self._log_operation("compute_all_metrics_success", 
                              auc_roc=metrics.get('auc_roc'),
                              f1=metrics.get('f1_score'))
            
            return metrics
            
        except Exception as e:
            return self._handle_error("compute_all_metrics", e, default_return={})
    
    def _compute_calibration_metrics(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray,
        n_bins: int = 10
    ) -> Dict[str, float]:
        """
        Compute calibration metrics (ECE and MCE).
        
        Args:
            y_true: True labels
            y_pred_proba: Predicted probabilities
            n_bins: Number of bins for calibration
            
        Returns:
            Dictionary with ECE and MCE
        """
        try:
            # Bin predictions
            bins = np.linspace(0, 1, n_bins + 1)
            bin_indices = np.digitize(y_pred_proba, bins) - 1
            bin_indices = np.clip(bin_indices, 0, n_bins - 1)
            
            bin_sums = np.bincount(bin_indices, weights=y_pred_proba, minlength=n_bins)
            bin_true = np.bincount(bin_indices, weights=y_true, minlength=n_bins)
            bin_total = np.bincount(bin_indices, minlength=n_bins)
            
            # Avoid division by zero
            nonzero = bin_total != 0
            
            # Expected Calibration Error (ECE)
            bin_acc = np.zeros(n_bins)
            bin_conf = np.zeros(n_bins)
            bin_acc[nonzero] = bin_true[nonzero] / bin_total[nonzero]
            bin_conf[nonzero] = bin_sums[nonzero] / bin_total[nonzero]
            
            ece = np.sum(bin_total[nonzero] * np.abs(bin_acc[nonzero] - bin_conf[nonzero])) / np.sum(bin_total)
            
            # Maximum Calibration Error (MCE)
            mce = np.max(np.abs(bin_acc[nonzero] - bin_conf[nonzero])) if np.any(nonzero) else 0.0
            
            return {
                'expected_calibration_error': float(ece),
                'maximum_calibration_error': float(mce)
            }
            
        except Exception as e:
            self.logger.warning("Failed to compute calibration metrics", error=str(e))
            return {
                'expected_calibration_error': 0.0,
                'maximum_calibration_error': 0.0
            }
    
    def save_metrics(
        self,
        model_id: str,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        Save metrics for a model.
        
        Args:
            model_id: Model identifier
            metrics: Computed metrics
            
        Returns:
            True if successful
        """
        self._log_operation("save_metrics", model_id=model_id)
        
        try:
            success = self.dal.save_model_metrics(
                model_id,
                metrics,
                source_module=self.service_name
            )
            
            if success:
                self._log_operation("save_metrics_success", model_id=model_id)
            
            return success
            
        except Exception as e:
            return self._handle_error("save_metrics", e, model_id=model_id, default_return=False)
    
    def get_metrics(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Metrics dictionary or None
        """
        self._log_operation("get_metrics", model_id=model_id)
        
        try:
            metrics = self.dal.get_model_metrics(model_id)
            
            if metrics:
                self._log_operation("get_metrics_success", model_id=model_id)
            else:
                self.logger.warning("No metrics found", model_id=model_id)
            
            return metrics
            
        except Exception as e:
            return self._handle_error("get_metrics", e, model_id=model_id, default_return=None)
    
    def compare_metrics(
        self,
        model_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Compare metrics across multiple models.
        
        Args:
            model_ids: List of model identifiers
            
        Returns:
            Comparison data
        """
        self._log_operation("compare_metrics", model_count=len(model_ids))
        
        try:
            comparison = {
                'models': [],
                'best_auc_roc': None,
                'best_f1': None,
                'best_accuracy': None
            }
            
            best_auc = -1
            best_f1 = -1
            best_acc = -1
            
            for model_id in model_ids:
                metrics = self.get_metrics(model_id)
                if metrics:
                    model_data = {
                        'model_id': model_id,
                        'metrics': metrics
                    }
                    comparison['models'].append(model_data)
                    
                    # Track best models
                    if metrics.get('auc_roc', 0) > best_auc:
                        best_auc = metrics['auc_roc']
                        comparison['best_auc_roc'] = model_id
                    
                    if metrics.get('f1_score', 0) > best_f1:
                        best_f1 = metrics['f1_score']
                        comparison['best_f1'] = model_id
                    
                    if metrics.get('accuracy', 0) > best_acc:
                        best_acc = metrics['accuracy']
                        comparison['best_accuracy'] = model_id
            
            return comparison
            
        except Exception as e:
            return self._handle_error("compare_metrics", e, default_return={'models': []})
    
    def validate_metrics(self, metrics: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that metrics contain all required fields.
        
        Args:
            metrics: Metrics dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        required_fields = [
            'accuracy', 'precision', 'recall', 'f1_score',
            'auc_roc', 'auc_pr', 'confusion_matrix'
        ]
        
        missing = [field for field in required_fields if field not in metrics]
        
        is_valid = len(missing) == 0
        
        if not is_valid:
            self.logger.warning("Metrics validation failed", missing_fields=missing)
        
        return is_valid, missing


# Global metrics service instance
metrics_service = MetricsService()
