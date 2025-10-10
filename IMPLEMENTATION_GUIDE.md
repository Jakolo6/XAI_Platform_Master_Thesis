# 🛠️ IMPLEMENTATION GUIDE
## Step-by-Step Evolution to Multi-Dataset Platform

**Target:** Transform XAI Platform into open-source research tool with Supabase

---

## 🎯 PHASE 1: SUPABASE SETUP (Week 1)

### Day 1: Supabase Project Setup

#### 1.1 Create Supabase Project
```bash
# 1. Go to https://supabase.com
# 2. Sign up / Log in
# 3. Create new project
#    - Name: xai-research-platform
#    - Database Password: [secure password]
#    - Region: [closest to you]
```

#### 1.2 Get Credentials
```bash
# From Supabase Dashboard → Settings → API
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

#### 1.3 Update Environment Variables
```bash
# backend/.env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your_anon_key
SUPABASE_SERVICE_KEY=your_service_key

# Keep existing PostgreSQL for local development
DATABASE_URL=postgresql+asyncpg://xai_user:xai_password@localhost:5432/xai_db
```

### Day 2: Database Migration

#### 2.1 Create Migration Script
```sql
-- supabase/migrations/001_initial_schema.sql

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Datasets table
CREATE TABLE datasets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL UNIQUE,
    display_name VARCHAR(255),
    description TEXT,
    
    -- Source
    source VARCHAR(50) NOT NULL,
    source_identifier VARCHAR(255),
    kaggle_dataset VARCHAR(255),
    kaggle_competition VARCHAR(255),
    
    -- Configuration
    target_column VARCHAR(100),
    positive_class VARCHAR(50),
    split_ratios JSONB DEFAULT '{"train": 0.7, "val": 0.15, "test": 0.15}',
    
    -- Preprocessing
    preprocessing_pipeline JSONB,
    feature_engineering JSONB,
    
    -- Statistics
    total_samples INTEGER,
    num_features INTEGER,
    class_balance JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    -- Metadata
    license VARCHAR(255),
    citation TEXT,
    tags JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Models table
CREATE TABLE models (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    
    -- Dataset reference
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    
    -- Configuration
    hyperparameters JSONB,
    training_config JSONB,
    
    -- Storage
    model_path VARCHAR(500),
    model_hash VARCHAR(64) UNIQUE,
    model_size_mb FLOAT,
    
    -- Training
    training_time_seconds FLOAT,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Model metrics table
CREATE TABLE model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models(id) ON DELETE CASCADE,
    
    -- Classification metrics
    auc_roc FLOAT,
    auc_pr FLOAT,
    f1_score FLOAT,
    precision FLOAT,
    recall FLOAT,
    accuracy FLOAT,
    log_loss FLOAT,
    brier_score FLOAT,
    
    -- Calibration
    expected_calibration_error FLOAT,
    maximum_calibration_error FLOAT,
    
    -- Confusion matrix
    confusion_matrix JSONB,
    class_metrics JSONB,
    additional_metrics JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Explanations table (NEW)
CREATE TABLE explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES models(id) ON DELETE CASCADE,
    dataset_id UUID REFERENCES datasets(id) ON DELETE CASCADE,
    
    -- Method
    method VARCHAR(50) NOT NULL,  -- 'shap' or 'lime'
    type VARCHAR(50) NOT NULL,    -- 'global' or 'local'
    
    -- Summary data (aggregated, not raw)
    summary_json JSONB,
    top_features JSONB,
    feature_importance JSONB,
    
    -- Quality metrics
    faithfulness_score FLOAT,
    robustness_score FLOAT,
    complexity_score FLOAT,
    overall_quality FLOAT,
    
    -- Metadata
    num_samples INTEGER,
    num_features INTEGER,
    computation_time_seconds FLOAT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Experiments table (NEW)
CREATE TABLE experiments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    description TEXT,
    
    dataset_id UUID REFERENCES datasets(id),
    model_id UUID REFERENCES models(id),
    
    config JSONB,
    results JSONB,
    metrics JSONB,
    
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Benchmarks table (NEW)
CREATE TABLE benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255),
    description TEXT,
    
    dataset_ids JSONB,
    model_ids JSONB,
    metrics JSONB,
    
    results JSONB,
    summary JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_models_dataset ON models(dataset_id);
