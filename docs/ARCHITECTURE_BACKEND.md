# Backend Architecture - XAI Research Platform

## Overview

The XAI Research Platform backend is built on a **unified, modular architecture** that prevents regressions and ensures data consistency across all modules.

### Core Principles

1. **Single Source of Truth**: All data access goes through the Data Access Layer (DAL)
2. **Service Inheritance**: All services inherit from base classes for consistency
3. **Centralized Metrics**: One metrics service for all metric computation and storage
4. **Standardized Schemas**: Consistent database schemas with versioning
5. **Regression Protection**: Automated integrity tests validate data consistency

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     API Endpoints Layer                      │
│  /models  /datasets  /interpretation  /explanations  /etc   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Service Layer                             │
│  ModelService  DatasetService  InterpretationService  etc   │
│  (All inherit from XAIService base class)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│              Data Access Layer (DAL)                         │
│  Unified interface for all data operations                  │
│  - Models & Metrics                                         │
│  - Datasets & Preprocessing                                 │
│  - Explanations (SHAP, LIME)                                │
│  - Interpretation Feedback                                  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────────┐
│                  Storage Layer                               │
│  Supabase (PostgreSQL)  │  R2 (S3-compatible)              │
│  - Metadata & Metrics   │  - Model Files                    │
│  - Datasets Registry    │  - Large Datasets                 │
│  - Feedback Data        │  - Explanation Artifacts          │
└──────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Model Training Flow

```
1. User Request → POST /api/v1/models/train
   ↓
2. ModelService.train_model()
   ├─ Validates dataset via DAL
   ├─ Trains model
   ├─ Computes metrics via MetricsService
   └─ Saves to DAL
   ↓
3. DAL.create_model() + DAL.save_model_metrics()
   ├─ Adds metadata (last_updated, source_module)
   ├─ Validates schema
   └─ Writes to Supabase
   ↓
4. Model + Metrics stored consistently
```

### Metrics Retrieval Flow

```
1. User Request → GET /api/v1/models/{id}
   ↓
2. Endpoint calls DAL.get_model(id, include_metrics=True)
   ↓
3. DAL fetches model + enriches with metrics
   ├─ Strips _metrics suffix if present
   ├─ Fetches from models table
   └─ Joins with model_metrics table
   ↓
4. Returns unified model+metrics object
```

### Interpretation Flow

```
1. User Request → POST /api/v1/interpretation/generate
   ↓
2. InterpretationService.generate_interpretation()
   ├─ Gets model via DAL
   ├─ Gets SHAP data via DAL
   ├─ Generates interpretation (LLM or Rule-based)
   └─ Saves feedback via DAL
   ↓
3. DAL.save_interpretation_feedback()
   ├─ Adds metadata
   └─ Stores in interpretation_feedback table
   ↓
4. Feedback available for research analysis
```

---

## Core Components

### 1. Data Access Layer (DAL)

**File:** `backend/app/core/data_access.py`

**Purpose:** Single point of access for all data operations

**Key Methods:**
- `get_model(model_id, include_metrics)` - Get model with optional metrics
- `list_models(dataset_id, include_metrics, status)` - List models with filtering
- `save_model_metrics(model_id, metrics, source_module)` - Save metrics
- `get_explanation(model_id, method)` - Get SHAP/LIME explanation
- `save_interpretation_feedback(feedback_data)` - Save research feedback

**Features:**
- Automatic `_metrics` suffix handling
- Metadata injection (`last_updated`, `source_module`)
- Consistent error handling
- Logging for all operations

### 2. Base Service Classes

**File:** `backend/app/core/base_service.py`

**Classes:**
- `XAIService` - Base for all services
- `ModelServiceBase` - Base for model-related services
- `DatasetServiceBase` - Base for dataset-related services
- `ExplanationServiceBase` - Base for explanation services
- `InterpretationServiceBase` - Base for interpretation services

**Provides:**
- Standardized logging with service name
- Error handling and recovery
- Configuration validation
- DAL access

**Usage:**
```python
class MyService(ModelServiceBase):
    def __init__(self):
        super().__init__(service_name="my_service")
    
    def get_service_status(self):
        return {"status": "operational"}
    
    def my_operation(self):
        # Use self.dal for data access
        model = self.dal.get_model("model_id")
        # Use self.logger for logging
        self.logger.info("Operation completed")
```

### 3. Centralized Metrics Service

**File:** `backend/app/services/metrics_service.py`

**Purpose:** Single source of truth for all metric computation

