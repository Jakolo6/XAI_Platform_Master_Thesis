# Data Directory Structure

This directory contains all datasets, processed data, trained models, and generated explanations for the XAI Finance Benchmark Platform.

## Directory Structure

```
data/
├── raw/                    # Raw datasets
│   ├── ieee_fraud_cleaned.csv
│   └── uploaded/           # User-uploaded datasets
├── processed/              # Processed and cleaned datasets
│   ├── train/
│   ├── validation/
│   └── test/
├── models/                 # Trained ML models
│   ├── logistic_regression/
│   ├── random_forest/
│   ├── xgboost/
│   ├── lightgbm/
│   ├── catboost/
│   └── mlp/
├── explanations/           # Generated explanations
│   ├── shap/
│   ├── lime/
│   ├── dice/
│   └── cache/              # Cached explanations
└── reports/                # Generated reports
    ├── audit_reports/
    ├── study_results/
    └── benchmarks/
```

## Data Sources

### IEEE-CIS Fraud Detection Dataset
- **Source**: Kaggle Competition
- **Files**: `train_transaction.csv`, `train_identity.csv`
- **Size**: ~500MB (original), ~50MB (sampled)
- **License**: Competition License
- **Description**: Anonymized credit card transactions with fraud labels

## Data Processing Pipeline

1. **Raw Data Ingestion**
   - Download from Kaggle API
   - Validate file integrity
   - Store in `raw/` directory

2. **Data Preprocessing**
   - Merge transaction and identity data
   - Handle missing values
   - Feature engineering (ratios, time features, frequency encoding)
   - Balanced sampling (5-10% of original data)
   - Store in `processed/` directory

3. **Train/Validation/Test Split**
   - 70% training
   - 15% validation
   - 15% test
   - Stratified by fraud label

## Model Storage

Models are stored in subdirectories by algorithm type:
- **Format**: Pickle/Joblib for sklearn models, native formats for others
- **Metadata**: JSON files with hyperparameters, metrics, and training info
- **Versioning**: SHA256 hash for model versioning

## Explanation Storage

Explanations are stored by method and cached for reuse:
- **Global explanations**: Feature importance, summary plots
- **Local explanations**: Instance-level attributions
- **Counterfactuals**: Alternative scenarios
- **Cache**: Keyed by (model_id, method, data_subset)

## Data Retention Policy

- **Raw data**: Permanent (within project scope)
- **Processed data**: 6 months
- **Models**: 1 year
- **Explanations**: 6 months (cached), 1 year (baseline)
- **Study data**: 6 months, then anonymized

## Security & Privacy

- All data is anonymized (Kaggle dataset is synthetic)
- No personal identifiers stored
- IP-like hashes removed from reports
- GDPR-compliant data handling

## File Naming Conventions

### Datasets
- `{source}_{version}_{sample_size}.csv`
- Example: `ieee_fraud_v1_500k.csv`

### Models
- `{algorithm}_{dataset_id}_{timestamp}_{hash}.pkl`
- Example: `xgboost_abc123_20240108_def456.pkl`

### Explanations
- `{method}_{model_id}_{type}_{timestamp}.json`
- Example: `shap_tree_abc123_global_20240108.json`

## Usage Guidelines

1. **Always use the data processing pipeline** - don't modify raw data directly
2. **Check for existing explanations** before generating new ones
3. **Use appropriate sampling** for large datasets (>200MB)
4. **Document any custom preprocessing** in the dataset metadata
5. **Clean up temporary files** after processing

## Backup Strategy

- **Nightly backups** to Supabase storage
- **Weekly exports** to S3 for long-term retention
- **Model checkpoints** saved during training
- **Explanation cache** backed up weekly
