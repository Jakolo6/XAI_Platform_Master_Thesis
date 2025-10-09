# Next Steps for AI Assistant

**Date:** 2025-10-08  
**Current Phase:** Phase 2 - Backend Core Development  
**Completion:** 60% of Phase 2, 35% overall

---

## 🎯 Immediate Actions Required

### 1. Environment Setup (User Dependency)

The user needs to install Docker or PostgreSQL/Redis before backend can run.

**Check if Docker is installed:**
```bash
which docker
docker --version
```

**If Docker is NOT installed, user has two options:**

#### Option A: Install Docker Desktop (Recommended)
- Download from: https://www.docker.com/products/docker-desktop
- Install and start Docker Desktop
- Then run: `docker-compose up -d`

#### Option B: Manual Installation
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install services
brew install postgresql@15 redis

# Start services
brew services start postgresql@15
brew services start redis

# Create database
psql postgres -c "CREATE DATABASE xai_finance_db;"
psql postgres -c "CREATE USER xai_user WITH PASSWORD 'xai_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE xai_finance_db TO xai_user;"
```

### 2. Configure Environment Variables

**Create `.env` file from template:**
```bash
cp .env.example .env
```

**Edit `.env` and update these critical values:**
- `JWT_SECRET_KEY` - Generate a secure random string
- `SUPABASE_URL` - Create Supabase project and add URL
- `SUPABASE_ANON_KEY` - Get from Supabase project settings
- `SUPABASE_SERVICE_ROLE_KEY` - Get from Supabase project settings

**Note:** Kaggle credentials are already configured at `~/.kaggle/kaggle.json`

### 3. Start Backend Services

**If using Docker:**
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

**If using manual setup:**
```bash
# Terminal 1: Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Celery Worker
cd backend
source venv/bin/activate
celery -A workers worker --loglevel=info --concurrency=2

# Terminal 3: Celery Beat
cd backend
source venv/bin/activate
celery -A workers beat --loglevel=info
```

### 4. Verify Backend is Running

```bash
# Health check
curl http://localhost:8000/api/v1/health/detailed

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "database": {"status": "healthy"},
#     "redis": {"status": "healthy"}
#   }
# }

# Check API docs
open http://localhost:8000/api/v1/docs
```

---

## 🔨 Development Tasks (In Priority Order)

### Phase 2A: Model Training Implementation (Next Priority)

#### Task 1: Create Model Training Utilities
**File:** `backend/app/utils/training.py`

**Requirements:**
- Model factory for 6 algorithms: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost, MLP
- Training pipeline with cross-validation
- Hyperparameter optimization using Optuna (light tuning)
- Model evaluation with metrics:
  - AUC-ROC, AUC-PR
  - F1 Score, Precision, Recall
  - Log Loss, Brier Score
  - Calibration metrics
- Model serialization with SHA256 hash for versioning
- Integration with Supabase for model storage

**Key Functions to Implement:**
```python
class ModelTrainer:
    def __init__(self, model_type: str, hyperparameters: dict)
    def train(self, X_train, y_train, X_val, y_val)
    def evaluate(self, X_test, y_test)
    def optimize_hyperparameters(self, X_train, y_train)
    def save_model(self, model_path: str)
    def calculate_model_hash(self, model)
