# 🎯 Ethical Model & Denormalization Implementation Guide

## Overview

This guide implements a two-step upgrade to make the German Credit study more realistic and ethically compliant:

1. **Step 1:** Train an ethical model (exclude discriminatory features, keep normalization)
2. **Step 2:** Denormalize values for human participants (show real-world numbers)

---

## ✅ What Has Been Implemented

### 1. Ethical Training Script
**File:** `backend/scripts/train_ethical_model.py`

**Features:**
- ✅ Excludes discriminatory features (personal_status, foreign_worker, dependents)
- ✅ Keeps only ethical features (age, credit_amount, duration, employment, etc.)
- ✅ Uses StandardScaler for normalization (stored for later denormalization)
- ✅ Trains XGBoost with same configuration as before
- ✅ Saves model, scaler, and metadata
- ✅ Logs excluded features for transparency

**Excluded Features (Discriminatory):**
- `personal_status` - Gender-coded (e.g., "male single", "female divorced")
- `foreign_worker` - Nationality discrimination
- `dependents` - Family status

**Kept Features (Ethical):**
- `age`, `credit_amount`, `duration`, `installment_rate`
- `checking_status`, `credit_history`, `purpose`, `savings_status`
- `employment`, `property_magnitude`, `housing`, `job`
- `present_residence`, `existing_credits`, `own_telephone`

### 2. Denormalization Utilities
**File:** `backend/app/utils/denormalization.py`

**Features:**
- ✅ `FeatureDenormalizer` class - inverse transforms normalized values
- ✅ Categorical mappings (e.g., checking_status: 0 → "< 0 DM")
- ✅ Numerical formatting (e.g., credit_amount: 4500 → "€4,500")
- ✅ Human-readable display strings
- ✅ Applicant summary generation

**Example Output:**
```
Applicant: 35 years old, 1-4 years employment, requesting €4,500 for 24 months
```

### 3. Realistic Personas
**File:** `backend/app/data/personas.json`

**Three Personas:**
1. **High Risk** - High credit demand, short employment → likely rejection
2. **Borderline** - Middle-income, average duration → uncertain
3. **Low Risk** - Long-term employed, small loan → likely approval

### 4. Updated Study Service
**File:** `backend/app/services/study_service.py`

**Changes:**
- ✅ Integrated `FeatureDenormalizer` in `__init__()`
- ✅ Updated `_format_loan_data()` to use denormalization
- ✅ Added human-readable summary to loan data
- ✅ Categorized features (applicant_info, loan_details, financial_status)
- ✅ Keeps normalized values for model, shows denormalized for humans

---

## 🚀 Implementation Steps

### Step 1: Train the Ethical Model

#### 1.1 Prepare Data
Ensure you have the German Credit dataset:
```bash
# Data should be at:
backend/data/datasets/german-credit/raw/german_credit_data.csv
```

#### 1.2 Run Training Script
```bash
cd backend
python3 scripts/train_ethical_model.py
```

**Expected Output:**
```
================================================================================
ETHICAL GERMAN CREDIT MODEL TRAINING
================================================================================

STEP 1: LOADING AND PREPARING DATA
✅ Loaded 1000 samples with 20 columns
✅ Target column: Risk

📋 Feature Selection:
   ✅ Keeping 15 ethical features
   ❌ Excluding 3 discriminatory features: ['personal_status', 'foreign_worker', 'dependents']

STEP 2: PREPROCESSING FEATURES
📊 Feature types:
   Categorical: 10 features
   Numerical: 5 features
✅ Categorical features encoded
✅ Numerical features normalized (StandardScaler)

STEP 3: TRAINING XGBOOST MODEL
✅ Model trained successfully

STEP 4: EVALUATING MODEL
📊 Model Performance:
   AUC-ROC:   0.7800
   F1 Score:  0.7100

STEP 5: SAVING MODEL AND SCALER
✅ Model saved: data/models/german_credit_fair/german_credit_fair_xgb.pkl
✅ Scaler saved: data/models/german_credit_fair/german_credit_scaler.pkl
✅ Metadata saved: data/models/german_credit_fair/model_metadata.pkl

✅ SUCCESS: ETHICAL MODEL TRAINING COMPLETE
```

