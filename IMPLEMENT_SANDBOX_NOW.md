# 🚀 IMPLEMENT SANDBOX NOW - Quick Start Guide

## ✅ WHAT'S ALREADY DONE

### **Frontend (100% Complete)**
- ✅ Sandbox page created (`frontend/src/app/sandbox/page.tsx`)
- ✅ Navigation updated (Navbar shows "Sandbox")
- ✅ API methods added
- ✅ Error handling implemented
- ✅ Loading states implemented
- ✅ Beautiful UI with tooltips and visualizations

### **Backend (Files Created, Need Integration)**
- ✅ Database migration (`backend/migrations/3_sandbox_schema.sql`)
- ✅ Pydantic schemas (`backend/app/schemas/sandbox.py`)
- ✅ Database models (`backend/app/models/sandbox.py`)
- ⏳ Service layer (need to create)
- ⏳ API endpoints (need to create)
- ⏳ Route registration (need to add)

---

## 🎯 STEP-BY-STEP IMPLEMENTATION (30 Minutes)

### **STEP 1: Run Database Migration** (2 minutes)

```bash
cd backend

# Option 1: Using psql directly
psql -U postgres -d xai_platform -f migrations/3_sandbox_schema.sql

# Option 2: Using docker (if using docker)
docker exec -i postgres_container psql -U postgres -d xai_platform < migrations/3_sandbox_schema.sql

# Verify tables created
psql -U postgres -d xai_platform -c "\dt sandbox_*"
psql -U postgres -d xai_platform -c "\dt explanation_ratings"
```

**Expected Output:**
```
                  List of relations
 Schema |         Name          | Type  |  Owner   
--------+-----------------------+-------+----------
 public | sandbox_instances     | table | postgres
 public | explanation_ratings   | table | postgres
```

---

### **STEP 2: Create Sandbox Service** (10 minutes)

**File:** `backend/app/services/sandbox_service.py`

I'll create this file with the complete implementation. Copy this entire file:

```python
# See SANDBOX_COMPLETION_PLAN.md Step 1.3 for full code
# This file contains:
# - load_test_data()
# - get_sample_instance()
# - generate_shap_explanation()
# - generate_lime_explanation()
# - what_if_analysis()
```

**Action:** Copy the code from `SANDBOX_COMPLETION_PLAN.md` Step 1.3

---

### **STEP 3: Create API Endpoints** (10 minutes)

**File:** `backend/app/api/v1/endpoints/sandbox.py`

```python
# See SANDBOX_COMPLETION_PLAN.md Step 1.4 for full code
# This file contains 4 endpoints:
# - GET /sample/{model_id}
# - GET /local/{model_id}/{instance_id}
# - POST /what-if
# - POST /rating
```

**Action:** Copy the code from `SANDBOX_COMPLETION_PLAN.md` Step 1.4

---

### **STEP 4: Register Routes** (2 minutes)

**File:** `backend/app/api/v1/api.py`

Add these lines:

```python
from app.api.v1.endpoints import sandbox

# Add this line with other route registrations
api_router.include_router(
    sandbox.router, 
    prefix="/explanations", 
    tags=["sandbox"]
)
```

---

### **STEP 5: Update Base Model Imports** (1 minute)

**File:** `backend/app/db/base.py`

Add:
```python
from app.models.sandbox import SandboxInstance, ExplanationRating
```

---

### **STEP 6: Restart Backend** (1 minute)

```bash
cd backend

# Kill existing process
pkill -f uvicorn

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### **STEP 7: Test API Endpoints** (5 minutes)

```bash
# Test 1: Get sample instance
curl http://localhost:8000/api/v1/explanations/sample/YOUR_MODEL_ID

# Test 2: Get SHAP explanation
curl "http://localhost:8000/api/v1/explanations/local/YOUR_MODEL_ID/sample_0?method=shap"

# Test 3: Get LIME explanation
curl "http://localhost:8000/api/v1/explanations/local/YOUR_MODEL_ID/sample_0?method=lime"

# Test 4: Submit rating
curl -X POST http://localhost:8000/api/v1/explanations/rating \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "YOUR_MODEL_ID",
    "instance_id": "sample_0",
    "clarity": 5,
    "trustworthiness": 4,
    "actionability": 3,
    "shap_method": "shap",
    "lime_method": "lime"
  }'
```

---

### **STEP 8: Test Frontend** (5 minutes)

1. Open browser: `http://localhost:3000/sandbox`
2. Select a trained model
3. Click "Load Sample Prediction"
4. Verify SHAP and LIME explanations load
5. Submit a rating
6. Check database:
   ```sql
   SELECT * FROM explanation_ratings ORDER BY created_at DESC LIMIT 5;
   ```

