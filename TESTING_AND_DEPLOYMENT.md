# 🚀 TESTING & DEPLOYMENT GUIDE

**Status:** Frontend-Backend Connection Complete!  
**Date:** October 10, 2025

---

## ✅ WHAT WE JUST CONNECTED

All frontend components now make real API calls to the backend:

1. ✅ **DatasetSelector** - Fetches real datasets from Supabase
2. ✅ **Datasets Page** - Can trigger real dataset processing
3. ✅ **Training Page** - Submits real training jobs
4. ✅ **Benchmarks Page** - Shows real cross-dataset comparisons

---

## 🧪 TESTING GUIDE

### Prerequisites
- ✅ Backend running on `localhost:8000`
- ✅ Frontend running on `localhost:3000`
- ✅ Supabase configured
- ✅ At least one dataset processed

### Step-by-Step Testing

#### 1. Start Backend (Terminal 1)
```bash
cd backend
source ~/.zshrc  # Load environment with XGBoost support
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

#### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**Expected Output:**
```
- Local:        http://localhost:3000
- ready started server on 0.0.0.0:3000
```

#### 3. Test Datasets Page
1. Navigate to: `http://localhost:3000/datasets`
2. **Expected:** See real datasets from Supabase
3. **If empty:** Datasets not synced yet
4. **If error:** Backend not running or CORS issue

**Troubleshooting:**
```bash
# Check if datasets are in Supabase
cd backend
python3 -c "
from app.supabase.client import get_supabase_client
supabase = get_supabase_client()
datasets = supabase.get_datasets()
print(f'Found {len(datasets)} datasets')
for d in datasets:
    print(f'  - {d[\"name\"]}: {d[\"status\"]}')
"
```

#### 4. Test Training Page
1. Navigate to: `http://localhost:3000/models/train`
2. Select a dataset (must be processed)
3. Select a model type
4. Click "Start Training"
5. **Expected:** Success message with model ID

**If Error:**
- "Dataset not found" → Dataset not in registry
- "Dataset not processed" → Run `python scripts/process_dataset.py <dataset_id>`
- "Backend not running" → Start backend

#### 5. Test Benchmarks Page
1. Navigate to: `http://localhost:3000/benchmarks`
2. **Expected:** See models grouped by dataset
3. **If empty:** No models trained yet
4. **If error:** Backend not running

---

## 🐛 COMMON ISSUES & FIXES

### Issue 1: CORS Error
**Symptom:** Browser console shows CORS policy error

**Fix:** Add CORS middleware to backend

```python
# File: backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: 401 Unauthorized
**Symptom:** All API calls return 401

**Fix:** Disable authentication for development

```python
# File: backend/app/api/dependencies.py
# Comment out authentication temporarily
def get_current_researcher():
    return {"id": "dev-user", "email": "dev@example.com"}
```

### Issue 3: Connection Refused
**Symptom:** "Failed to fetch" or "Network Error"

**Fix:** Verify backend is running
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"healthy"}
```

### Issue 4: Empty Datasets
**Symptom:** Datasets page shows "No datasets available"

**Fix:** Sync datasets to Supabase
```bash
cd backend
python3 scripts/sync_datasets_to_supabase.py
```

### Issue 5: Dataset Not Processed
**Symptom:** Training fails with "Dataset splits not found"

**Fix:** Process the dataset
```bash
cd backend
python3 scripts/process_dataset.py givemesomecredit
```

---

## 📋 COMPLETE WORKFLOW TEST

### End-to-End Test Scenario

```bash
# Terminal 1: Backend
cd backend
source ~/.zshrc
uvicorn app.main:app --reload

# Terminal 2: Process Dataset
cd backend
python3 scripts/process_dataset.py givemesomecredit
# Wait for completion (~1 minute)

# Terminal 3: Frontend
cd frontend
npm run dev

# Browser:
# 1. Go to http://localhost:3000/datasets
# 2. Verify "Give Me Some Credit" appears
# 3. Go to /models/train
# 4. Select "Give Me Some Credit"
# 5. Select "XGBoost"
# 6. Click "Start Training"
# 7. Wait for success message
# 8. Go to /benchmarks
# 9. Verify model appears in table
```

