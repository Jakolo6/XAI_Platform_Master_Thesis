"""
Model training utilities.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, Optional
import pickle
import hashlib
import structlog
from pathlib import Path

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
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
)
from sklearn.calibration import calibration_curve

# Lazy imports for libraries that may have dependencies
# These will be imported only when the specific model type is used
xgb = None
lgb = None
cb = None
optuna = None

from app.core.config import settings, MODEL_CONFIGS

logger = structlog.get_logger()


class ModelTrainer:
    """
    Model training and evaluation utility.
    """
    
    def __init__(self, model_type: str, hyperparameters: Optional[Dict[str, Any]] = None):
        """
        Initialize model trainer.
        
        Args:
            model_type: Type of model (e.g., 'xgboost', 'random_forest')
            hyperparameters: Model hyperparameters (uses defaults if None)
        """
        self.model_type = model_type
        self.model_config = MODEL_CONFIGS.get(model_type)
        
        if not self.model_config:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Merge default params with provided hyperparameters
        self.hyperparameters = self.model_config["default_params"].copy()
        if hyperparameters:
            self.hyperparameters.update(hyperparameters)
        
        self.model = None
        
    def _create_model(self):
        """Create model instance based on type."""
        global xgb, lgb, cb
        
        if self.model_type == "logistic_regression":
            return LogisticRegression(**self.hyperparameters)
        elif self.model_type == "random_forest":
            return RandomForestClassifier(**self.hyperparameters)
        elif self.model_type == "xgboost":
            if xgb is None:
                import xgboost as xgb_module
                xgb = xgb_module
            return xgb.XGBClassifier(**self.hyperparameters)
        elif self.model_type == "lightgbm":
            if lgb is None:
                import lightgbm as lgb_module
                lgb = lgb_module
            return lgb.LGBMClassifier(**self.hyperparameters)
        elif self.model_type == "catboost":
            if cb is None:
                import catboost as cb_module
                cb = cb_module
            return cb.CatBoostClassifier(**self.hyperparameters)
        elif self.model_type == "mlp":
            return MLPClassifier(**self.hyperparameters)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
    ) -> Dict[str, Any]:
        """
        Train the model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            
        Returns:
            Training results dictionary
        """
        logger.info("Starting model training", model_type=self.model_type)
        
        import time
        start_time = time.time()
        
        # Create model
        self.model = self._create_model()
        
        # Train with validation set if available (for early stopping)
        if X_val is not None and y_val is not None:
            if self.model_type in ["xgboost", "lightgbm", "catboost"]:
                # Use early stopping for gradient boosting models
                eval_set = [(X_val, y_val)]
                
                if self.model_type == "xgboost":
                    self.model.fit(
                        X_train, y_train,
                        eval_set=eval_set,
                        verbose=False
                    )
                elif self.model_type == "lightgbm":
                    if lgb is None:
                        import lightgbm as lgb_module
                        lgb = lgb_module
                    self.model.fit(
                        X_train, y_train,
                        eval_set=eval_set,
                        callbacks=[lgb.early_stopping(stopping_rounds=10, verbose=False)]
                    )
                elif self.model_type == "catboost":
                    self.model.fit(
                        X_train, y_train,
                        eval_set=eval_set,
                        early_stopping_rounds=10,
                        verbose=False
                    )
            else:
                # Standard training for other models
                self.model.fit(X_train, y_train)
        else:
            # Train without validation
            self.model.fit(X_train, y_train)
        
        training_time = time.time() - start_time
        
        logger.info("Model training complete",
                   model_type=self.model_type,
                   training_time=training_time)
        
        return {
            "status": "success",
            "training_time_seconds": training_time,
        }
    
    def evaluate(
        self,
        X_test: pd.DataFrame,
        y_test: pd.Series,
    ) -> Dict[str, Any]:
        """
        Evaluate the model.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Evaluation metrics dictionary
        """
        if self.model is None:
            raise ValueError("Model must be trained before evaluation")
        
        logger.info("Evaluating model", model_type=self.model_type)
        
        # Get predictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        metrics = {
            "auc_roc": float(roc_auc_score(y_test, y_pred_proba)),
            "auc_pr": float(average_precision_score(y_test, y_pred_proba)),
            "f1_score": float(f1_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred)),
            "recall": float(recall_score(y_test, y_pred)),
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "log_loss": float(log_loss(y_test, y_pred_proba)),
            "brier_score": float(brier_score_loss(y_test, y_pred_proba)),
        }
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        metrics["confusion_matrix"] = {
            "tn": int(cm[0, 0]),
            "fp": int(cm[0, 1]),
            "fn": int(cm[1, 0]),
            "tp": int(cm[1, 1]),
        }
        
        # Calibration metrics
        try:
            prob_true, prob_pred = calibration_curve(y_test, y_pred_proba, n_bins=10)
            ece = float(np.abs(prob_true - prob_pred).mean())
            mce = float(np.abs(prob_true - prob_pred).max())
            
            metrics["expected_calibration_error"] = ece
            metrics["maximum_calibration_error"] = mce
        except Exception as e:
            logger.warning("Calibration calculation failed", exc_info=e)
            metrics["expected_calibration_error"] = None
            metrics["maximum_calibration_error"] = None
        
        # ROC curve data
        try:
            from sklearn.metrics import roc_curve, precision_recall_curve
            fpr, tpr, roc_thresholds = roc_curve(y_test, y_pred_proba)
            precision_curve, recall_curve, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)
            
            # Sample points to reduce data size (keep 100 points)
            n_points = min(100, len(fpr))
            indices = np.linspace(0, len(fpr) - 1, n_points, dtype=int)
            
            metrics["roc_curve"] = {
                "fpr": [float(fpr[i]) for i in indices],
                "tpr": [float(tpr[i]) for i in indices],
                "thresholds": [float(roc_thresholds[i]) for i in indices]
            }
            
            # Sample PR curve points
            n_points_pr = min(100, len(precision_curve))
            indices_pr = np.linspace(0, len(precision_curve) - 1, n_points_pr, dtype=int)
            
            metrics["pr_curve"] = {
                "precision": [float(precision_curve[i]) for i in indices_pr],
                "recall": [float(recall_curve[i]) for i in indices_pr],
                "thresholds": [float(pr_thresholds[i]) for i in indices_pr if i < len(pr_thresholds)]
            }
        except Exception as e:
            logger.warning("ROC curve calculation failed", exc_info=e)
            metrics["roc_curve"] = None
            metrics["pr_curve"] = None
        
        logger.info("Model evaluation complete",
                   model_type=self.model_type,
                   auc_roc=metrics["auc_roc"],
                   f1_score=metrics["f1_score"])
        
        return metrics
    
    def get_feature_importance(self, feature_names: list, top_n: int = 20) -> Dict[str, float]:
        """
        Get feature importance scores.
        
        Args:
            feature_names: List of feature names
            top_n: Number of top features to return
            
        Returns:
            Dictionary mapping feature names to importance scores
        """
        if self.model is None:
            raise ValueError("Model must be trained before getting feature importance")
        
        try:
            # Get feature importance based on model type
            if hasattr(self.model, 'feature_importances_'):
                # Tree-based models (XGBoost, Random Forest, LightGBM, CatBoost)
                importances = self.model.feature_importances_
            elif hasattr(self.model, 'coef_'):
                # Linear models (Logistic Regression)
                importances = np.abs(self.model.coef_[0])
            else:
                logger.warning("Model does not support feature importance")
                return {}
            
            # Normalize to sum to 1
            importances = importances / importances.sum()
            
            # Create feature importance dictionary
            feature_importance = dict(zip(feature_names, importances))
            
            # Sort by importance and get top N
            sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
            top_features = dict(sorted_features[:top_n])
            
            return top_features
            
        except Exception as e:
            logger.error("Failed to get feature importance", exc_info=e)
            return {}
    
    def optimize_hyperparameters(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: pd.DataFrame,
        y_val: pd.Series,
        n_trials: Optional[int] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Optimize hyperparameters using Optuna.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            n_trials: Number of optimization trials
            timeout: Timeout in seconds
            
        Returns:
            Best hyperparameters
        """
        if n_trials is None:
            n_trials = settings.OPTUNA_N_TRIALS
        if timeout is None:
            timeout = settings.OPTUNA_TIMEOUT_SECONDS
        
        logger.info("Starting hyperparameter optimization",
                   model_type=self.model_type,
                   n_trials=n_trials)
        
        def objective(trial):
            # Sample hyperparameters
            params = self.model_config["default_params"].copy()
            
            for param_name, param_config in self.model_config["optuna_params"].items():
                if param_config["type"] == "int":
                    params[param_name] = trial.suggest_int(
                        param_name,
                        param_config["low"],
                        param_config["high"],
                        step=param_config.get("step", 1)
                    )
                elif param_config["type"] == "uniform":
                    params[param_name] = trial.suggest_float(
                        param_name,
                        param_config["low"],
                        param_config["high"]
                    )
                elif param_config["type"] == "loguniform":
                    params[param_name] = trial.suggest_float(
                        param_name,
                        param_config["low"],
                        param_config["high"],
                        log=True
                    )
                elif param_config["type"] == "categorical":
                    params[param_name] = trial.suggest_categorical(
                        param_name,
                        param_config["choices"]
                    )
            
            # Train model with these parameters
            temp_trainer = ModelTrainer(self.model_type, params)
            temp_trainer.train(X_train, y_train, X_val, y_val)
            
            # Evaluate on validation set
            y_pred_proba = temp_trainer.model.predict_proba(X_val)[:, 1]
            auc_score = roc_auc_score(y_val, y_pred_proba)
            
            return auc_score
        
        # Run optimization
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials, timeout=timeout, show_progress_bar=False)
        
        best_params = study.best_params
        best_score = study.best_value
        
        logger.info("Hyperparameter optimization complete",
                   model_type=self.model_type,
                   best_score=best_score,
                   best_params=best_params)
        
        # Update hyperparameters with best params
        self.hyperparameters.update(best_params)
        
        return {
            "best_params": best_params,
            "best_score": float(best_score),
            "n_trials": len(study.trials),
        }
    
    def save_model(self, file_path: str) -> str:
        """
        Save model to file and return SHA256 hash.
        
        Args:
            file_path: Path to save model
            
        Returns:
            SHA256 hash of the model file
        """
        if self.model is None:
            raise ValueError("Model must be trained before saving")
        
        # Create directory if it doesn't exist
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save model
        with open(file_path, 'wb') as f:
            pickle.dump(self.model, f)
        
        # Calculate hash
        model_hash = self.calculate_model_hash(file_path)
        
        logger.info("Model saved",
                   model_type=self.model_type,
                   file_path=file_path,
                   model_hash=model_hash)
        
        return model_hash
    
    @staticmethod
    def calculate_model_hash(file_path: str) -> str:
        """
        Calculate SHA256 hash of model file.
        
        Args:
            file_path: Path to model file
            
        Returns:
            SHA256 hash string
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    @staticmethod
    def load_model(file_path: str):
        """
        Load model from file.
        
        Args:
            file_path: Path to model file
            
        Returns:
            Loaded model
        """
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
        
        logger.info("Model loaded", file_path=file_path)
        
        return model