**Key Methods:**
- `compute_all_metrics(y_true, y_pred, y_pred_proba)` - Compute all metrics
- `save_metrics(model_id, metrics)` - Save metrics via DAL
- `get_metrics(model_id)` - Retrieve metrics via DAL
- `compare_metrics(model_ids)` - Compare multiple models
- `validate_metrics(metrics)` - Validate metric schema

**Computed Metrics:**
- Classification: accuracy, precision, recall, F1
- Probabilistic: AUC-ROC, AUC-PR, log loss, Brier score
- Calibration: ECE, MCE
- Curves: ROC curve, PR curve
- Confusion matrix

---

## Database Schema Standards

### Models Table

```sql
CREATE TABLE models (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255),
    model_type VARCHAR(50),
    status VARCHAR(50),
    dataset_id VARCHAR(255),
    version VARCHAR(50),
    hyperparameters JSONB,
    training_time_seconds FLOAT,
    
    -- Metadata fields (added by DAL)
    last_updated TIMESTAMPTZ,
    source_module VARCHAR(100),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Model Metrics Table

```sql
CREATE TABLE model_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) REFERENCES models(id) ON DELETE CASCADE,
    
    -- Classification metrics
    accuracy FLOAT,
    precision FLOAT,
    recall FLOAT,
    f1_score FLOAT,
    
    -- Probabilistic metrics
    auc_roc FLOAT,
    auc_pr FLOAT,
    log_loss FLOAT,
    brier_score FLOAT,
    
    -- Confusion matrix
    confusion_matrix JSONB,
    
    -- Calibration
    expected_calibration_error FLOAT,
    maximum_calibration_error FLOAT,
    
    -- Curves
    roc_curve JSONB,
    pr_curve JSONB,
    
    -- Metadata
    last_updated TIMESTAMPTZ,
    source_module VARCHAR(100),
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(model_id)
);
```

### Explanations Table

```sql
CREATE TABLE explanations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id VARCHAR(255) REFERENCES models(id) ON DELETE CASCADE,
    method VARCHAR(50), -- 'shap' or 'lime'
    status VARCHAR(50),
    
    feature_importance JSONB,
    explanation_data JSONB,
    
    -- Metadata
    last_updated TIMESTAMPTZ,
    source_module VARCHAR(100),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Interpretation Feedback Table

```sql
CREATE TABLE interpretation_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    interpretation_id VARCHAR(255),
    model_id VARCHAR(255),
    mode VARCHAR(50), -- 'llm' or 'rule-based'
    
    -- Ratings (1-5)
    clarity INT CHECK (clarity BETWEEN 1 AND 5),
    trustworthiness INT CHECK (trustworthiness BETWEEN 1 AND 5),
    fairness INT CHECK (fairness BETWEEN 1 AND 5),
    
    comments TEXT,
    user_id VARCHAR(255),
    
    -- Metadata
    last_updated TIMESTAMPTZ,
    source_module VARCHAR(100),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## Service Registry Pattern

All services are registered and can be accessed through a central registry:

**File:** `backend/app/core/service_registry.py` (to be created)

```python
from app.services.model_service import model_service
from app.services.dataset_service import dataset_service
from app.services.metrics_service import metrics_service
from app.services.interpretation_service import interpretation_service

class ServiceRegistry:
    """Central registry for all services."""
    
    def __init__(self):
        self.model = model_service
        self.dataset = dataset_service
        self.metrics = metrics_service
        self.interpretation = interpretation_service
    
    def get_all_status(self):
        """Get status of all services."""
        return {
            'model': self.model.get_service_status(),
            'dataset': self.dataset.get_service_status(),
            'metrics': self.metrics.get_service_status(),
            'interpretation': self.interpretation.get_service_status()
        }

services = ServiceRegistry()
```

---

## Regression Protection

### Automated Integrity Tests

**File:** `backend/tests/test_integrity.py`

**Tests:**
1. **Data Integrity**
   - Every completed model has all required metrics
   - All metrics follow consistent schema
   - All models have required metadata fields

2. **Service Integrity**
   - Metrics service is operational
   - Metrics validation works correctly
   - Metrics can be retrieved for all models

3. **DAL Integrity**
   - Model retrieval with/without metrics works
   - `_metrics` suffix handling works
   - Model filtering works correctly

4. **Configuration Integrity**
   - Required config is present
   - Optional config is handled gracefully

**Run Tests:**
```bash
cd backend
pytest tests/test_integrity.py -v
```

### Pre-Deployment Checklist

Before deploying to Railway:

- [ ] Run integrity tests: `pytest tests/test_integrity.py`
- [ ] Verify all services operational: `GET /api/v1/health`
- [ ] Check DAL connection: Verify Supabase connectivity
- [ ] Validate config: Ensure all required env vars set
- [ ] Test metric consistency: Verify no missing metrics

---

## Configuration Management

**File:** `backend/app/core/config.py`

All configuration loaded through single `Settings` class:

```python
class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    
    # R2 Storage
    R2_BUCKET_NAME: str
    R2_ACCESS_KEY_ID: str
    R2_SECRET_ACCESS_KEY: str
    
    # OpenAI (optional)
    OPENAI_API_KEY: str = ""
    
    # Kaggle (optional)
    KAGGLE_USERNAME: str = ""
    KAGGLE_KEY: str = ""