```

#### Task 2: Implement Training Tasks
**File:** `backend/app/tasks/training_tasks.py`

**Requirements:**
- Complete the `train_model` task stub
- Load dataset from Supabase/local storage
- Train model with progress updates
- Calculate all required metrics
- Save model to Supabase
- Update database with results
- Handle errors and timeouts

**Task Signature:**
```python
@celery_app.task(bind=True)
def train_model(
    self,
    model_id: str,
    dataset_id: str,
    model_type: str,
    hyperparameters: Dict[str, Any],
    optimize: bool = False
) -> Dict[str, Any]
```

#### Task 3: Complete Model API Endpoints
**File:** `backend/app/api/v1/endpoints/models.py`

**Requirements:**
- Implement all model endpoints (currently stubs)
- Add Pydantic schemas for request/response
- Integrate with training tasks
- Add model comparison functionality
- Create leaderboard endpoint with sorting/filtering

**Endpoints to Implement:**
```python
POST   /api/v1/models/train          # Train new model
GET    /api/v1/models                # List models with filters
GET    /api/v1/models/{id}           # Get model details
GET    /api/v1/models/{id}/metrics   # Get detailed metrics
POST   /api/v1/models/{id}/predict   # Make predictions
GET    /api/v1/models/leaderboard    # Performance leaderboard
DELETE /api/v1/models/{id}           # Delete model
```

### Phase 2B: XAI Explanation Implementation

#### Task 4: Create XAI Utilities
**File:** `backend/app/utils/xai.py`

**Requirements:**
- SHAP TreeExplainer for tree-based models
- SHAP KernelExplainer for other models
- LIME tabular explainer
- Explanation caching with Redis
- Quantus metrics integration (faithfulness, stability, sparsity)
- Visualization data preparation

**Key Functions:**
```python
class XAIExplainer:
    def __init__(self, method: str, model, X_background)
    def explain_global(self, X_data)
    def explain_local(self, X_instance)
    def calculate_quality_metrics(self, explanation, X_data, y_data)
    def cache_explanation(self, cache_key: str, explanation)
    def get_cached_explanation(self, cache_key: str)
```

#### Task 5: Implement Explanation Tasks
**File:** `backend/app/tasks/explanation_tasks.py`

**Requirements:**
- Complete the `generate_explanation` task stub
- Load model and dataset
- Generate explanations with appropriate method
- Calculate quality metrics
- Cache results
- Store in Supabase

#### Task 6: Complete Explanation API Endpoints
**File:** `backend/app/api/v1/endpoints/explanations.py`

**Requirements:**
- Implement all explanation endpoints
- Add explanation comparison functionality
- Support both global and local explanations
- Return visualization-ready data

---

## 📁 File Structure Status

### ✅ Completed Files
```
backend/
├── app/
│   ├── __init__.py ✅
│   ├── main.py ✅ (FastAPI app with middleware)
│   ├── core/
│   │   ├── __init__.py ✅
│   │   ├── config.py ✅ (Settings + model/XAI configs)
│   │   ├── database.py ✅ (Async SQLAlchemy)
│   │   └── security.py ✅ (JWT + password hashing)
│   ├── models/
│   │   ├── __init__.py ✅
│   │   ├── dataset.py ✅ (Dataset + DatasetStatus)
│   │   ├── model.py ✅ (Model + ModelMetrics)
│   │   ├── explanation.py ✅ (Explanation + ExplanationMetrics)
│   │   ├── user.py ✅ (User + UserRole)
│   │   └── study.py ✅ (StudySession + StudyInteraction)
│   ├── api/
│   │   ├── __init__.py ✅
│   │   └── v1/
│   │       ├── __init__.py ✅
│   │       ├── api.py ✅ (Main router)
│   │       └── endpoints/
│   │           ├── __init__.py ✅
│   │           ├── health.py ✅ (All health checks)
│   │           ├── auth.py ✅ (Register, login, refresh)
│   │           ├── datasets.py ✅ (Full CRUD + preprocessing)
│   │           ├── models.py ⚠️ (Stub only)
│   │           ├── explanations.py ⚠️ (Stub only)
│   │           ├── study.py ⚠️ (Stub only)
│   │           ├── reports.py ⚠️ (Stub only)
│   │           └── tasks.py ✅ (Task status tracking)
│   ├── utils/
│   │   ├── __init__.py ✅
│   │   ├── preprocessing.py ✅ (Complete preprocessing pipeline)
│   │   └── kaggle_client.py ✅ (Kaggle API integration)
│   └── tasks/
│       ├── __init__.py ✅
│       ├── dataset_tasks.py ✅ (Download, preprocess, stats)
│       ├── training_tasks.py ⚠️ (Stub only)
│       ├── explanation_tasks.py ⚠️ (Stub only)
│       └── report_tasks.py ⚠️ (Stub only)
├── workers.py ✅ (Celery configuration)
├── requirements.txt ✅ (All dependencies)
└── Dockerfile ✅
```

### ⏳ Files to Create Next
```
backend/app/utils/
├── training.py ⏳ (Model training utilities)
├── xai.py ⏳ (XAI explanation utilities)
├── metrics.py ⏳ (Evaluation metrics)
└── storage.py ⏳ (Supabase integration)
```

---

## 🧪 Testing Strategy

### Unit Tests to Create
```
tests/
├── test_preprocessing.py ⏳
├── test_training.py ⏳
├── test_xai.py ⏳
├── test_api_datasets.py ⏳
├── test_api_models.py ⏳
└── test_api_explanations.py ⏳
```

### Integration Tests
- End-to-end dataset processing
- Model training pipeline
- Explanation generation
- API endpoint integration

---

## 🎨 Frontend Development (Phase 3)

### When Backend is Complete, Create:

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx (Landing page)
│   │   ├── layout.tsx (Root layout with Nova SBE branding)
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── (dashboard)/
│   │   │   ├── datasets/page.tsx
│   │   │   ├── models/page.tsx
│   │   │   ├── explanations/page.tsx
│   │   │   └── leaderboard/page.tsx
│   │   └── (study)/
│   │       └── [sessionId]/page.tsx
│   ├── components/
│   │   ├── ui/ (shadcn/ui components)
│   │   ├── charts/ (Visualization components)
│   │   ├── forms/ (Form components)
│   │   └── layout/ (Layout components)
│   ├── lib/
│   │   ├── api.ts (API client)
│   │   ├── auth.ts (Auth utilities)
│   │   └── utils.ts
│   └── types/
│       └── index.ts (TypeScript types)
├── public/
│   └── nova-sbe-logo.svg
├── package.json
├── tailwind.config.js
├── next.config.js
└── tsconfig.json
```

