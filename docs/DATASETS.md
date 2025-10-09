# Dataset Documentation

**Dataset:** IEEE-CIS Fraud Detection  
**Source:** Kaggle Competition  
**Status:** Ready to download via Kaggle API

---

## 📊 Dataset Overview

### IEEE-CIS Fraud Detection Dataset

**Description:** Anonymized credit card transaction data with fraud labels

**Files:**
- `train_transaction.csv` - Transaction data (~590k rows, ~400 columns)
- `train_identity.csv` - Identity information (~144k rows, ~40 columns)

**Size:**
- Original: ~500MB
- After sampling: ~50MB (500k rows)

**Target Variable:** `isFraud` (binary: 0 = legitimate, 1 = fraud)

**Class Distribution:**
- Legitimate transactions: ~96.5%
- Fraudulent transactions: ~3.5%

---

## 🔄 Data Processing Pipeline

### 1. Download from Kaggle
```python
# Automatic download via API
POST /api/v1/datasets/download-ieee-cis
Authorization: Bearer {token}
```

**What happens:**
- Downloads `train_transaction.csv` and `train_identity.csv`
- Extracts files to `data/raw/`
- Verifies file integrity
- Creates dataset entry in database

### 2. Merge Datasets
```python
# Merges transaction and identity data on TransactionID
df = df_transaction.merge(df_identity, on='TransactionID', how='left')
```

**Result:** Single DataFrame with ~434 columns

### 3. Feature Engineering

#### Ratio Features
- `amt_to_card_mean_ratio` - Transaction amount / card mean amount
- `amt_log` - Log-transformed transaction amount
- `amt_decimal` - Decimal part of transaction amount

#### Time Features
- `transaction_hour` - Hour of day (0-23)
- `transaction_day` - Day number
- `transaction_weekday` - Day of week (0-6)
- `hour_sin`, `hour_cos` - Cyclical encoding of hour

#### Frequency Encoding
- Card frequency (`card1_freq`, `card2_freq`, etc.)
- Device frequency (`id_30_freq`, `DeviceType_freq`, etc.)
- Browser frequency (`id_31_freq`)

### 4. Data Cleaning

#### Missing Values
- **Numerical:** Fill with median
- **Categorical:** Fill with mode or 'missing'

#### Privacy Protection
- Remove IP-like columns (any column with 'ip' in name)
- Keep Kaggle anonymized IDs (TransactionID, etc.)

### 5. Encoding
- **Categorical features:** LabelEncoder
- **Numerical features:** StandardScaler

### 6. Balanced Sampling
- **Trigger:** Dataset >200MB
- **Strategy:** Equal samples from fraud and non-fraud classes
- **Target:** ~500k rows (5-10% of original)
- **Result:** Balanced class distribution (~50/50)

### 7. Train/Validation/Test Split
- **Training:** 70% (~350k rows)
- **Validation:** 15% (~75k rows)
- **Test:** 15% (~75k rows)
- **Stratification:** Maintains class distribution

---

## 📁 File Structure

```
data/
├── raw/
│   ├── train_transaction.csv      # Original transaction data
│   └── train_identity.csv          # Original identity data
├── processed/
│   └── {dataset_id}/
│       ├── train.csv               # Training set (70%)
│       ├── validation.csv          # Validation set (15%)
│       └── test.csv                # Test set (15%)
└── models/
    └── {model_id}/
        ├── model.pkl               # Trained model
        └── metadata.json           # Model metadata
```

---

## 🔍 Feature Categories

### Transaction Features
- `TransactionDT` - Time delta from reference point
- `TransactionAmt` - Transaction amount
- `ProductCD` - Product code
- `card1-6` - Card information (anonymized)
- `addr1-2` - Address information (anonymized)
- `dist1-2` - Distance information

### Identity Features
- `id_01-38` - Identity information (anonymized)
- `DeviceType` - Device type (mobile/desktop)
- `DeviceInfo` - Device information

### Engineered Features
- Ratio features (amount-based)
- Time features (hour, day, cyclical)
- Frequency features (card, device, browser)

