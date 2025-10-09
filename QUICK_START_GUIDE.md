# 🚀 Quick Start Guide - XAI Finance Platform

**Status:** ✅ System is Running and Ready!  
**Date:** 2025-10-08

---

## ✅ Current Status

All services are **running and healthy**:
- ✅ PostgreSQL Database
- ✅ Redis Cache
- ✅ FastAPI Backend (http://localhost:8000)
- ✅ Celery Worker
- ✅ Celery Beat Scheduler
- ✅ Flower Monitoring (http://localhost:5555)

---

## 🎯 What You Can Do Now

### 1. View API Documentation
```bash
open http://localhost:8000/api/v1/docs
```

### 2. Monitor Celery Tasks
```bash
open http://localhost:5555
```

### 3. Test the System

#### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "researcher@test.com",
    "password": "testpass123",
    "full_name": "Test Researcher"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "researcher@test.com",
    "password": "testpass123"
  }'
```

**Save the `access_token` from the response!**

---

## 📊 Train Your First Model

### Step 1: Download IEEE-CIS Dataset

First, make sure you have Kaggle credentials configured at `~/.kaggle/kaggle.json`.

```bash
# Download dataset
curl -X POST http://localhost:8000/api/v1/datasets/download-ieee-cis \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

This will return a `dataset_id` and `task_id`. Save the `dataset_id`.

### Step 2: Wait for Download to Complete

Check the task status in Flower: http://localhost:5555

Or check dataset status:
```bash
curl http://localhost:8000/api/v1/datasets/DATASET_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 3: Preprocess the Dataset

```bash
curl -X POST http://localhost:8000/api/v1/datasets/DATASET_ID/preprocess \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

Wait for preprocessing to complete (check in Flower or dataset status).

### Step 4: Train a Model

Train an XGBoost model:
```bash
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "XGBoost Fraud Detector v1",
    "model_type": "xgboost",
    "dataset_id": "YOUR_DATASET_ID",
    "optimize": false
  }'
```

This returns a `model_id` and `task_id`.

### Step 5: Monitor Training

Watch progress in Flower: http://localhost:5555

Or check model status:
```bash
curl http://localhost:8000/api/v1/models/MODEL_ID \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Step 6: View Results

Get model metrics:
```bash
curl http://localhost:8000/api/v1/models/MODEL_ID/metrics \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

View leaderboard:
```bash
curl http://localhost:8000/api/v1/models/leaderboard/performance \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 🤖 Available Models

Train any of these 6 models:

1. **`logistic_regression`** - Linear baseline
2. **`random_forest`** - Ensemble method
3. **`xgboost`** - Gradient boosting (recommended to start)
4. **`lightgbm`** - Fast gradient boosting
5. **`catboost`** - Categorical boosting
6. **`mlp`** - Neural network

Example training request for each:
```json
{
  "name": "Model Name",
  "model_type": "xgboost",  // or any model above
  "dataset_id": "YOUR_DATASET_ID",
  "optimize": false,  // set true for hyperparameter optimization
  "hyperparameters": {}  // optional custom parameters
}
```

---

## 📈 Metrics Calculated

For each trained model, you'll get:

**Classification Metrics:**
- AUC-ROC
- AUC-PR (Precision-Recall)
- F1 Score
- Precision
- Recall
- Accuracy
- Log Loss
- Brier Score

**Calibration Metrics:**
- Expected Calibration Error (ECE)
- Maximum Calibration Error (MCE)

**Additional:**
- Confusion Matrix
- Training Time
- Model Hash (SHA256)

---

## 🔧 Useful Commands

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# Backend logs
docker-compose logs -f backend

# Celery worker logs
docker-compose logs -f celery_worker

# All logs
docker-compose logs -f
```

### Restart Services
```bash
docker-compose restart
```

### Stop Services
```bash
docker-compose down
```

### Start Services Again
```bash
docker-compose up -d
```

### Rebuild After Code Changes
```bash
docker-compose down
docker-compose up -d --build
```

---

## 📁 Data Directories

Your data is stored in:
- `data/raw/` - Downloaded datasets
- `data/processed/DATASET_ID/` - Preprocessed train/val/test splits
- `data/models/MODEL_ID/` - Trained model files

---

## 🎓 Training Time Estimates

Approximate training times (without optimization):
- Logistic Regression: 1-2 minutes
- Random Forest: 3-7 minutes
- XGBoost: 2-5 minutes ⭐ (recommended to start)
- LightGBM: 2-4 minutes
- CatBoost: 3-6 minutes
- MLP: 5-10 minutes

With hyperparameter optimization (`optimize: true`):
- Add 10-30 minutes per model

---

## 🐛 Troubleshooting

### Backend Not Responding
```bash
docker-compose logs backend
docker-compose restart backend
```

### Celery Tasks Not Running
```bash
docker-compose logs celery_worker
docker-compose restart celery_worker
```

### Database Connection Issues
```bash
docker-compose logs postgres
docker-compose restart postgres
```

### Redis Connection Issues
```bash
docker-compose logs redis
docker-compose restart redis
```

### Complete Reset
```bash
docker-compose down -v  # WARNING: Deletes all data!
docker-compose up -d --build
```

---

## 📚 Documentation

- **API Docs (Swagger):** http://localhost:8000/api/v1/docs
- **API Docs (ReDoc):** http://localhost:8000/api/v1/redoc
- **Celery Monitor:** http://localhost:5555
- **Implementation Summary:** `IMPLEMENTATION_SUMMARY.md`
- **Project Status:** `PROJECT_STATUS.md`

---

## 🎯 Next Steps

1. ✅ **System is running** - You're ready to go!
2. 📥 **Download dataset** - Use the IEEE-CIS download endpoint
3. 🔄 **Preprocess data** - Trigger preprocessing task
4. 🤖 **Train models** - Start with XGBoost
5. 📊 **Compare results** - Use the leaderboard endpoint
6. 🔬 **Implement XAI** - Phase 3 (SHAP, LIME explanations)
7. 👥 **Human study** - Phase 4 (Study interface)

---

## ⚠️ Important Notes

1. **Kaggle Credentials:** Already configured at `~/.kaggle/kaggle.json`
2. **Supabase:** Optional - models saved locally by default
3. **Dataset Size:** IEEE-CIS is ~500k rows after preprocessing
4. **Training:** All training happens asynchronously via Celery
5. **Monitoring:** Always check Flower (http://localhost:5555) for task status

---

**🎉 Your XAI Finance Platform is ready for model training!**

Start by registering a user, downloading the dataset, and training your first XGBoost model.
