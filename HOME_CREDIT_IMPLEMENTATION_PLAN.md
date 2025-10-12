# 🏦 HOME CREDIT XAI PLATFORM - COMPLETE IMPLEMENTATION PLAN

## 📋 OVERVIEW

Building a production-grade XAI platform for **Home Credit Default Risk** dataset with:
- ✅ NO mock data
- ✅ Full frontend-backend integration
- ✅ Real Kaggle dataset
- ✅ Async processing
- ✅ Human-interpretable explanations

---

## 🎯 IMPLEMENTATION PHASES

### **PHASE 1: Dataset Integration** (4-6 hours)
### **PHASE 2: Model Training** (4-6 hours)
### **PHASE 3: Explainability** (6-8 hours)
### **PHASE 4: Interpretability Bridge** (3-4 hours)
### **PHASE 5: Experiments & Benchmarking** (3-4 hours)

**Total Estimated Time: 20-28 hours**

---

# 📦 PHASE 1: DATASET INTEGRATION (/datasets)

## **CHUNK 1.1: Backend - Kaggle Integration** (2 hours)

### **Step 1.1.1: Install Dependencies**
```bash
cd backend
pip install kaggle opendatasets pandas numpy scikit-learn
```

### **Step 1.1.2: Create Kaggle Service**
**File:** `backend/app/services/kaggle_service.py`

```python
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
import kaggle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

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
                df[col].fillna(df[col].mode()[0], inplace=True)
            
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
            "missing_values": df.isnull().sum().to_dict(),
            "correlations": df[numerical_cols].corr().to_dict(),
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
                "quartiles": df[col].quantile([0.25, 0.5, 0.75]).to_dict()
            }
        
        return stats


# Singleton instance
kaggle_service = KaggleService()
```

### **Step 1.1.3: Create Dataset API Endpoints**
**File:** `backend/app/api/v1/endpoints/home_credit.py`

```python
"""
API endpoints for Home Credit dataset management.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import structlog

from app.services.kaggle_service import kaggle_service
from app.utils.supabase_client import supabase_db

router = APIRouter()
logger = structlog.get_logger()


@router.post("/download")
async def download_home_credit_dataset(background_tasks: BackgroundTasks):
    """
    Download Home Credit dataset from Kaggle.
    Requires KAGGLE_USERNAME and KAGGLE_KEY in environment.
    """
    try:
        logger.info("API: Downloading Home Credit dataset")
        
        # Run download in background
        result = kaggle_service.download_dataset()
        
        return {
            "status": "success",
            "message": "Dataset download initiated",
            "details": result
        }
        
    except Exception as e:
        logger.error("Failed to download dataset", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download dataset: {str(e)}"
        )


@router.post("/preprocess")
async def preprocess_home_credit_dataset():
    """
    Preprocess Home Credit dataset:
    - Handle missing values
    - Encode categorical variables
    - Scale features
    - Train/val/test split
    - Generate EDA statistics
    """
    try:
        logger.info("API: Preprocessing Home Credit dataset")
        
        result = kaggle_service.load_and_preprocess()
        
        # Save metadata to Supabase
        dataset_metadata = {
            "dataset_id": result["dataset_id"],
            "name": "Home Credit Default Risk",
            "source": "Kaggle",
            "n_samples": result["n_samples"],
            "n_features": result["n_features"],
            "train_size": result["train_size"],
            "val_size": result["val_size"],
            "test_size": result["test_size"],
            "target_distribution": result["target_distribution"],
            "status": "processed",
            "eda_stats": result["eda_stats"]
        }
        
        # Insert or update in Supabase
        supabase_db.table('datasets').upsert(dataset_metadata).execute()
        
        logger.info("Dataset preprocessed and saved")
        
        return result
        
    except Exception as e:
        logger.error("Failed to preprocess dataset", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to preprocess dataset: {str(e)}"
        )


@router.get("/eda/{dataset_id}")
async def get_eda_statistics(dataset_id: str):
    """
    Get EDA statistics for visualization.
    """
    try:
        logger.info("API: Getting EDA stats", dataset_id=dataset_id)
        
        # Get from Supabase
        result = supabase_db.table('datasets').select('*').eq('dataset_id', dataset_id).execute()
        
        if not result.data or len(result.data) == 0:
            raise HTTPException(status_code=404, detail="Dataset not found")
        
        dataset = result.data[0]
        
        return {
            "dataset_id": dataset_id,
            "eda_stats": dataset.get("eda_stats", {}),
            "target_distribution": dataset.get("target_distribution", {}),
            "n_samples": dataset.get("n_samples", 0),
            "n_features": dataset.get("n_features", 0)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get EDA stats", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get EDA statistics: {str(e)}"
        )
```

---

## **CHUNK 1.2: Frontend - Dataset Page** (2 hours)

### **Step 1.2.1: Create Dataset Page**
**File:** `frontend/src/app/datasets/home-credit/page.tsx`

