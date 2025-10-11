"""
Application configuration using Pydantic settings.
"""

from typing import List, Dict, Any, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "XAI Finance Benchmark Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000,https://xai-working-project.netlify.app"
    ALLOWED_ORIGINS: str = ""  # Alternative env var for Railway
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://xai_user:xai_password@localhost:5432/xai_finance_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""  # Renamed from SUPABASE_SERVICE_ROLE_KEY to match .env
    
    # Cloudflare R2 Storage (S3-compatible)
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "xai-platform-datasets"
    R2_ENDPOINT_URL: str = "https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com"
    R2_PUBLIC_URL: str = ""  # Optional: for public access
    
    # Storage Buckets (legacy - now using R2 paths)
    STORAGE_BUCKET_DATASETS: str = "datasets"
    STORAGE_BUCKET_MODELS: str = "models"
    STORAGE_BUCKET_EXPLANATIONS: str = "explanations"
    STORAGE_BUCKET_REPORTS: str = "reports"
    
    # Kaggle
    KAGGLE_USERNAME: str = ""
    KAGGLE_KEY: str = ""
    
    # Model Training
    MAX_TRAINING_TIME_SECONDS: int = 3600
    OPTUNA_N_TRIALS: int = 10
    OPTUNA_TIMEOUT_SECONDS: int = 1800
    
    # Dataset
    MAX_DATASET_SIZE_MB: int = 500
    DEFAULT_SAMPLE_SIZE: int = 500000
    
    # XAI
    SHAP_MAX_SAMPLES: int = 1000
    LIME_NUM_SAMPLES: int = 5000
    EXPLANATION_CACHE_TTL_SECONDS: int = 3600
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    SENTRY_DSN: str = ""
    ENABLE_METRICS: bool = True
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def convert_cors_origins_to_string(cls, v):
        """Convert CORS origins to string format if it's a list (from Railway env vars)."""
        if isinstance(v, list):
            # Convert list to comma-separated string
            return ",".join(v)
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Model configurations for 6 ML algorithms
MODEL_CONFIGS: Dict[str, Dict[str, Any]] = {
    "logistic_regression": {
        "name": "Logistic Regression",
        "class": "sklearn.linear_model.LogisticRegression",
        "default_params": {
            "max_iter": 1000,
            "random_state": 42,
            "n_jobs": -1,
        },
        "optuna_params": {
            "C": {"type": "loguniform", "low": 0.001, "high": 10.0},
            "penalty": {"type": "categorical", "choices": ["l2"]},
            "solver": {"type": "categorical", "choices": ["lbfgs", "saga"]},
        },
    },
    "random_forest": {
        "name": "Random Forest",
        "class": "sklearn.ensemble.RandomForestClassifier",
        "default_params": {
            "random_state": 42,
            "n_jobs": -1,
        },
        "optuna_params": {
            "n_estimators": {"type": "int", "low": 100, "high": 500, "step": 100},
            "max_depth": {"type": "int", "low": 5, "high": 30},
            "min_samples_split": {"type": "int", "low": 2, "high": 20},
            "min_samples_leaf": {"type": "int", "low": 1, "high": 10},
        },
    },
    "xgboost": {
        "name": "XGBoost",
        "class": "xgboost.XGBClassifier",
        "default_params": {
            "random_state": 42,
            "n_jobs": -1,
            "eval_metric": "logloss",
        },
        "optuna_params": {
            "n_estimators": {"type": "int", "low": 100, "high": 500, "step": 100},
            "max_depth": {"type": "int", "low": 3, "high": 10},
            "learning_rate": {"type": "loguniform", "low": 0.01, "high": 0.3},
            "subsample": {"type": "uniform", "low": 0.6, "high": 1.0},
            "colsample_bytree": {"type": "uniform", "low": 0.6, "high": 1.0},
        },
    },
    "lightgbm": {
        "name": "LightGBM",
        "class": "lightgbm.LGBMClassifier",
        "default_params": {
            "random_state": 42,
            "n_jobs": -1,
            "verbose": -1,
        },
        "optuna_params": {
            "n_estimators": {"type": "int", "low": 100, "high": 500, "step": 100},
            "max_depth": {"type": "int", "low": 3, "high": 10},
            "learning_rate": {"type": "loguniform", "low": 0.01, "high": 0.3},
            "num_leaves": {"type": "int", "low": 20, "high": 150},
            "subsample": {"type": "uniform", "low": 0.6, "high": 1.0},
        },
    },
    "catboost": {
        "name": "CatBoost",
        "class": "catboost.CatBoostClassifier",
        "default_params": {
            "random_state": 42,
            "verbose": False,
        },
        "optuna_params": {
            "iterations": {"type": "int", "low": 100, "high": 500, "step": 100},
            "depth": {"type": "int", "low": 3, "high": 10},
            "learning_rate": {"type": "loguniform", "low": 0.01, "high": 0.3},
            "l2_leaf_reg": {"type": "loguniform", "low": 1, "high": 10},
        },
    },
    "mlp": {
        "name": "Multi-Layer Perceptron",
        "class": "sklearn.neural_network.MLPClassifier",
        "default_params": {
            "random_state": 42,
            "max_iter": 500,
        },
        "optuna_params": {
            "hidden_layer_sizes": {
                "type": "categorical",
                "choices": [(100,), (100, 50), (200, 100), (200, 100, 50)],
            },
            "activation": {"type": "categorical", "choices": ["relu", "tanh"]},
            "alpha": {"type": "loguniform", "low": 0.0001, "high": 0.1},
            "learning_rate": {"type": "categorical", "choices": ["constant", "adaptive"]},
        },
    },
}

# XAI method configurations
XAI_CONFIGS: Dict[str, Dict[str, Any]] = {
    "shap_tree": {
        "name": "SHAP TreeExplainer",
        "applicable_models": ["random_forest", "xgboost", "lightgbm", "catboost"],
        "config": {
            "max_samples": 1000,
            "check_additivity": False,
        },
    },
    "shap_kernel": {
        "name": "SHAP KernelExplainer",
        "applicable_models": ["logistic_regression", "mlp"],
        "config": {
            "max_samples": 100,
            "n_samples": 1000,
        },
    },
    "lime": {
        "name": "LIME",
        "applicable_models": ["logistic_regression", "random_forest", "xgboost", "lightgbm", "catboost", "mlp"],
        "config": {
            "num_samples": 5000,
            "num_features": 10,
        },
    },
}

# Evaluation metrics configuration
METRICS_CONFIG = {
    "classification": [
        "auc_roc",
        "auc_pr",
        "f1_score",
        "precision",
        "recall",
        "accuracy",
        "log_loss",
        "brier_score",
    ],
    "calibration": [
        "expected_calibration_error",
        "maximum_calibration_error",
    ],
}

# Create settings instance
settings = Settings()
