"""
Kaggle dataset integration service.
Downloads and processes Home Credit Default Risk dataset.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import structlog
from typing import Dict, Any, Tuple
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

from app.services.r2_service import r2_service

logger = structlog.get_logger()


class KaggleService:
    """Service for Kaggle dataset operations"""
    
    DATASET_NAME = "c/home-credit-default-risk"
    DATA_DIR = Path("data/raw/home_credit")
    PROCESSED_DIR = Path("data/processed")
    
    def __init__(self):
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    def download_dataset(self) -> Dict[str, Any]:
        """Download Home Credit dataset from Kaggle"""
        try:
            logger.info("Downloading Home Credit dataset from Kaggle")
            
            # Check if kaggle is configured
            if not os.path.exists(os.path.expanduser('~/.kaggle/kaggle.json')):
                raise Exception("Kaggle API not configured. Please set up ~/.kaggle/kaggle.json")
            
            import kaggle
            
            # Download using Kaggle API
            kaggle.api.competition_download_files(
                'home-credit-default-risk',
                path=str(self.DATA_DIR),
                quiet=False
            )
            
            # Unzip files
            import zipfile
            zip_path = self.DATA_DIR / "home-credit-default-risk.zip"
            
            if zip_path.exists():
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.DATA_DIR)
                zip_path.unlink()  # Delete zip after extraction
            
            logger.info("Dataset downloaded successfully")
            
            # Upload to R2 for persistent storage
            if r2_service.is_configured():
                logger.info("Uploading dataset files to R2 for persistent storage")
                r2_service.upload_directory(self.DATA_DIR, "home-credit/raw")
                logger.info("Dataset uploaded to R2")
            else:
                logger.warning("R2 not configured, files will be ephemeral")
            
            return {
                "status": "success",
                "message": "Home Credit dataset downloaded",
                "files": [f.name for f in self.DATA_DIR.glob("*.csv")]
            }
            
        except Exception as e:
            logger.error("Failed to download dataset", error=str(e))
            raise
    
    def load_and_preprocess(self) -> Dict[str, Any]:
        """Load and preprocess the main application_train.csv file"""
        try:
            logger.info("Loading application_train.csv")
            
            # Load main training data
            train_path = self.DATA_DIR / "application_train.csv"
            
            # Try to load from R2 if not available locally
            if not train_path.exists():
                logger.info("File not found locally, checking R2...")
                
                if r2_service.is_configured() and r2_service.file_exists("home-credit/raw/application_train.csv"):
                    logger.info("Downloading dataset from R2")
                    r2_service.download_directory("home-credit/raw", self.DATA_DIR)
                    logger.info("Dataset downloaded from R2")
                else:
                    raise FileNotFoundError(f"application_train.csv not found. Please download dataset first.")
            
            df = pd.read_csv(train_path)
            
            logger.info("Dataset loaded", 
                       n_samples=len(df), 
                       n_features=len(df.columns))
            
            # Preprocessing steps
            logger.info("Starting preprocessing")
            
            # 1. Handle target variable
            target = df['TARGET']
            df = df.drop('TARGET', axis=1)
            
            # 2. Remove SK_ID_CURR (identifier, not feature)
            if 'SK_ID_CURR' in df.columns:
                df = df.drop('SK_ID_CURR', axis=1)
            
            # 3. Handle missing values
            # For numerical: fill with median
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            for col in numerical_cols:
                df[col].fillna(df[col].median(), inplace=True)
            
            # For categorical: fill with mode
            categorical_cols = df.select_dtypes(include=['object']).columns
            for col in categorical_cols:
                if len(df[col].mode()) > 0:
                    df[col].fillna(df[col].mode()[0], inplace=True)
                else:
                    df[col].fillna('UNKNOWN', inplace=True)
            
            # 4. Encode categorical variables
            label_encoders = {}
            for col in categorical_cols:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                label_encoders[col] = le
            
            # 5. Feature scaling
            scaler = StandardScaler()
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            
            # 6. Train/validation/test split
            X_train, X_temp, y_train, y_temp = train_test_split(
                df, target, test_size=0.3, random_state=42, stratify=target
            )
            
            X_val, X_test, y_val, y_test = train_test_split(
                X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp
            )
            
            # 7. Save processed data
            train_df = X_train.copy()
            train_df['TARGET'] = y_train
            train_df.to_csv(self.PROCESSED_DIR / "home_credit_train.csv", index=False)
            
            val_df = X_val.copy()
            val_df['TARGET'] = y_val
            val_df.to_csv(self.PROCESSED_DIR / "home_credit_val.csv", index=False)
            
            test_df = X_test.copy()
            test_df['TARGET'] = y_test
            test_df.to_csv(self.PROCESSED_DIR / "home_credit_test.csv", index=False)
            
            logger.info("Preprocessing complete",
                       train_size=len(X_train),
                       val_size=len(X_val),
                       test_size=len(X_test))
            
            # Upload processed files to R2 for persistent storage
            if r2_service.is_configured():
                logger.info("Uploading processed files to R2")
                r2_service.upload_directory(self.PROCESSED_DIR, "home-credit/processed")
                logger.info("Processed files uploaded to R2")
            
            # Generate EDA statistics
            eda_stats = self._generate_eda_stats(df, target)
            
            return {
                "status": "success",
                "dataset_id": "home-credit-default-risk",
                "n_samples": len(df),
                "n_features": len(df.columns),
                "train_size": len(X_train),
                "val_size": len(X_val),
                "test_size": len(X_test),
                "target_distribution": {
                    "class_0": int((target == 0).sum()),
                    "class_1": int((target == 1).sum())
                },
                "eda_stats": eda_stats
            }
            
        except Exception as e:
            logger.error("Failed to preprocess dataset", error=str(e))
            raise
    
    def _generate_eda_stats(self, df: pd.DataFrame, target: pd.Series) -> Dict[str, Any]:
        """Generate EDA statistics for visualization"""
        
        numerical_cols = df.select_dtypes(include=[np.number]).columns[:10]  # Top 10
        
        stats = {
            "missing_values": {},
            "correlations": {},
            "distributions": {},
            "feature_stats": {}
        }
        
        # Get distributions for key features
        for col in numerical_cols:
            stats["distributions"][col] = {
                "mean": float(df[col].mean()),
                "std": float(df[col].std()),
                "min": float(df[col].min()),
                "max": float(df[col].max()),
                "quartiles": {
                    "0.25": float(df[col].quantile(0.25)),
                    "0.5": float(df[col].quantile(0.5)),
                    "0.75": float(df[col].quantile(0.75))
                }
            }
        
        return stats


# Singleton instance
kaggle_service = KaggleService()