```

**Validation:**
- Required fields raise error if missing
- Optional fields have defaults
- Services validate their specific requirements on init

---

## Migration Guide

### Updating Existing Services

**Before (Direct Supabase access):**
```python
def get_model(model_id):
    result = supabase_db.client.table('models').select('*').eq('id', model_id).execute()
    return result.data[0] if result.data else None
```

**After (Using DAL):**
```python
from app.core.data_access import dal

def get_model(model_id):
    return dal.get_model(model_id, include_metrics=True)
```

### Updating Endpoints

**Before:**
```python
@router.get("/{model_id}")
async def get_model(model_id: str):
    model = supabase_db.get_model(model_id)
    metrics = supabase_db.get_model_metrics(model_id)
    return {**model, **metrics}
```

**After:**
```python
from app.core.data_access import dal

@router.get("/{model_id}")
async def get_model(model_id: str):
    return dal.get_model(model_id, include_metrics=True)
```

---

## Deployment

### Railway Environment Variables

Required:
```
SUPABASE_URL=https://...
SUPABASE_SERVICE_KEY=eyJ...
R2_BUCKET_NAME=xai-platform-datasets
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
```

Optional:
```
OPENAI_API_KEY=sk-...
KAGGLE_USERNAME=...
KAGGLE_KEY=...
```

### Health Check

```bash
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "services": {
    "model": "operational",
    "dataset": "operational",
    "metrics": "operational",
    "interpretation": "operational"
  }
}
```

---

## Best Practices

### 1. Always Use DAL for Data Access
```python
# ✅ Good
model = dal.get_model(model_id)

# ❌ Bad
model = supabase_db.client.table('models').select('*').eq('id', model_id).execute()
```

### 2. Inherit from Base Services
```python
# ✅ Good
class MyService(ModelServiceBase):
    def __init__(self):
        super().__init__(service_name="my_service")

# ❌ Bad
class MyService:
    def __init__(self):
        self.db = supabase_db
```

### 3. Use Metrics Service for All Metrics
```python
# ✅ Good
metrics = metrics_service.compute_all_metrics(y_true, y_pred, y_pred_proba)
metrics_service.save_metrics(model_id, metrics)

# ❌ Bad
metrics = {'accuracy': accuracy_score(y_true, y_pred)}
supabase_db.client.table('model_metrics').insert(metrics).execute()
```

### 4. Add Metadata to All Updates
```python
# ✅ Good (DAL does this automatically)
dal.update_model(model_id, updates, source_module="my_service")

# ❌ Bad (missing metadata)
supabase_db.client.table('models').update(updates).eq('id', model_id).execute()
```

---

## Troubleshooting

### Metrics Not Showing

**Symptom:** Model page shows dashes instead of metrics

**Solution:**
1. Check if metrics exist: `dal.get_model_metrics(model_id)`
2. Verify model was trained with new system
3. Check `model_metrics` table in Supabase
4. Run integrity tests

### Service Not Operational

**Symptom:** Service status shows error

**Solution:**
1. Check service logs in Railway
2. Verify configuration: `service._validate_config()`
3. Check DAL connection: `dal.db.is_available()`
4. Verify Supabase credentials

### Data Inconsistency

**Symptom:** Different pages show different data

**Solution:**
1. Run integrity tests: `pytest tests/test_integrity.py`
2. Check `last_updated` and `source_module` fields
3. Verify all endpoints use DAL
4. Clear any cached data

---

## Future Enhancements

1. **Caching Layer**: Add Redis for frequently accessed data
2. **Event System**: Publish events when data changes
3. **Audit Trail**: Track all data modifications
4. **Versioning**: Support multiple model versions
5. **Rollback**: Ability to rollback to previous states

---

## Contact

For questions about the backend architecture:
- Check this documentation
- Review code comments in `app/core/`
- Run integrity tests
- Check Railway logs

**Last Updated:** October 2025
**Version:** 1.0