**Design System:**
- Colors: White + Navy (#1e3a8a) + Mint (#10b981)
- WCAG 2.1 AA compliant
- Responsive (desktop, tablet, mobile)

---

## 📊 Research Deliverables Checklist

### Technical Benchmarking
- ⏳ Train all 6 models on IEEE-CIS dataset
- ⏳ Generate explanations with SHAP, LIME
- ⏳ Calculate explanation quality metrics
- ⏳ Create performance comparison tables
- ⏳ Generate benchmark visualizations

### Human Study
- ⏳ Create study interface
- ⏳ Implement randomization (50% no explanation, 50% SHAP)
- ⏳ Collect 600 interactions (30 participants × 20 transactions)
- ⏳ Log: binary decision, confidence (1-7), trust (1-7), response time
- ⏳ Export results for statistical analysis

### Regulatory Compliance
- ⏳ Generate XAI audit reports
- ⏳ EU AI Act Articles 13 & 14 compliance
- ⏳ Document model transparency
- ⏳ Human oversight mechanisms

---

## 🔑 Critical Information for Next Session

### Kaggle Credentials (Already Configured)
- **Location:** `~/.kaggle/kaggle.json`
- **Username:** jaakoob6
- **Status:** ✅ Ready to use

### Supabase Setup (To Be Done)
1. Create Supabase project at https://supabase.com
2. Create storage buckets:
   - `datasets` - for dataset files
   - `models` - for trained models
   - `explanations` - for explanation data
   - `reports` - for generated reports
3. Get API keys from Project Settings → API
4. Update `.env` with credentials

### Database Schema
All tables are defined in models but need to be created:
- Run `docker-compose up -d` to auto-create tables
- OR manually run migrations with Alembic

---

## 🚦 Decision Points

### If Docker is Installed:
1. Run `docker-compose up -d`
2. Verify services with `docker-compose ps`
3. Check health: `curl http://localhost:8000/api/v1/health/detailed`
4. **Proceed to:** Implement model training utilities

### If Docker is NOT Installed:
1. Ask user to install Docker Desktop OR
2. Guide through manual PostgreSQL/Redis installation
3. Setup Python virtual environment
4. Install dependencies
5. Start services manually
6. **Then proceed to:** Implement model training utilities

---

## 📝 Code Implementation Priority

### Priority 1: Model Training (Next)
1. Create `backend/app/utils/training.py`
   - ModelTrainer class
   - Support for all 6 models
   - Optuna integration for hyperparameter tuning
   - Metrics calculation
   - Model versioning with SHA256

2. Implement `backend/app/tasks/training_tasks.py`
   - Complete train_model task
   - Add progress reporting
   - Error handling
   - Model storage to Supabase

3. Complete `backend/app/api/v1/endpoints/models.py`
   - All CRUD endpoints
   - Training trigger
   - Metrics retrieval
   - Leaderboard

### Priority 2: XAI Explanations
1. Create `backend/app/utils/xai.py`
   - SHAP TreeExplainer
   - SHAP KernelExplainer
   - LIME integration
   - Caching logic
   - Quantus metrics

2. Implement `backend/app/tasks/explanation_tasks.py`
   - Complete generate_explanation task
   - Cache management
   - Quality metrics

3. Complete `backend/app/api/v1/endpoints/explanations.py`
   - Generation endpoint
   - Comparison endpoint
   - Visualization data

### Priority 3: Supabase Integration
1. Create `backend/app/utils/storage.py`
   - Supabase client wrapper
   - File upload/download
   - Bucket management

2. Integrate storage in tasks
   - Upload models to Supabase
   - Upload explanations
   - Upload reports

---

## 🧪 Testing Commands

```bash
# Run all tests
cd backend && pytest tests/ -v

# Run specific test file
pytest tests/test_preprocessing.py -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html

# Check linting
flake8 app

# Type checking
mypy app --ignore-missing-imports
```

---

## 📖 API Documentation

Once backend is running, access interactive API docs at:
- **Swagger UI:** http://localhost:8000/api/v1/docs
- **ReDoc:** http://localhost:8000/api/v1/redoc

---

## 🎓 Research-Specific Notes

### Dataset Preprocessing
- IEEE-CIS dataset: train_transaction.csv + train_identity.csv
- Balanced sampling: 5-10% (~500k rows)
- Features: ratio, time-of-day, frequency encoding
- Remove IP-like hashes for privacy

### Model Training
- 6 models: LR, RF, XGBoost, LightGBM, CatBoost, MLP
- Light Optuna tuning (3-5 trials per hyperparameter)
- Metrics focus: AUC, PR-AUC, F1, Log Loss, Calibration, Brier Score

### XAI Methods
- **Priority:** SHAP (Tree + Kernel) and LIME
- **Later:** DiCE (counterfactuals), Quantus metrics
- **Focus:** Faithfulness, stability, sparsity
- **Caching:** Global per (model, explainer, subset)

### Human Study
- 30 participants × 20 transactions = 600 interactions
- Randomized: 50% no explanation, 50% SHAP
- Collect: decision, confidence (1-7), trust (1-7), response time
- Pseudonymous session IDs, no authentication

---

## 🚨 Common Issues & Solutions

### Issue: "Database connection failed"
**Solution:** Ensure PostgreSQL is running
```bash
# Docker: docker-compose ps postgres
# Manual: brew services list | grep postgresql
```

### Issue: "Redis connection failed"
**Solution:** Ensure Redis is running
```bash
# Docker: docker-compose ps redis
# Manual: brew services list | grep redis
```

### Issue: "Celery worker not processing tasks"
**Solution:** Check worker logs
```bash
# Docker: docker-compose logs celery_worker
# Manual: Check terminal running celery worker
```

### Issue: "Kaggle API authentication failed"
**Solution:** Verify kaggle.json
```bash
cat ~/.kaggle/kaggle.json
# Should show: {"username":"jaakoob6","key":"..."}
```

### Issue: "Module not found"
**Solution:** Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

---

## 📌 Important Reminders

1. **Kaggle credentials are configured** - ready to download IEEE-CIS dataset
2. **All database models are defined** - tables will auto-create on first run
3. **Dataset preprocessing is fully implemented** - ready to use
4. **Authentication system is complete** - can register/login researchers
5. **Docker is NOT installed** - need to install or use manual setup

---

## 🎯 Success Criteria for Phase 2

- ✅ Dataset management fully functional
- ⏳ All 6 models can be trained successfully
- ⏳ SHAP and LIME explanations can be generated
- ⏳ Explanation quality metrics calculated
- ⏳ Model leaderboard functional
- ⏳ All API endpoints tested and working

---

## 🚀 Quick Start for Next Session

```bash
# 1. Check if Docker is installed
which docker

# 2. If yes, start services
docker-compose up -d

# 3. If no, ask user to install Docker or use manual setup

# 4. Once services are running, verify
curl http://localhost:8000/api/v1/health/detailed

# 5. Proceed with model training implementation
# Start with: backend/app/utils/training.py
```

---

**Current Status:** Backend infrastructure complete, dataset management implemented, ready for model training development.

**Next AI Session Should:** Install/start services → Implement model training → Implement XAI explanations → Test end-to-end