---

## 🚀 DEPLOYMENT GUIDE

### Option A: Local Development (Current)
- Backend: `localhost:8000`
- Frontend: `localhost:3000`
- Database: Supabase cloud

### Option B: Production Deployment

#### 1. Backend Deployment (Heroku/Railway/Render)

**Environment Variables:**
```bash
DATABASE_URL=postgresql://...
SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
SUPABASE_KEY=your-key-here
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-key
```

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 2. Frontend Deployment (Vercel/Netlify)

**Environment Variables:**
```bash
NEXT_PUBLIC_API_URL=https://your-backend.herokuapp.com/api/v1
```

**Build Command:**
```bash
npm run build
```

**Deploy:**
```bash
# Vercel
vercel deploy

# Netlify
netlify deploy --prod
```

---

## 📊 VERIFICATION CHECKLIST

### Backend Health
- [ ] Backend starts without errors
- [ ] Health endpoint responds: `curl http://localhost:8000/api/v1/health`
- [ ] Supabase connection works
- [ ] Datasets endpoint returns data: `curl http://localhost:8000/api/v1/datasets/`

### Frontend Health
- [ ] Frontend starts without errors
- [ ] No console errors in browser
- [ ] Can navigate to all pages
- [ ] API calls succeed (check Network tab)

### Data Flow
- [ ] Datasets page shows real data
- [ ] Can select a dataset
- [ ] Training page accepts submission
- [ ] Benchmarks page shows results

### End-to-End
- [ ] Can process a dataset
- [ ] Can train a model
- [ ] Can view benchmarks
- [ ] No errors in any workflow

---

## 🎯 QUICK START (Copy-Paste)

```bash
# Terminal 1: Backend
cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis/backend
source ~/.zshrc
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis/frontend
npm run dev

# Browser: http://localhost:3000
```

---

## 🔧 DEBUGGING TIPS

### Check Backend Logs
```bash
# Backend terminal shows all API requests
# Look for errors or 404s
```

### Check Frontend Console
```bash
# Browser DevTools → Console
# Look for network errors or API failures
```

### Check Network Tab
```bash
# Browser DevTools → Network
# Filter: XHR
# Check API call responses
```

### Test API Directly
```bash
# Test datasets endpoint
curl http://localhost:8000/api/v1/datasets/

# Test benchmarks endpoint
curl http://localhost:8000/api/v1/benchmarks/

# Test health
curl http://localhost:8000/api/v1/health
```

---

## 📈 PERFORMANCE EXPECTATIONS

### API Response Times
- Datasets list: <100ms
- Start training: <500ms
- Benchmarks: <200ms

### Training Times
- XGBoost: 0.3-1s (small dataset)
- Random Forest: 2-5s (small dataset)
- Large datasets: 10-60s

### Dataset Processing
- Small (1K rows): 10-30s
- Medium (150K rows): 1-2 min
- Large (590K rows): 5-10 min

---

## ✅ SUCCESS CRITERIA

### Minimum Viable
- [ ] Backend starts
- [ ] Frontend starts
- [ ] Can view datasets
- [ ] Can start training
- [ ] No critical errors

### Fully Functional
- [ ] All pages load
- [ ] All API calls work
- [ ] Can complete full workflow
- [ ] Benchmarks show data
- [ ] Error handling works

### Production Ready
- [ ] CORS configured
- [ ] Authentication working
- [ ] Error messages helpful
- [ ] Loading states smooth
- [ ] Deployed and accessible

---

## 🎉 YOU'RE DONE WHEN...

✅ Backend runs without errors  
✅ Frontend runs without errors  
✅ Datasets page shows real data  
✅ Training page submits successfully  
✅ Benchmarks page displays results  
✅ No console errors  
✅ Complete workflow tested  

**Congratulations! Your platform is 100% functional!** 🚀
