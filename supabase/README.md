# 🗄️ Supabase Database Documentation

## Overview

This directory contains the Supabase database schema and migration scripts for the XAI Research Platform.

---

## 📊 Database Schema

### Tables

#### 1. **datasets**
Stores dataset metadata and configuration.

**Columns:**
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Unique dataset identifier
- `display_name` (VARCHAR) - Human-readable name
- `description` (TEXT) - Dataset description
- `source` (VARCHAR) - Source type: 'kaggle', 'upload', 'url'
- `source_identifier` (VARCHAR) - Source-specific ID
- `kaggle_dataset` (VARCHAR) - Kaggle dataset path
- `kaggle_competition` (VARCHAR) - Kaggle competition name
- `target_column` (VARCHAR) - Target variable name
- `positive_class` (VARCHAR) - Positive class label
- `split_ratios` (JSONB) - Train/val/test split ratios
- `preprocessing_pipeline` (JSONB) - Preprocessing steps
- `feature_engineering` (JSONB) - Feature engineering config
- `total_samples` (INTEGER) - Total number of samples
- `num_features` (INTEGER) - Number of features
- `class_balance` (JSONB) - Class distribution
- `status` (VARCHAR) - Processing status
- `error_message` (TEXT) - Error details if failed
- `license` (VARCHAR) - Dataset license
- `citation` (TEXT) - Citation information
- `tags` (JSONB) - Dataset tags
- `is_active` (BOOLEAN) - Active status
- `created_at`, `updated_at`, `completed_at` (TIMESTAMP)

#### 2. **models**
Stores trained model metadata.

**Columns:**
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Model name
- `model_type` (VARCHAR) - Algorithm type (xgboost, lightgbm, etc.)
- `version` (VARCHAR) - Model version
- `dataset_id` (UUID) - Foreign key to datasets
- `hyperparameters` (JSONB) - Model hyperparameters
- `training_config` (JSONB) - Training configuration
- `model_path` (VARCHAR) - Storage path
- `model_hash` (VARCHAR) - SHA256 hash for versioning
- `model_size_mb` (FLOAT) - Model file size
- `training_time_seconds` (FLOAT) - Training duration
- `status` (VARCHAR) - Training status
- `error_message` (TEXT) - Error details if failed
- `created_at`, `updated_at`, `completed_at` (TIMESTAMP)

#### 3. **model_metrics**
Stores model performance metrics.

**Columns:**
- `id` (UUID) - Primary key
- `model_id` (UUID) - Foreign key to models
- `auc_roc`, `auc_pr`, `f1_score`, `precision`, `recall`, `accuracy` (FLOAT)
- `log_loss`, `brier_score` (FLOAT)
- `expected_calibration_error`, `maximum_calibration_error` (FLOAT)
- `confusion_matrix` (JSONB) - Confusion matrix
- `class_metrics` (JSONB) - Per-class metrics
- `additional_metrics` (JSONB) - Other metrics
- `created_at` (TIMESTAMP)

#### 4. **explanations**
Stores explanation summaries (not raw data).

**Columns:**
- `id` (UUID) - Primary key
- `model_id` (UUID) - Foreign key to models
- `dataset_id` (UUID) - Foreign key to datasets
- `method` (VARCHAR) - 'shap' or 'lime'
- `type` (VARCHAR) - 'global' or 'local'
- `summary_json` (JSONB) - Aggregated explanation data
- `top_features` (JSONB) - Top important features
- `feature_importance` (JSONB) - Feature importance scores
- `faithfulness_score`, `robustness_score`, `complexity_score` (FLOAT)
- `overall_quality` (FLOAT) - Overall quality score
- `num_samples`, `num_features` (INTEGER)
- `computation_time_seconds` (FLOAT)
- `created_at`, `updated_at` (TIMESTAMP)

#### 5. **experiments**
Tracks experimental runs.

**Columns:**
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Experiment name
- `description` (TEXT) - Experiment description
- `dataset_id` (UUID) - Foreign key to datasets
- `model_id` (UUID) - Foreign key to models
- `config` (JSONB) - Experiment configuration
- `results` (JSONB) - Experiment results
- `metrics` (JSONB) - Experiment metrics
- `status` (VARCHAR) - Experiment status
- `error_message` (TEXT) - Error details if failed
- `created_at`, `completed_at` (TIMESTAMP)