### Target
- `isFraud` - Fraud label (0/1)

---

## 📈 Dataset Statistics

### After Preprocessing

**Size:**
- Total rows: ~500,000
- Total columns: ~150 (after feature engineering and cleaning)
- Memory usage: ~45 MB

**Class Distribution:**
- Non-fraud: ~250,000 (50%)
- Fraud: ~250,000 (50%)

**Data Quality:**
- Missing values: Handled (imputed)
- Duplicates: Removed
- Outliers: Retained (important for fraud detection)

**Feature Distribution:**
- Numerical features: ~120
- Categorical features: ~30 (after encoding, all numerical)

---

## 🔐 Privacy & Compliance

### Anonymization
- Dataset is already anonymized by Kaggle
- No real customer information
- All IDs are synthetic

### Privacy Measures
- Remove IP-like hash columns
- Keep transaction IDs for reproducibility
- No reverse-mapping possible

### GDPR Compliance
- Synthetic data, no personal information
- No additional anonymization needed
- Safe for research use

---

## 🎯 Usage in Research

### Model Training
- Use `train.csv` for model training
- Use `validation.csv` for hyperparameter tuning
- Use `test.csv` for final evaluation

### XAI Explanations
- Generate global explanations on full training set
- Generate local explanations on test set samples
- Use validation set for explanation quality metrics

### Human Study
- Select 20 diverse transactions from test set
- Show to participants with/without explanations
- Collect decisions and trust ratings

---

## 📊 Dataset Card

**Name:** IEEE-CIS Fraud Detection (Processed)

**Description:** Anonymized credit card transaction data with fraud labels, preprocessed for XAI benchmarking.

**Source:** Kaggle Competition (IEEE Computational Intelligence Society)

**License:** Competition License (research use)

**Size:** ~500,000 rows × ~150 columns (~45 MB)

**Target:** Binary fraud classification (isFraud)

**Class Balance:** 50/50 (after balanced sampling)

**Features:**
- Transaction amount and metadata
- Card information (anonymized)
- Device and browser information
- Engineered time and ratio features
- Frequency-encoded categorical features

**Preprocessing:**
- Merged transaction and identity data
- Feature engineering (ratios, time, frequency)
- Missing value imputation
- Categorical encoding
- Feature scaling
- Balanced sampling
- Train/val/test split (70/15/15)

**Quality Metrics:**
- Missing values: 0% (after imputation)
- Duplicates: 0%
- Class imbalance: Balanced (50/50)
- Feature correlation: Analyzed

**Intended Use:**
- XAI method benchmarking
- Model performance comparison
- Human interpretability studies
- Regulatory compliance research

**Limitations:**
- Synthetic/anonymized data
- May not represent all fraud patterns
- Temporal aspects limited
- Geographic information removed

**Citation:**
```
IEEE-CIS Fraud Detection Dataset
Kaggle Competition, 2019
https://www.kaggle.com/c/ieee-fraud-detection
```

---

## 🔧 API Usage Examples

### Download Dataset
```bash
curl -X POST http://localhost:8000/api/v1/datasets/download-ieee-cis \
  -H "Authorization: Bearer {token}"
```

### Check Download Status
```bash
curl http://localhost:8000/api/v1/tasks/{task_id}
```

### Trigger Preprocessing
```bash
curl -X POST http://localhost:8000/api/v1/datasets/{dataset_id}/preprocess \
  -H "Authorization: Bearer {token}"
```

### Get Dataset Statistics
```bash
curl http://localhost:8000/api/v1/datasets/{dataset_id}/statistics \
  -H "Authorization: Bearer {token}"
```

---

## 📚 References

1. **Kaggle Competition:** https://www.kaggle.com/c/ieee-fraud-detection
2. **Dataset Discussion:** https://www.kaggle.com/c/ieee-fraud-detection/discussion
3. **Feature Documentation:** Available in Kaggle competition data tab

---

**Status:** Dataset processing pipeline fully implemented and ready to use.
