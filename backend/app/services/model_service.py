"""
Model training service - synchronous training without Celery.
"""

import os
import time
import uuid
import pickle
from pathlib import Path
from typing import Dict, Any
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    roc_curve, confusion_matrix, precision_recall_curve
)
import structlog

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from app.core.config import settings
from app.services.r2_service import r2_service
from app.utils.supabase_client import supabase_db
from app.core.data_access import dal

logger = structlog.get_logger()


class ModelTrainingService:
    """Service for training models without Celery."""
    
    def train_model(
        self,
        dataset_id: str,
        model_type: str,
        hyperparameters: Dict[str, Any] = None,
        model_name: str = None
    ) -> Dict[str, Any]:
        """
        Train a model on a processed dataset.
        
        Args:
            dataset_id: Dataset identifier
            model_type: Type of model (xgboost, random_forest, etc.)
            hyperparameters: Optional hyperparameters
            model_name: Optional custom name for the model
            
        Returns:
            Dictionary with training results
        """
        start_time = time.time()
        model_id = f"{dataset_id}_{model_type}_{uuid.uuid4().hex[:8]}"
        
        # Generate display name
        if model_name:
            display_name = model_name
        else:
            display_name = f"{model_type.upper()} on {dataset_id}"
        
        logger.info("Starting model training",
                   model_id=model_id,
                   model_name=display_name,
                   dataset_id=dataset_id,
                   model_type=model_type)
        
        try:
            # 1. Check if dataset is processed
            logger.info("Fetching dataset info", dataset_id=dataset_id)
            dataset = dal.get_dataset(dataset_id)
            
            if not dataset:
                logger.error("Dataset not found", dataset_id=dataset_id)
                raise ValueError(f"Dataset {dataset_id} not found")
            
            logger.info("Dataset found", dataset_id=dataset_id, status=dataset.get('status'))
            
            if dataset['status'] != 'completed':
                logger.error("Dataset not processed", dataset_id=dataset_id, status=dataset['status'])
                raise ValueError(f"Dataset {dataset_id} is not processed (status: {dataset['status']})")
            
            file_path = dataset.get('file_path')
            if not file_path:
                raise ValueError(f"Dataset {dataset_id} has no file path")
            
            # 2. Create temp directory
            temp_dir = Path(f"/tmp/{model_id}")
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            try:
                # 3. Download processed data from R2
                logger.info("Downloading processed data from R2", dataset_id=dataset_id)
                train_path = temp_dir / "train.parquet"
                val_path = temp_dir / "val.parquet"
                test_path = temp_dir / "test.parquet"
                
                r2_service.download_file(f"{file_path}/train.parquet", train_path)
                r2_service.download_file(f"{file_path}/val.parquet", val_path)
                r2_service.download_file(f"{file_path}/test.parquet", test_path)
                
                # 4. Load data
                logger.info("Loading training data", dataset_id=dataset_id)
                train_df = pd.read_parquet(train_path)
                val_df = pd.read_parquet(val_path)
                test_df = pd.read_parquet(test_path)
                
                # 5. Prepare features and target
                # Assume last column is target (or get from config)
                target_col = train_df.columns[-1]  # TODO: Get from dataset config
                
                X_train = train_df.drop(columns=[target_col])
                y_train = train_df[target_col]
                X_val = val_df.drop(columns=[target_col])
                y_val = val_df[target_col]
                X_test = test_df.drop(columns=[target_col])
                y_test = test_df[target_col]
                
                logger.info("Data loaded",
                           train_samples=len(X_train),
                           val_samples=len(X_val),
                           test_samples=len(X_test),
                           features=len(X_train.columns))
                
                # 6. Train model
                logger.info("Training model", model_type=model_type)
                model, training_time = self._train_model(
                    model_type,
                    X_train, y_train,
                    X_val, y_val,
                    hyperparameters
                )
                
                # 7. Evaluate on test set
                logger.info("Evaluating model on test set")
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
                
                # Calculate basic metrics
                metrics = {
                    'accuracy': float(accuracy_score(y_test, y_pred)),
                    'precision': float(precision_score(y_test, y_pred, average='binary', zero_division=0)),
                    'recall': float(recall_score(y_test, y_pred, average='binary', zero_division=0)),
                    'f1_score': float(f1_score(y_test, y_pred, average='binary', zero_division=0)),
                    'auc_roc': float(roc_auc_score(y_test, y_pred_proba)) if len(np.unique(y_test)) > 1 else 0.0
                }
                
                # Calculate ROC curve
                if hasattr(model, 'predict_proba') and len(np.unique(y_test)) > 1:
                    fpr, tpr, thresholds = roc_curve(y_test, y_pred_proba)
                    metrics['roc_curve'] = {
                        'fpr': fpr.tolist(),
                        'tpr': tpr.tolist(),
                        'thresholds': thresholds.tolist()
                    }
                else:
                    metrics['roc_curve'] = None
                
                # Calculate confusion matrix
                cm = confusion_matrix(y_test, y_pred)
                metrics['confusion_matrix'] = cm.tolist()
                
                # Calculate PR curve
                if hasattr(model, 'predict_proba') and len(np.unique(y_test)) > 1:
                    precision_vals, recall_vals, pr_thresholds = precision_recall_curve(y_test, y_pred_proba)
                    metrics['pr_curve'] = {
                        'precision': precision_vals.tolist(),
                        'recall': recall_vals.tolist(),
                        'thresholds': pr_thresholds.tolist()
                    }
                else:
                    metrics['pr_curve'] = None
                
                logger.info("Model evaluation complete", 
                           accuracy=metrics['accuracy'],
                           auc_roc=metrics['auc_roc'])
                
                # 8. Get feature importance
                feature_importance = self._get_feature_importance(model, X_train.columns)
                
                # 9. Save model to temp file
                model_path = temp_dir / f"{model_id}.pkl"
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                # 10. Upload model to R2
                logger.info("Uploading model to R2", model_id=model_id)
                r2_model_path = f"models/{dataset_id}/{model_id}.pkl"
                r2_service.upload_file(
                    model_path,
                    r2_model_path
                )
                
                total_time = time.time() - start_time
                
                # 11. Save model metadata to Supabase
                model_data = {
                    'id': model_id,
                    'name': display_name,  # Use custom name or auto-generated
                    'model_type': model_type,
                    'version': '1.0',
                    'dataset_id': dataset_id,
                    'status': 'completed',
                    'model_path': r2_model_path,
                    'training_time_seconds': training_time,
                    'hyperparameters': hyperparameters or {},
                    'feature_importance': feature_importance,
                    'completed_at': pd.Timestamp.now().isoformat()
                }
                
                # Save model via DAL
                logger.info("Saving model to database", model_id=model_id)
                created_model_id = dal.create_model(model_data, source_module="model_service")
                
                if not created_model_id:
                    raise RuntimeError(f"Failed to save model {model_id} to database")
                
                logger.info("Model saved successfully", model_id=model_id)
                
                # 12. Save metrics via DAL
                logger.info("Saving model metrics", model_id=model_id)
                dal.save_model_metrics(model_id, metrics, source_module="model_service")
                logger.info("Metrics saved successfully", model_id=model_id)
                
                # 13. Generate SHAP explanation automatically
                logger.info("Generating SHAP explanation", model_id=model_id)
                try:
                    shap_explanation = self._generate_shap_explanation(
                        model, X_test, y_test, model_type
                    )
                    
                    # Save explanation via DAL
                    explanation_id = f"{model_id}_shap"
                    explanation_data = {
                        'status': 'completed',
                        'explanation_data': shap_explanation,
                        'completed_at': pd.Timestamp.now().isoformat()
                    }
                    dal.save_explanation(model_id, 'shap', explanation_data, source_module="model_service")
                    logger.info("SHAP explanation generated", explanation_id=explanation_id)
                except Exception as e:
                    logger.warning("Failed to generate SHAP explanation", error=str(e))
                
                logger.info("Model training complete",
                           model_id=model_id,
                           total_time=total_time,
                           accuracy=metrics['accuracy'])
                
                return {
                    'status': 'success',
                    'model_id': model_id,
                    'metrics': metrics,
                    'training_time_seconds': training_time,
                    'model_path': r2_model_path
                }
                
            finally:
                # Cleanup temp directory
                import shutil
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    logger.debug("Temp directory cleaned up", path=str(temp_dir))
        
        except Exception as e:
            import sys
            import traceback
            
            error_details = traceback.format_exc()
            logger.error("Model training failed",
                        model_id=model_id,
                        dataset_id=dataset_id,
                        error=str(e),
                        traceback=error_details,
                        exc_info=True)
            sys.stdout.flush()
            sys.stderr.flush()
            
            return {
                'status': 'error',
                'model_id': model_id,
                'dataset_id': dataset_id,
                'error': str(e),
                'traceback': error_details
            }
    
    def _train_model(
        self,
        model_type: str,
        X_train, y_train,
        X_val, y_val,
        hyperparameters: Dict = None
    ):
        """Train the specified model type."""
        start_time = time.time()
        
        if model_type == 'xgboost':
            if not XGBOOST_AVAILABLE:
                raise ValueError("XGBoost is not installed")
            
            params = hyperparameters or {
                'max_depth': 6,
                'learning_rate': 0.1,
                'n_estimators': 100,
                'objective': 'binary:logistic',
                'random_state': 42
            }
            
            model = xgb.XGBClassifier(**params)
            model.fit(
                X_train, y_train,
                eval_set=[(X_val, y_val)],
                verbose=False
            )
        
        elif model_type == 'random_forest':
            params = hyperparameters or {
                'n_estimators': 100,
                'max_depth': 10,
                'random_state': 42,
                'n_jobs': -1
            }
            
            model = RandomForestClassifier(**params)
            model.fit(X_train, y_train)
        
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
        
        training_time = time.time() - start_time
        return model, training_time
    
    def _generate_shap_explanation(
        self,
        model,
        X_test: pd.DataFrame,
        y_test: pd.Series,
        model_type: str
    ) -> Dict[str, Any]:
        """
        Generate SHAP explanation for the trained model.
        
        Args:
            model: Trained model
            X_test: Test features
            y_test: Test labels
            model_type: Type of model
            
        Returns:
            Dictionary with SHAP values and feature importance
        """
        import shap
        import numpy as np
        
        # Sample data for faster computation
        sample_size = min(100, len(X_test))
        X_sample = X_test.sample(n=sample_size, random_state=42)
        
        # Create explainer based on model type
        if model_type in ['xgboost', 'random_forest']:
            explainer = shap.TreeExplainer(model)
        else:
            # Use KernelExplainer for other models
            background = shap.sample(X_test, min(50, len(X_test)))
            explainer = shap.KernelExplainer(model.predict_proba, background)
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X_sample)
        
        # For binary classification, take positive class
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        # Calculate feature importance (mean absolute SHAP values)
        feature_importance = {}
        for i, col in enumerate(X_sample.columns):
            feature_importance[col] = float(np.abs(shap_values[:, i]).mean())
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        # Get top 20 features
        top_features = dict(list(feature_importance.items())[:20])
        
        return {
            'feature_importance': top_features,
            'method': 'shap',
            'sample_size': sample_size,
            'feature_names': list(X_sample.columns)
        }
    
    def _get_feature_importance(self, model, feature_names) -> Dict[str, float]:
        """Extract feature importance from model."""
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                # Get top 20 features
                top_indices = np.argsort(importances)[-20:][::-1]
                return {
                    str(feature_names[i]): float(importances[i])
                    for i in top_indices
                }
        except Exception as e:
            logger.warning("Could not extract feature importance", error=str(e))
        
        return {}


# Global service instance
model_service = ModelTrainingService()