```typescript
'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Database,
  Download,
  CheckCircle,
  Loader2,
  BarChart3,
  TrendingUp,
  AlertCircle
} from 'lucide-react';
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

interface DatasetStatus {
  downloaded: boolean;
  processed: boolean;
  n_samples?: number;
  n_features?: number;
  train_size?: number;
  val_size?: number;
  test_size?: number;
}

interface EDAStats {
  distributions: Record<string, any>;
  correlations: Record<string, any>;
  missing_values: Record<string, number>;
  target_distribution: {
    class_0: number;
    class_1: number;
  };
}

export default function HomeCreditDatasetPage() {
  const router = useRouter();
  const [status, setStatus] = useState<DatasetStatus>({
    downloaded: false,
    processed: false
  });
  const [edaStats, setEdaStats] = useState<EDAStats | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkDatasetStatus();
  }, []);

  const checkDatasetStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE}/datasets/home-credit/eda/home-credit-default-risk`);
      
      setStatus({
        downloaded: true,
        processed: true,
        n_samples: response.data.n_samples,
        n_features: response.data.n_features,
        train_size: response.data.eda_stats?.train_size,
        val_size: response.data.eda_stats?.val_size,
        test_size: response.data.eda_stats?.test_size
      });
      
      setEdaStats(response.data.eda_stats);
    } catch (error) {
      // Dataset not yet downloaded/processed
      console.log('Dataset not ready yet');
    }
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    setError(null);
    
    try {
      await axios.post(`${API_BASE}/datasets/home-credit/download`);
      setStatus(prev => ({ ...prev, downloaded: true }));
      alert('Dataset downloaded successfully! Now preprocessing...');
      await handlePreprocess();
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to download dataset');
    } finally {
      setIsDownloading(false);
    }
  };

  const handlePreprocess = async () => {
    setIsProcessing(true);
    setError(null);
    
    try {
      const response = await axios.post(`${API_BASE}/datasets/home-credit/preprocess`);
      
      setStatus({
        downloaded: true,
        processed: true,
        n_samples: response.data.n_samples,
        n_features: response.data.n_features,
        train_size: response.data.train_size,
        val_size: response.data.val_size,
        test_size: response.data.test_size
      });
      
      setEdaStats(response.data.eda_stats);
      
      alert('Dataset preprocessed successfully!');
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to preprocess dataset');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <div className="bg-white border-b shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl">
              <Database className="h-8 w-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Home Credit Default Risk Dataset
              </h1>
              <p className="text-gray-600 mt-1">
                Kaggle Competition Dataset for Credit Risk Assessment
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-600" />
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Data Preparation Checklist */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            Data Preparation Steps
          </h2>
          
          <div className="space-y-3">
            <div className="flex items-center space-x-3">
              {status.downloaded ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.downloaded ? 'text-green-900' : 'text-gray-600'}>
                Dataset Downloaded from Kaggle
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900' : 'text-gray-600'}>
                Data Cleaning & Feature Engineering
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900' : 'text-gray-600'}>
                Train/Validation/Test Split
              </span>
            </div>
            
            <div className="flex items-center space-x-3">
              {status.processed ? (
                <CheckCircle className="h-5 w-5 text-green-600" />
              ) : (
                <div className="h-5 w-5 rounded-full border-2 border-gray-300" />
              )}
              <span className={status.processed ? 'text-green-900' : 'text-gray-600'}>
                Dataset Version Stored
              </span>
            </div>
          </div>

          {!status.downloaded && (
            <button
              onClick={handleDownload}
              disabled={isDownloading}
              className="mt-6 flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              {isDownloading ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Downloading...</span>
                </>
              ) : (
                <>
                  <Download className="h-5 w-5" />
                  <span>Download Dataset</span>
                </>
              )}
            </button>
          )}

          {status.downloaded && !status.processed && (
            <button
              onClick={handlePreprocess}
              disabled={isProcessing}
              className="mt-6 flex items-center space-x-2 px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-50"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <BarChart3 className="h-5 w-5" />
                  <span>Preprocess Dataset</span>
                </>
              )}
            </button>
          )}
        </div>

        {/* Dataset Statistics */}
        {status.processed && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="text-sm text-gray-600 mb-1">Total Samples</div>
              <div className="text-3xl font-bold text-gray-900">
                {status.n_samples?.toLocaleString()}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="text-sm text-gray-600 mb-1">Features</div>
              <div className="text-3xl font-bold text-gray-900">
                {status.n_features}
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="text-sm text-gray-600 mb-1">Train / Val / Test</div>
              <div className="text-lg font-bold text-gray-900">
                {status.train_size?.toLocaleString()} / {status.val_size?.toLocaleString()} / {status.test_size?.toLocaleString()}
              </div>
            </div>
          </div>
        )}

        {/* EDA Visualizations */}
        {edaStats && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-6">
              Exploratory Data Analysis
            </h2>
            
            {/* Target Distribution */}
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Target Distribution
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="text-sm text-green-700 mb-1">No Default (Class 0)</div>
                  <div className="text-2xl font-bold text-green-900">
                    {edaStats.target_distribution?.class_0?.toLocaleString()}
                  </div>
                </div>
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="text-sm text-red-700 mb-1">Default (Class 1)</div>
                  <div className="text-2xl font-bold text-red-900">
                    {edaStats.target_distribution?.class_1?.toLocaleString()}
                  </div>
                </div>
              </div>
            </div>

            {/* Feature Distributions */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-4">
                Key Feature Statistics
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Feature
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Mean
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Std Dev
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Min / Max
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {Object.entries(edaStats.distributions || {}).slice(0, 10).map(([feature, stats]: [string, any]) => (
                      <tr key={feature}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {feature}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {stats.mean?.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {stats.std?.toFixed(2)}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                          {stats.min?.toFixed(2)} / {stats.max?.toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

This is **CHUNK 1** (Dataset Integration). 

**Status:** Ready to implement
**Files to create:**
1. `backend/app/services/kaggle_service.py`
2. `backend/app/api/v1/endpoints/home_credit.py`
3. `frontend/src/app/datasets/home-credit/page.tsx`

**Next:** Should I continue with CHUNK 2 (Model Training), or do you want to implement CHUNK 1 first and test it?