CREATE INDEX idx_models_type ON models(model_type);
CREATE INDEX idx_metrics_model ON model_metrics(model_id);
CREATE INDEX idx_explanations_model ON explanations(model_id);
CREATE INDEX idx_explanations_dataset ON explanations(dataset_id);
CREATE INDEX idx_explanations_method ON explanations(method);
CREATE INDEX idx_experiments_dataset ON experiments(dataset_id);
CREATE INDEX idx_experiments_model ON experiments(model_id);

-- Row Level Security (RLS)
ALTER TABLE datasets ENABLE ROW LEVEL SECURITY;
ALTER TABLE models ENABLE ROW LEVEL SECURITY;
ALTER TABLE model_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE explanations ENABLE ROW LEVEL SECURITY;
ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE benchmarks ENABLE ROW LEVEL SECURITY;

-- Policies (allow all for now, refine later)
CREATE POLICY "Allow all access to datasets" ON datasets FOR ALL USING (true);
CREATE POLICY "Allow all access to models" ON models FOR ALL USING (true);
CREATE POLICY "Allow all access to metrics" ON model_metrics FOR ALL USING (true);
CREATE POLICY "Allow all access to explanations" ON explanations FOR ALL USING (true);
CREATE POLICY "Allow all access to experiments" ON experiments FOR ALL USING (true);
CREATE POLICY "Allow all access to benchmarks" ON benchmarks FOR ALL USING (true);
```

#### 2.2 Run Migration
```bash
# In Supabase Dashboard → SQL Editor
# Paste and run the migration script above
```

### Day 3: Supabase Client Implementation

#### 3.1 Install Dependencies
```bash
cd backend
pip install supabase-py python-dotenv
```

#### 3.2 Create Supabase Client
```python
# backend/app/supabase/__init__.py
from .client import get_supabase_client

__all__ = ['get_supabase_client']
```

```python
# backend/app/supabase/client.py
"""Supabase client for metadata storage."""

from supabase import create_client, Client
from typing import Optional, Dict, Any, List
import structlog
from app.core.config import settings

logger = structlog.get_logger()

