# CHUNK 2: MODEL TRAINING - BACKEND

## File 1: Training Service
**Path:** `backend/app/services/training_service.py`

```python
"""Model training service with XGBoost, RF, LogReg + Optuna"""
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
import structlog
from typing import Dict, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score
import xgboost as xgb
import optuna

logger = structlog.get_logger()

class TrainingService:
    MODELS_DIR = Path("models")
    DATA_DIR = Path("data/processed")
    
    def __init__(self):
        self.MODELS_DIR.mkdir(exist_ok=True)
    
    def train_model(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Train model with given config"""
        algorithm = config['algorithm']
        params = config.get('params', {})
        optimize = config.get('optimize', False)
        
        # Load data
        train_df = pd.read_csv(self.DATA_DIR / "home_credit_train.csv")
        val_df = pd.read_csv(self.DATA_DIR / "home_credit_val.csv")
        
        X_train = train_df.drop('TARGET', axis=1)
        y_train = train_df['TARGET']
        X_val = val_df.drop('TARGET', axis=1)
        y_val = val_df['TARGET']
        
        if optimize:
            params = self._optimize_hyperparameters(algorithm, X_train, y_train, X_val, y_val)
        
        # Train model
        if algorithm == 'xgboost':
            model = xgb.XGBClassifier(**params)
        elif algorithm == 'random_forest':
            model = RandomForestClassifier(**params)
        else:
            model = LogisticRegression(**params)
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict_proba(X_val)[:, 1]
        metrics = {
            'auc': float(roc_auc_score(y_val, y_pred)),
            'accuracy': float(accuracy_score(y_val, model.predict(X_val))),
            'f1': float(f1_score(y_val, model.predict(X_val)))
        }
        
        # Save model
        model_id = f"{algorithm}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
        joblib.dump(model, self.MODELS_DIR / f"{model_id}.pkl")
        
        return {
            'model_id': model_id,
            'algorithm': algorithm,
            'params': params,
            'metrics': metrics
        }
    
    def _optimize_hyperparameters(self, algorithm, X_train, y_train, X_val, y_val):
        """Optuna hyperparameter optimization"""
        def objective(trial):
            if algorithm == 'xgboost':
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 3, 10),
                    'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3),
                    'subsample': trial.suggest_float('subsample', 0.6, 1.0),
                    'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0)
                }
                model = xgb.XGBClassifier(**params)
            elif algorithm == 'random_forest':
                params = {
                    'n_estimators': trial.suggest_int('n_estimators', 50, 300),
                    'max_depth': trial.suggest_int('max_depth', 5, 30),
                    'min_samples_split': trial.suggest_int('min_samples_split', 2, 20)
                }
                model = RandomForestClassifier(**params)
            else:
                params = {'C': trial.suggest_float('C', 0.001, 10.0)}
                model = LogisticRegression(**params)
            
            model.fit(X_train, y_train)
            y_pred = model.predict_proba(X_val)[:, 1]
            return roc_auc_score(y_val, y_pred)
        
        study = optuna.create_study(direction='maximize')
        study.optimize(objective, n_trials=20)
        return study.best_params

training_service = TrainingService()
```

## File 2: Training API
**Path:** `backend/app/api/v1/endpoints/training.py`

```python
"""Training API endpoints"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import structlog
from app.services.training_service import training_service
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()

class TrainRequest(BaseModel):
    algorithm: str
    params: Optional[Dict[str, Any]] = {}
    optimize: bool = False

@router.post("/train")
async def train_model(request: TrainRequest, background_tasks: BackgroundTasks):
    """Train model with given config"""
    try:
        result = training_service.train_model(request.dict())
        
        # Save to Supabase
        supabase_db.table('models').insert({
            'model_id': result['model_id'],
            'name': f"{request.algorithm} Model",
            'model_type': request.algorithm,
            'dataset_id': 'home-credit-default-risk',
            'hyperparameters': result['params'],
            'metrics': result['metrics'],
            'status': 'completed'
        }).execute()
        
        return result
    except Exception as e:
        logger.error("Training failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_models():
    """Get all trained models"""
    result = supabase_db.table('models').select('*').eq('dataset_id', 'home-credit-default-risk').execute()
    return {'models': result.data}
```

## Register Routes
Add to `backend/app/api/v1/api.py`:
```python
from app.api.v1.endpoints import training
api_router.include_router(training.router, prefix="/training", tags=["training"])
```
