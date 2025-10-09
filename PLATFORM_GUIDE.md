# 🌐 XAI Platform - User Guide

**Your platform is running at:**
- **API Docs:** http://localhost:8000/api/v1/docs
- **Task Monitor:** http://localhost:5555
- **API (ReDoc):** http://localhost:8000/api/v1/redoc

---

## 🎯 What You Can Do Now

### 1. View Your Models (API Docs)

**Open:** http://localhost:8000/api/v1/docs

**Steps:**
1. Click **"Authorize"** button (top right)
2. Get a token:
   ```bash
   curl -X POST http://localhost:8000/api/v1/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"researcher@xai.com","password":"research123"}'
   ```
3. Copy the `access_token` from response
4. Paste in the "Value" field
5. Click "Authorize"

**Now you can:**
- View all models: `/models/` endpoint
- Get leaderboard: `/models/leaderboard/performance`
- Get specific model: `/models/{model_id}`
- Get model metrics: `/models/{model_id}/metrics`

---

### 2. Monitor Tasks (Flower Dashboard)

**Open:** http://localhost:5555

**You'll see:**
- ✅ All completed training tasks
- ⏱️ Task execution times
- 📊 Success/failure rates
- 🔄 Worker status

**Your completed tasks:**
- 6 model training tasks (all succeeded!)
- 1 preprocessing task
- 1 dataset download task

---

### 3. Explore API Endpoints

#### **Authentication**
- `POST /auth/login` - Get access token
- `POST /auth/register` - Create new user
- `POST /auth/refresh` - Refresh token

#### **Datasets**
- `GET /datasets/` - List all datasets
- `GET /datasets/{id}` - Get dataset details
- `POST /datasets/download-ieee-cis` - Download dataset
- `POST /datasets/{id}/preprocess` - Preprocess dataset
- `GET /datasets/{id}/statistics` - Get statistics

#### **Models**
- `GET /models/` - List all models
- `POST /models/train` - Train new model
- `GET /models/{id}` - Get model details
- `GET /models/{id}/metrics` - Get model metrics
- `GET /models/leaderboard/performance` - Get leaderboard
- `GET /models/leaderboard/comparison` - Compare models

#### **Explanations** (XAI Features)
- `POST /explanations/generate` - Generate SHAP/LIME explanations
- `GET /explanations/{id}` - Get explanation details
- `GET /explanations/model/{model_id}` - Get all explanations for a model

---

## 📊 View Your Results

### Option 1: Using API Docs (Easiest)

1. Open http://localhost:8000/api/v1/docs
2. Authorize with your token
3. Go to **"Models"** section
4. Try **"GET /models/leaderboard/performance"**
5. Click **"Try it out"** → **"Execute"**
6. See your results in JSON format!

### Option 2: Using curl

```bash
# Get fresh token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"researcher@xai.com","password":"research123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# View leaderboard
curl http://localhost:8000/api/v1/models/leaderboard/performance \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# View specific model
curl http://localhost:8000/api/v1/models/d941370a-b058-4bcc-8b72-3dcac17d1af4 \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# Get model metrics
curl http://localhost:8000/api/v1/models/d941370a-b058-4bcc-8b72-3dcac17d1af4/metrics \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## 🎨 Visual Overview

### Your Platform Architecture:

```
┌─────────────────────────────────────────────────────┐
│                  Your Browser                        │
│  http://localhost:8000/docs  (API Documentation)   │
│  http://localhost:5555        (Task Monitoring)     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8000)            │
│  • REST API                                         │
│  • Authentication                                   │
│  • Model Management                                 │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ PostgreSQL  │  │   Redis     │  │   Celery    │
│  Database   │  │   Cache     │  │   Worker    │
│             │  │             │  │             │
│ • Users     │  │ • Tasks     │  │ • Training  │
│ • Models    │  │ • Queue     │  │ • Process   │
│ • Metrics   │  │             │  │ • Download  │
└─────────────┘  └─────────────┘  └─────────────┘
```

### Your Data Flow:

```
1. Download Dataset (Kaggle)
         ↓
2. Preprocess (270k samples)
         ↓
3. Train Models (6 algorithms)
         ↓
4. Evaluate & Save Metrics
         ↓