class SupabaseClient:
    """Supabase client wrapper."""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_KEY
        )
        logger.info("Supabase client initialized")
    
    # ========== DATASETS ==========
    
    async def get_datasets(self, is_active: bool = True) -> List[Dict]:
        """Get all datasets."""
        try:
            query = self.client.table('datasets').select('*')
            if is_active:
                query = query.eq('is_active', True)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error("Failed to get datasets", error=str(e))
            raise
    
    async def get_dataset(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset by ID."""
        try:
            response = self.client.table('datasets').select('*').eq('id', dataset_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error("Failed to get dataset", dataset_id=dataset_id, error=str(e))
            raise
    
    async def insert_dataset(self, dataset_data: Dict[str, Any]) -> Dict:
        """Insert new dataset."""
        try:
            response = self.client.table('datasets').insert(dataset_data).execute()
            logger.info("Dataset inserted", dataset_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert dataset", error=str(e))
            raise
    
    async def update_dataset(self, dataset_id: str, updates: Dict[str, Any]) -> Dict:
        """Update dataset."""
        try:
            response = self.client.table('datasets').update(updates).eq('id', dataset_id).execute()
            return response.data[0]
        except Exception as e:
            logger.error("Failed to update dataset", dataset_id=dataset_id, error=str(e))
            raise
    
    # ========== MODELS ==========
    
    async def get_models(self, dataset_id: Optional[str] = None) -> List[Dict]:
        """Get models, optionally filtered by dataset."""
        try:
            query = self.client.table('models').select('*')
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error("Failed to get models", error=str(e))
            raise
    
    async def insert_model(self, model_data: Dict[str, Any]) -> Dict:
        """Insert new model."""
        try:
            response = self.client.table('models').insert(model_data).execute()
            logger.info("Model inserted", model_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert model", error=str(e))
            raise
    
    async def insert_model_metrics(self, metrics_data: Dict[str, Any]) -> Dict:
        """Insert model metrics."""
        try:
            response = self.client.table('model_metrics').insert(metrics_data).execute()
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert metrics", error=str(e))
            raise
    
    # ========== EXPLANATIONS ==========
    
    async def insert_explanation(self, explanation_data: Dict[str, Any]) -> Dict:
        """Insert explanation summary."""
        try:
            response = self.client.table('explanations').insert(explanation_data).execute()
            logger.info("Explanation inserted", explanation_id=response.data[0]['id'])
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert explanation", error=str(e))
            raise
    
    async def get_explanations(
        self, 
        model_id: Optional[str] = None,
        dataset_id: Optional[str] = None,
        method: Optional[str] = None
    ) -> List[Dict]:
        """Get explanations with optional filters."""
        try:
            query = self.client.table('explanations').select('*')
            if model_id:
                query = query.eq('model_id', model_id)
            if dataset_id:
                query = query.eq('dataset_id', dataset_id)
            if method:
                query = query.eq('method', method)
            response = query.execute()
            return response.data
        except Exception as e:
            logger.error("Failed to get explanations", error=str(e))
            raise
    
    # ========== EXPERIMENTS ==========
    
    async def insert_experiment(self, experiment_data: Dict[str, Any]) -> Dict:
        """Insert experiment."""
        try:
            response = self.client.table('experiments').insert(experiment_data).execute()
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert experiment", error=str(e))
            raise
    
    # ========== BENCHMARKS ==========
    
    async def insert_benchmark(self, benchmark_data: Dict[str, Any]) -> Dict:
        """Insert benchmark results."""
        try:
            response = self.client.table('benchmarks').insert(benchmark_data).execute()
            return response.data[0]
        except Exception as e:
            logger.error("Failed to insert benchmark", error=str(e))
            raise
    
    async def get_benchmarks(self) -> List[Dict]:
        """Get all benchmarks."""
        try:
            response = self.client.table('benchmarks').select('*').execute()
            return response.data
        except Exception as e:
            logger.error("Failed to get benchmarks", error=str(e))
            raise


# Singleton instance
_supabase_client: Optional[SupabaseClient] = None

def get_supabase_client() -> SupabaseClient:
    """Get or create Supabase client singleton."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
```

#### 3.3 Update Config
```python
# backend/app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # ... existing settings ...
    
    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""
    
    class Config:
        env_file = ".env"
```

---

## 🎯 PHASE 2: DATASET REGISTRY (Week 2)

### Day 4: Dataset Registry Configuration

#### 4.1 Create Dataset Registry Config
```yaml
# config/datasets.yaml
datasets:
  - id: ieee-cis-fraud
    name: ieee-cis-fraud
    display_name: "IEEE-CIS Fraud Detection"
    description: "IEEE Computational Intelligence Society fraud detection dataset from Kaggle"
    source: kaggle
    kaggle_competition: ieee-fraud-detection
    target_column: isFraud
    positive_class: 1
    split_ratios:
      train: 0.7
      val: 0.15
      test: 0.15
    preprocessing_pipeline:
      - handle_missing_values
      - encode_categorical
      - scale_numerical
    feature_engineering:
      - transaction_frequency
      - amount_statistics
    license: "Kaggle Competition License"
    citation: "IEEE-CIS Fraud Detection, Kaggle 2019"
    tags:
      - fraud-detection
      - financial
      - imbalanced
  
  - id: givemesomecredit
    name: givemesomecredit
    display_name: "Give Me Some Credit"
    description: "Credit default prediction dataset"
    source: kaggle
    kaggle_dataset: brycecf/give-me-some-credit-dataset
    target_column: SeriousDlqin2yrs
    positive_class: 1
    split_ratios:
      train: 0.7
      val: 0.15
      test: 0.15
    preprocessing_pipeline:
      - handle_missing_values
      - remove_outliers
      - scale_numerical
    license: "CC0: Public Domain"
    citation: "Give Me Some Credit, Kaggle 2011"
    tags:
      - credit-risk
      - financial
      - classification
  
  - id: german-credit
    name: german-credit
    display_name: "German Credit Risk"
    description: "German credit risk classification dataset"
    source: kaggle
    kaggle_dataset: uciml/german-credit
    target_column: Risk
    positive_class: bad
    split_ratios:
      train: 0.7
      val: 0.15
      test: 0.15
    preprocessing_pipeline:
      - encode_categorical
      - scale_numerical
    license: "CC0: Public Domain"
    citation: "UCI Machine Learning Repository"
    tags:
      - credit-risk
      - financial
      - small-dataset
```

#### 4.2 Create Dataset Registry Loader
```python
# backend/app/datasets/registry.py
"""Dataset registry management."""

import yaml
from pathlib import Path
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()

class DatasetRegistry:
    """Manages dataset configurations."""
    
    def __init__(self, config_path: str = "config/datasets.yaml"):
        self.config_path = Path(config_path)
        self.datasets = self._load_registry()
    
    def _load_registry(self) -> Dict[str, Dict]:
        """Load dataset registry from YAML."""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            datasets = {}
            for dataset in config.get('datasets', []):
                datasets[dataset['id']] = dataset
            
            logger.info("Dataset registry loaded", count=len(datasets))
            return datasets
        except Exception as e:
            logger.error("Failed to load dataset registry", error=str(e))
            return {}
    
    def get_dataset_config(self, dataset_id: str) -> Optional[Dict]:
        """Get dataset configuration by ID."""
        return self.datasets.get(dataset_id)
    
    def list_datasets(self) -> List[Dict]:
        """List all datasets."""
        return list(self.datasets.values())
    
    def add_dataset(self, dataset_config: Dict):
        """Add new dataset to registry."""
        dataset_id = dataset_config['id']
        self.datasets[dataset_id] = dataset_config
        self._save_registry()
    
    def _save_registry(self):
        """Save registry to YAML."""
        try:
            config = {'datasets': list(self.datasets.values())}
            with open(self.config_path, 'w') as f:
                yaml.dump(config, f, default_flow_style=False)
            logger.info("Dataset registry saved")
        except Exception as e:
            logger.error("Failed to save dataset registry", error=str(e))


# Singleton
_registry: Optional[DatasetRegistry] = None

def get_dataset_registry() -> DatasetRegistry:
    """Get dataset registry singleton."""
    global _registry
    if _registry is None:
        _registry = DatasetRegistry()
    return _registry
```

### Day 5-6: Dataset Loaders

#### 5.1 Base Dataset Loader
```python
# backend/app/datasets/loaders/base.py
"""Base dataset loader."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
import structlog

logger = structlog.get_logger()

class BaseDatasetLoader(ABC):
    """Base class for dataset loaders."""
    
    def __init__(self, dataset_id: str, config: Dict):
        self.dataset_id = dataset_id
        self.config = config
        self.data_dir = Path(f"data/{dataset_id}")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    async def download(self) -> Path:
        """Download dataset from source."""
        pass
    
    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess dataset."""
        pass
    
    def split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split dataset into train/val/test."""
        ratios = self.config.get('split_ratios', {
            'train': 0.7,
            'val': 0.15,
            'test': 0.15
        })
        
        # Shuffle
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Calculate split points
        n = len(df)
        train_end = int(n * ratios['train'])
        val_end = train_end + int(n * ratios['val'])
        
        train_df = df[:train_end]
        val_df = df[train_end:val_end]
        test_df = df[val_end:]
        
        logger.info(
            "Dataset split",
            dataset_id=self.dataset_id,
            train=len(train_df),
            val=len(val_df),
            test=len(test_df)
        )
        
        return train_df, val_df, test_df
    
    def save_splits(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ):
        """Save splits to parquet files."""
        train_df.to_parquet(self.data_dir / "train.parquet", index=False)
        val_df.to_parquet(self.data_dir / "validation.parquet", index=False)
        test_df.to_parquet(self.data_dir / "test.parquet", index=False)
        
        logger.info("Dataset splits saved", dataset_id=self.dataset_id)
    
    def load_splits(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load splits from parquet files."""
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "validation.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")
        
        return train_df, val_df, test_df
```

#### 5.2 IEEE-CIS Loader
```python
# backend/app/datasets/loaders/ieee_cis.py
"""IEEE-CIS Fraud Detection dataset loader."""

from pathlib import Path
import pandas as pd
from .base import BaseDatasetLoader
from app.utils.kaggle_client import download_kaggle_competition

class IEEECISLoader(BaseDatasetLoader):
    """Loader for IEEE-CIS Fraud Detection dataset."""
    
    async def download(self) -> Path:
        """Download from Kaggle."""
        competition = self.config['kaggle_competition']
        return await download_kaggle_competition(
            competition,
            self.data_dir
        )
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess IEEE-CIS dataset."""
        # Handle missing values
        df = df.fillna(df.median(numeric_only=True))
        
        # Encode categorical
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].astype('category').cat.codes
        
        # Scale numerical
        from sklearn.preprocessing import StandardScaler
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numerical_cols = [c for c in numerical_cols if c != self.config['target_column']]
        
        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
        
        return df
```

This is getting very long. Should I continue with the full implementation guide, or would you prefer I create a more concise action plan for immediate next steps?