---

## 🔥 QUICK COPY-PASTE IMPLEMENTATION

If you want to implement everything in one go, here are the exact files to create:

### **1. Service Layer**
Create: `backend/app/services/sandbox_service.py`
Copy from: `SANDBOX_COMPLETION_PLAN.md` - Step 1.3 (full code provided)

### **2. API Endpoints**
Create: `backend/app/api/v1/endpoints/sandbox.py`
Copy from: `SANDBOX_COMPLETION_PLAN.md` - Step 1.4 (full code provided)

### **3. Register Routes**
Edit: `backend/app/api/v1/api.py`
Add:
```python
from app.api.v1.endpoints import sandbox
api_router.include_router(sandbox.router, prefix="/explanations", tags=["sandbox"])
```

### **4. Update Base Imports**
Edit: `backend/app/db/base.py`
Add:
```python
from app.models.sandbox import SandboxInstance, ExplanationRating
```

---

## 🐛 TROUBLESHOOTING

### **Error: "Test data not found"**
**Solution:** Ensure dataset is processed:
```bash
curl -X POST http://localhost:8000/api/v1/datasets/ieee-cis-fraud/preprocess
```

### **Error: "Model not found"**
**Solution:** Train a model first:
```bash
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test XGBoost",
    "model_type": "xgboost",
    "dataset_id": "ieee-cis-fraud"
  }'
```

### **Error: "Module not found: shap/lime"**
**Solution:** Install dependencies:
```bash
cd backend
pip install shap lime
```

### **Error: "Table does not exist"**
**Solution:** Run migration again:
```bash
psql -U postgres -d xai_platform -f migrations/3_sandbox_schema.sql
```

---

## ✅ VERIFICATION CHECKLIST

After implementation, verify:

- [ ] Database tables created (`sandbox_instances`, `explanation_ratings`)
- [ ] Backend starts without errors
- [ ] API docs show sandbox endpoints: `http://localhost:8000/docs`
- [ ] GET `/explanations/sample/{model_id}` returns data
- [ ] GET `/explanations/local/{model_id}/{instance_id}` returns SHAP
- [ ] GET `/explanations/local/{model_id}/{instance_id}?method=lime` returns LIME
- [ ] POST `/explanations/rating` saves to database
- [ ] Frontend `/sandbox` page loads
- [ ] Can select model and load sample
- [ ] SHAP and LIME explanations display
- [ ] Can submit rating
- [ ] Rating appears in database

---

## 📊 EXPECTED RESULTS

### **Sample Instance Response:**
```json
{
  "instance_id": "sample_42",
  "features": {
    "TransactionAmt": 850.50,
    "card_type": "credit",
    "merchant_category": "retail"
  },
  "prediction": 0.91,
  "model_output": "Fraud",
  "true_label": "Fraud"
}
```

### **SHAP Explanation Response:**
```json
{
  "method": "shap",
  "prediction_proba": 0.91,
  "base_value": 0.15,
  "features": [
    {
      "feature": "TransactionAmt",
      "value": 850.50,
      "contribution": 0.23,
      "importance": 0.23
    },
    ...
  ]
}
```

### **Database Rating:**
```sql
SELECT * FROM explanation_ratings LIMIT 1;

 id | rating_id      | model_id    | instance_id | clarity | trustworthiness | actionability
----+----------------+-------------+-------------+---------+-----------------+--------------
  1 | rating_abc123  | xgboost_123 | sample_42   |       5 |               4 |             3
```

---

## 🎯 SUCCESS = 100% REAL DATA

After implementation:
- ✅ NO mock data anywhere
- ✅ Real SHAP explanations from trained models
- ✅ Real LIME explanations from trained models
- ✅ Real predictions from test data
- ✅ Real ratings saved to database
- ✅ Production-ready code

---

## 🚀 DEPLOYMENT

### **Backend:**
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Frontend:**
```bash
cd frontend
npm run build
# Auto-deploys to Netlify from GitHub
```

---

## 📞 NEED HELP?

Check these files for complete code:
1. `SANDBOX_COMPLETION_PLAN.md` - Full implementation guide
2. `SANDBOX_IMPLEMENTATION.md` - Original design document
3. `backend/migrations/3_sandbox_schema.sql` - Database schema
4. `backend/app/schemas/sandbox.py` - Pydantic models
5. `backend/app/models/sandbox.py` - SQLAlchemy models

**START IMPLEMENTING NOW!** 🔥

The frontend is ready and waiting. Just implement the backend and everything will work!