5. View Results (API/Dashboard)
```

---

## 🔍 Your Model IDs

Copy these to view specific models:

1. **CatBoost** (Best): `ff766719-d93a-467b-be69-c62c7de35d65`
2. **XGBoost** (Fastest): `d941370a-b058-4bcc-8b72-3dcac17d1af4`
3. **Random Forest**: `ac2dc1dc-b849-4d50-bc62-fc0bc35cac80`
4. **LightGBM**: `99a100b1-aa08-4b47-aac2-5dc562cb9b4c`
5. **MLP**: `b3b5d1a1-4b3e-4296-a278-186b84e408ff`
6. **Logistic Regression**: `1d6dc77d-3117-4cc3-8326-fa50f3bd502a`

**Dataset ID:** `caa2b9e5-9fc5-49de-aa1f-2a7b2d66645a`

---

## 📈 Export Results for Thesis

### Export Leaderboard to JSON:
```bash
curl http://localhost:8000/api/v1/models/leaderboard/performance \
  -H "Authorization: Bearer $TOKEN" > leaderboard.json
```

### Export Specific Model Metrics:
```bash
curl http://localhost:8000/api/v1/models/ff766719-d93a-467b-be69-c62c7de35d65/metrics \
  -H "Authorization: Bearer $TOKEN" > catboost_metrics.json
```

### Convert to CSV (for Excel):
```bash
# Install jq if needed: brew install jq
curl http://localhost:8000/api/v1/models/leaderboard/performance \
  -H "Authorization: Bearer $TOKEN" | \
  jq -r '["Rank","Model","Type","AUC-ROC","F1","Accuracy","Time"], 
         (.[] | [.rank, .model_name, .model_type, .auc_roc, .f1_score, .accuracy, .training_time_seconds]) | 
         @csv' > results.csv
```

---

## 🎯 Next Steps

### 1. Generate Explanations (XAI)

Train a model and generate SHAP explanations:

```bash
# Generate explanation for a prediction
curl -X POST http://localhost:8000/api/v1/explanations/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "d941370a-b058-4bcc-8b72-3dcac17d1af4",
    "transaction_data": {...},
    "explanation_type": "shap"
  }'
```

### 2. Compare Models

```bash
curl http://localhost:8000/api/v1/models/leaderboard/comparison \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Retrain with Optimization

```bash
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "XGBoost Optimized",
    "model_type": "xgboost",
    "dataset_id": "caa2b9e5-9fc5-49de-aa1f-2a7b2d66645a",
    "optimize": true
  }'
```

This will run hyperparameter optimization (takes longer but better results).

---

## 🛠️ Manage Your Platform

### Check Status:
```bash
docker-compose ps
```

### View Logs:
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f celery_worker
docker-compose logs -f backend
```

### Restart Services:
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart celery_worker
```

### Stop Platform:
```bash
docker-compose down
```

### Start Platform:
```bash
docker-compose up -d
```

---

## 📱 Access from Other Devices (Optional)

To access from another computer on your network:

1. Find your laptop's IP:
   ```bash
   ipconfig getifaddr en0
   ```

2. Access from other device:
   ```
   http://YOUR_IP:8000/api/v1/docs
   http://YOUR_IP:5555
   ```

---

## 💡 Tips

### Quick Access Script:
Create a file `open_platform.sh`:
```bash
#!/bin/bash
open http://localhost:8000/api/v1/docs
open http://localhost:5555
echo "Platform opened in browser!"
```

Make it executable:
```bash
chmod +x open_platform.sh
./open_platform.sh
```

### Get Token Quickly:
Add to your `.bashrc` or `.zshrc`:
```bash
alias xai-token='curl -s -X POST http://localhost:8000/api/v1/auth/login -H "Content-Type: application/json" -d "{\"email\":\"researcher@xai.com\",\"password\":\"research123\"}" | python3 -c "import sys, json; print(json.load(sys.stdin)[\"access_token\"])"'
```

Then just run: `xai-token`

---

## 🎓 For Your Thesis

### Screenshots to Include:
1. API documentation page (http://localhost:8000/api/v1/docs)
2. Flower dashboard showing completed tasks
3. Leaderboard JSON output
4. Model metrics comparison

### Data to Export:
1. Leaderboard (all models ranked)
2. Individual model metrics
3. Confusion matrices
4. Training times
5. Dataset statistics

---

## 🆘 Troubleshooting

### Can't access localhost:8000?
```bash
# Check if backend is running
docker-compose ps backend

# Restart backend
docker-compose restart backend
```

### Can't access localhost:5555?
```bash
# Check if flower is running
docker-compose ps flower

# Restart flower
docker-compose restart flower
```

### Need to reset everything?
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d     # Start fresh
```

---

**Your platform is fully operational! Open the links above to explore your results.** 🚀