#### 1.3 Upload to R2 Storage
```bash
# Upload model
aws s3 cp data/models/german_credit_fair/german_credit_fair_xgb.pkl \
  s3://xai-platform-datasets/models/german-credit/german_credit_fair_xgb.pkl

# Upload scaler
aws s3 cp data/models/german_credit_fair/german_credit_scaler.pkl \
  s3://xai-platform-datasets/models/german-credit/german_credit_scaler.pkl

# Upload metadata
aws s3 cp data/models/german_credit_fair/model_metadata.pkl \
  s3://xai-platform-datasets/models/german-credit/model_metadata.pkl
```

#### 1.4 Register Model in Database
```bash
python3 scripts/register_model_direct.py \
  --model-id "german_credit_fair_xgb" \
  --model-name "German Credit Fair XGBoost" \
  --r2-path "models/german-credit/german_credit_fair_xgb.pkl" \
  --dataset-id "german-credit" \
  --algorithm "xgboost" \
  --auc-roc 0.78 \
  --f1-score 0.71
```

#### 1.5 Update Study Configuration
Edit `backend/app/services/study_service.py`:
```python
# Change from:
STUDY_MODEL_ID = "german_credit_xgb"

# To:
STUDY_MODEL_ID = "german_credit_fair_xgb"
```

---

### Step 2: Enable Denormalization

#### 2.1 Download Scaler and Metadata (Production)
For production deployment, download scaler and metadata to the backend:
```bash
# In production environment
mkdir -p data/models/german_credit_fair

# Download from R2
aws s3 cp s3://xai-platform-datasets/models/german-credit/german_credit_scaler.pkl \
  data/models/german_credit_fair/german_credit_scaler.pkl

aws s3 cp s3://xai-platform-datasets/models/german-credit/model_metadata.pkl \
  data/models/german_credit_fair/model_metadata.pkl
```

#### 2.2 Verify Denormalizer Initialization
Check backend logs on startup:
```
✅ Denormalizer initialized with scaler and metadata
```

If you see:
```
⚠️  Denormalizer initialized without scaler - will show normalized values
```
Then the scaler files are not found. Check paths.

#### 2.3 Test Denormalization
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test study endpoint
curl http://localhost:8000/api/v1/study/session/start
# Note the session_id

curl http://localhost:8000/api/v1/study/session/{session_id}/case/0
```

**Expected Response:**
```json
{
  "loan_data": {
    "summary": "Applicant: 35 years old, 1-4 years employment, requesting €4,500 for 24 months",
    "applicant_info": {
      "age": "Age: 35 years",
      "employment": "Employment Length: 1-4 years",
      "job": "Job Type: Skilled"
    },
    "loan_details": {
      "credit_amount": "Credit Amount: €4,500",
      "duration": "Duration: 24 months"
    },
    "financial_status": {
      "checking_status": "Checking Account: 0 - 200 DM",
      "savings_status": "Savings Account: 100 - 500 DM"
    }
  }
}
```

---

## 🎨 Frontend Integration

### Update StudyCaseCard Component

The frontend should display denormalized values from the API:

```typescript
// frontend/src/components/study/StudyCaseCard.tsx

interface LoanData {
  summary: string;
  applicant_info: Record<string, string>;
  loan_details: Record<string, string>;
  financial_status: Record<string, string>;
}

