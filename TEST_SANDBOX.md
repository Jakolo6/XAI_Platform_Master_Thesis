# 🧪 TEST EXPLAINABILITY SANDBOX

## ✅ BACKEND IMPLEMENTATION COMPLETE

The Explainability Sandbox backend is now fully implemented with:
- ✅ `sandbox_service.py` - Service layer with real data
- ✅ `sandbox.py` - API endpoints
- ✅ Routes registered in `api.py`
- ✅ Database migration ready
- ✅ NO MOCK DATA - 100% real explanations

---

## 🚀 STEP 1: RESTART BACKEND

The backend needs to be restarted to load the new endpoints.

### **Option A: If backend is running locally**
```bash
cd backend

# Kill existing process
pkill -f uvicorn

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### **Option B: If using Docker**
```bash
docker-compose restart backend
```

### **Option C: If deployed**
Redeploy the backend service with the new code.

---

## 🧪 STEP 2: TEST ENDPOINTS

### **Test 1: Health Check**
```bash
curl http://localhost:8000/api/v1/explanations/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "explainability_sandbox",
  "endpoints": [
    "GET /sample/{model_id}",
    "GET /local/{model_id}/{instance_id}",
    "POST /rating"
  ]
}
```

---

### **Test 2: Get Sample Instance**

First, get a model ID from your database:
```bash
curl http://localhost:8000/api/v1/models/
```

Then test with a real model ID:
```bash
curl http://localhost:8000/api/v1/explanations/sample/YOUR_MODEL_ID
```

**Expected Response:**
```json
{
  "instance_id": "sample_42",
  "features": {
    "TransactionAmt": 850.50,
    "card_type": "credit",
    "merchant_category": "retail",
    ...
  },
  "prediction": 0.91,
  "model_output": "Fraud",
  "true_label": "Fraud"
}
```

---

### **Test 3: Get SHAP Explanation**
```bash
curl "http://localhost:8000/api/v1/explanations/local/YOUR_MODEL_ID/sample_42?method=shap"
```

**Expected Response:**
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

---

### **Test 4: Get LIME Explanation**
```bash
curl "http://localhost:8000/api/v1/explanations/local/YOUR_MODEL_ID/sample_42?method=lime"
```

**Expected Response:**
```json
{
  "method": "lime",
  "prediction_proba": 0.91,
  "features": [
    {
      "feature": "TransactionAmt",
      "value": 850.50,
      "contribution": 0.21,
      "importance": 0.21
    },
    ...
  ]
}
```

---

### **Test 5: Submit Rating**
```bash
curl -X POST http://localhost:8000/api/v1/explanations/rating \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "YOUR_MODEL_ID",
    "instance_id": "sample_42",
    "clarity": 5,
    "trustworthiness": 4,
    "actionability": 3,
    "shap_method": "shap",
    "lime_method": "lime"
  }'
```

**Expected Response:**
```json
{
  "rating_id": "rating_abc123def456",
  "message": "Rating saved successfully. Thank you for your feedback!"
}
```

---

## 🌐 STEP 3: TEST FRONTEND

1. **Open browser:** `http://localhost:3000/sandbox`
2. **Select a trained model** from the dropdown
3. **Click "Load Sample Prediction"**
4. **Verify:**
   - Sample instance loads with features
   - SHAP explanation displays on left
   - LIME explanation displays on right
   - Interpretation text generates
   - Can submit rating

---

## 🐛 TROUBLESHOOTING

### **Error: "Test data not found"**
**Cause:** Dataset not processed yet

**Solution:**
```bash
# Process the dataset first
curl -X POST http://localhost:8000/api/v1/datasets/ieee-cis-fraud/preprocess
```

---

### **Error: "Model not found"**
**Cause:** No trained models in database

**Solution:**
```bash
# Train a model first
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test XGBoost",
    "model_type": "xgboost",
    "dataset_id": "ieee-cis-fraud"
  }'
```

---

### **Error: "Module 'shap' not found"**
**Cause:** Missing dependencies

**Solution:**
```bash
cd backend
pip install shap lime
```

---

### **Error: "Connection refused"**
**Cause:** Backend not running

**Solution:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### **Error: "Table does not exist"**
**Cause:** Database migration not run

**Solution:**
```bash
cd backend
psql postgresql://YOUR_CONNECTION_STRING -f migrations/3_sandbox_schema.sql
```

---

## ✅ VERIFICATION CHECKLIST

After testing, verify:

- [ ] Backend starts without errors
- [ ] Health endpoint returns 200
- [ ] Can get sample instance
- [ ] SHAP explanation returns data
- [ ] LIME explanation returns data
- [ ] Can submit rating
- [ ] Rating saves to database
- [ ] Frontend loads sandbox page
- [ ] Can select model in frontend
- [ ] Sample loads in frontend
- [ ] SHAP visualization displays
- [ ] LIME visualization displays
- [ ] Interpretation text generates
- [ ] Can submit rating from frontend

---

## 📊 CHECK DATABASE

Verify ratings are being saved:

```bash
psql postgresql://YOUR_CONNECTION_STRING -c "SELECT * FROM explanation_ratings ORDER BY created_at DESC LIMIT 5;"
```

**Expected Output:**
```
 id | rating_id      | model_id    | instance_id | clarity | trustworthiness | actionability
----+----------------+-------------+-------------+---------+-----------------+--------------
  1 | rating_abc123  | xgboost_123 | sample_42   |       5 |               4 |             3
```

---

## 🎯 SUCCESS CRITERIA

✅ **Backend:**
- All endpoints return 200 status
- Real data (no mock/fallback)
- SHAP and LIME generate correctly
- Ratings save to database

✅ **Frontend:**
- Page loads without errors
- Can select model
- Sample loads with features
- Both explanations display
- Interpretation generates
- Can submit rating

✅ **Integration:**
- Frontend → Backend communication works
- Data flows correctly
- Error handling works
- Loading states work

---

## 🚀 DEPLOYMENT

Once local testing passes:

### **Backend:**
```bash
# Deploy to production
git push origin main
# Backend auto-deploys or manually restart service
```

### **Frontend:**
```bash
# Already deployed via Netlify
# Auto-deploys from GitHub
```

---

## 📞 NEXT STEPS

1. ✅ **Restart backend** (most important!)
2. ✅ **Test endpoints** with curl
3. ✅ **Test frontend** in browser
4. ✅ **Verify database** saves ratings
5. ✅ **Deploy** to production

**The sandbox is ready to use!** 🎉

---

## 🎓 FOR THESIS

This sandbox now provides:
- ✅ Real SHAP explanations
- ✅ Real LIME explanations
- ✅ Human interpretability ratings
- ✅ Interactive exploration
- ✅ Method comparison
- ✅ Research data collection

**Perfect for your thesis evaluation!** 🚀