#### 6. **benchmarks**
Stores cross-dataset benchmark results.

**Columns:**
- `id` (UUID) - Primary key
- `name` (VARCHAR) - Benchmark name
- `description` (TEXT) - Benchmark description
- `dataset_ids` (JSONB) - Array of dataset IDs
- `model_ids` (JSONB) - Array of model IDs
- `metrics` (JSONB) - Metrics to compare
- `results` (JSONB) - Benchmark results
- `summary` (JSONB) - Summary statistics
- `created_at` (TIMESTAMP)

---

## 🔗 Relationships

```
datasets (1) ──→ (N) models
models (1) ──→ (1) model_metrics
models (1) ──→ (N) explanations
datasets (1) ──→ (N) explanations
datasets (1) ──→ (N) experiments
models (1) ──→ (N) experiments
```

---

## 📁 Migrations

### 001_initial_schema.sql
Creates the initial database schema with all 6 tables, indexes, and RLS policies.

**To run:**
1. Go to Supabase Dashboard → SQL Editor
2. Copy content from `migrations/001_initial_schema.sql`
3. Paste and run

---

## 🔒 Security

### Row Level Security (RLS)
All tables have RLS enabled with permissive policies for development.

**Current policies:**
- Allow all operations for all users (development mode)

**Production recommendations:**
- Add user authentication
- Restrict access based on user roles
- Add policies for read/write separation

---

## 🔍 Indexes

Performance indexes created on:
- `datasets.name`, `datasets.status`, `datasets.is_active`
- `models.dataset_id`, `models.model_type`, `models.status`
- `model_metrics.model_id`
- `explanations.model_id`, `explanations.dataset_id`, `explanations.method`
- `experiments.dataset_id`, `experiments.model_id`

---

## 📊 Data Flow

```
1. Dataset Registration
   → Insert into `datasets` table
   → Status: pending → downloading → processing → completed

2. Model Training
   → Insert into `models` table
   → Link to `dataset_id`
   → Insert metrics into `model_metrics`
   → Status: pending → training → completed

3. Explanation Generation
   → Insert into `explanations` table
   → Link to `model_id` and `dataset_id`
   → Store aggregated summaries (not raw data)

4. Benchmarking
   → Query multiple datasets/models
   → Insert results into `benchmarks` table
```

---

## 🛠️ Maintenance

### Backup
Supabase provides automatic daily backups.

### Monitoring
- Check table sizes: `SELECT pg_size_pretty(pg_total_relation_size('table_name'));`
- Check row counts: `SELECT COUNT(*) FROM table_name;`

### Cleanup
```sql
-- Remove old experiments (older than 30 days)
DELETE FROM experiments WHERE created_at < NOW() - INTERVAL '30 days';

-- Remove failed datasets
DELETE FROM datasets WHERE status = 'failed' AND created_at < NOW() - INTERVAL '7 days';
```

---

## 📚 Query Examples

### Get all models for a dataset
```sql
SELECT m.*, mm.*
FROM models m
LEFT JOIN model_metrics mm ON m.id = mm.model_id
WHERE m.dataset_id = 'your-dataset-id'
ORDER BY mm.auc_roc DESC;
```

### Get explanations for a model
```sql
SELECT *
FROM explanations
WHERE model_id = 'your-model-id'
ORDER BY created_at DESC;
```

### Cross-dataset comparison
```sql
SELECT 
    d.name as dataset_name,
    m.model_type,
    mm.auc_roc,
    mm.f1_score
FROM models m
JOIN datasets d ON m.dataset_id = d.id
JOIN model_metrics mm ON m.id = mm.model_id
WHERE d.is_active = true
ORDER BY d.name, mm.auc_roc DESC;
```

---

## 🔗 Connection Info

**Project:** jmqthnzmpfhczqzgbqkj  
**URL:** https://jmqthnzmpfhczqzgbqkj.supabase.co  
**Region:** [Your selected region]

**Environment Variables:**
```bash
SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
SUPABASE_ANON_KEY=[your-anon-key]
SUPABASE_SERVICE_KEY=[your-service-key]
```

---

## 📖 References

- [Supabase Documentation](https://supabase.com/docs)
- [PostgreSQL JSON Functions](https://www.postgresql.org/docs/current/functions-json.html)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)