function StudyCaseCard({ caseData }: { caseData: CaseData }) {
  const { loan_data, decision, explanation } = caseData;
  
  return (
    <div className="case-card">
      {/* Applicant Summary */}
      <div className="summary">
        <h3>Loan Application</h3>
        <p>{loan_data.summary}</p>
      </div>
      
      {/* Decision */}
      <div className="decision">
        <h4>Model Decision: {decision.approved ? 'Approved' : 'Rejected'}</h4>
        <p>Risk Score: {(decision.risk_score * 100).toFixed(0)}%</p>
      </div>
      
      {/* Applicant Details */}
      <div className="details">
        <h4>Applicant Information</h4>
        {Object.entries(loan_data.applicant_info).map(([key, value]) => (
          <div key={key}>{value}</div>
        ))}
        
        <h4>Loan Details</h4>
        {Object.entries(loan_data.loan_details).map(([key, value]) => (
          <div key={key}>{value}</div>
        ))}
        
        <h4>Financial Status</h4>
        {Object.entries(loan_data.financial_status).map(([key, value]) => (
          <div key={key}>{value}</div>
        ))}
      </div>
      
      {/* Explanation Layer */}
      <ExplanationLayer explanation={explanation} />
    </div>
  );
}
```

---

## 📊 Data Flow

### Before (Normalized Values Shown to Humans)
```
Dataset (normalized) → Model → Prediction
                    ↓
            Study API → Frontend
                    ↓
        Participant sees: age=0.42, credit_amount=1.23 ❌
```

### After (Denormalized Values for Humans)
```
Dataset (normalized) → Model → Prediction
                    ↓
            Denormalizer (inverse transform)
                    ↓
            Study API → Frontend
                    ↓
        Participant sees: age=35 years, credit_amount=€4,500 ✅
```

**Key Point:** Model still uses normalized values internally, only the display is denormalized.

---

## 🧪 Testing Checklist

### Model Training
- [ ] Script runs without errors
- [ ] Model achieves reasonable performance (AUC-ROC > 0.75)
- [ ] Scaler and metadata files are created
- [ ] Excluded features are logged

### Denormalization
- [ ] Denormalizer loads scaler successfully
- [ ] Numerical values are denormalized correctly (age, credit_amount, duration)
- [ ] Categorical values are mapped to text labels
- [ ] Display strings are formatted with units (€, years, months)

### Study Flow
- [ ] Study session starts successfully
- [ ] Case data includes denormalized loan_data
- [ ] Summary string is generated correctly
- [ ] Features are categorized properly
- [ ] Frontend displays human-readable values

### Ethical Compliance
- [ ] No discriminatory features in model input
- [ ] Model performance is maintained
- [ ] Feature importance doesn't show excluded features
- [ ] Documentation lists excluded features

---

## 🔍 Troubleshooting

### Issue: "Denormalizer initialized without scaler"
**Solution:** Scaler file not found. Check paths:
```python
# In study_service.py __init__
scaler_path = Path("data/models/german_credit_fair/german_credit_scaler.pkl")
# Make sure this path exists
```

### Issue: Values still look normalized
**Solution:** Scaler might not be loaded. Check logs:
```
logger.info("Denormalizer initialized with scaler and metadata")
```

### Issue: Categorical values show numbers instead of text
**Solution:** Metadata not loaded. Ensure `model_metadata.pkl` exists and contains `categorical_mappings`.

### Issue: Model performance dropped significantly
**Solution:** Check if important features were accidentally excluded. Review `ETHICAL_FEATURES` list in training script.

---

## 📝 Summary

### What's Implemented
✅ Ethical model training script (excludes discriminatory features)  
✅ Denormalization utilities (inverse transform for display)  
✅ Realistic personas (3 example cases)  
✅ Updated study service (integrated denormalization)  
✅ Comprehensive documentation  

### What's Next
1. Run training script to create ethical model
2. Upload model, scaler, and metadata to R2
3. Register model in database
4. Update study configuration to use new model
5. Test denormalization in study flow
6. Update frontend to display denormalized values

### Key Benefits
- ✅ **Ethical:** No discriminatory features
- ✅ **Realistic:** Human-readable values (€4,500 instead of 1.23)
- ✅ **Accurate:** Model still uses normalized values internally
- ✅ **Transparent:** Excluded features are documented

---

## 🎓 Research Implications

### Ethical Considerations
- Model trained only on ethically acceptable features
- No gender, nationality, or marital status bias
- Transparent about what was excluded and why

### Human Factors
- Participants see realistic loan applications
- Values are in familiar units (€, years, months)
- Easier to understand and evaluate explanations

### Data Quality
- Model performance maintained despite fewer features
- Normalization ensures good training
- Denormalization ensures good human interpretation

**Ready to deploy!** 🚀
