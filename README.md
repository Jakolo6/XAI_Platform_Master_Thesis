# XAI Finance Benchmark Platform

> **Explainable AI in Financial Services: Benchmarking Predictive and Interpretability Performance**

A comprehensive research platform for benchmarking explainable AI (XAI) methods in financial fraud detection contexts. This platform supports reproducible evaluation of ML models and explanation algorithms using the IEEE-CIS Fraud Detection dataset.

**Institution:** Nova School of Business and Economics  
**Status:** Phase 2 - Backend Core Development (60% complete)  
**Last Updated:** 2025-10-08

---

## 🎯 Project Goal

Develop a reproducible, extensible, and interactive web platform for benchmarking explainable AI (XAI) methods in financial contexts. The platform enables comparison of predictive models and explanation algorithms using real-world financial datasets, focusing on accuracy, interpretability, and regulatory transparency.

---

## 📊 Current Status

### ✅ Phase 1: Infrastructure (100% Complete)
- Complete backend scaffold with FastAPI
- Database models for all entities
- Authentication system (JWT)
- Docker configuration
- CI/CD pipeline
- Comprehensive documentation

### 🔄 Phase 2: Backend Core (60% Complete)
- ✅ Dataset management fully implemented
- ✅ Kaggle API integration
- ✅ Data preprocessing pipeline
- ⏳ Model training (next priority)
- ⏳ XAI explanation generation

### ⏳ Phase 3-7: Upcoming
- Frontend development (Next.js 15)
- Human study module
- Report generation
- Deployment to Netlify/Render

---

## 🏗️ Architecture

- **Frontend**: Next.js 15 + TypeScript + TailwindCSS + shadcn/ui (Netlify)
- **Backend**: FastAPI + Celery + Redis + PostgreSQL (Render)
- **Storage**: Supabase for datasets, models, and reports
- **Dataset**: IEEE-CIS Fraud Detection (Kaggle API integration)

---

## 📁 Project Structure

```
xai-finance-benchmark/
├── backend/              # FastAPI application (Phase 1 & 2)
│   ├── app/
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Configuration & database
│   │   ├── models/      # SQLAlchemy models
│   │   ├── tasks/       # Celery tasks
│   │   └── utils/       # Utilities (preprocessing, Kaggle)
│   ├── workers.py       # Celery configuration
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js app (Phase 3 - not started)
├── data/                # Dataset storage
├── docs/                # Documentation
├── .github/             # CI/CD workflows
├── docker-compose.yml   # Docker services
├── .env.example         # Environment template
├── PROJECT_STATUS.md    # Detailed status
├── NEXT_STEPS.md        # Implementation guide
└── QUICK_START.md       # Quick reference
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (you have 3.13 ✅)
- **Docker Desktop** (not installed yet ❌)
- **Kaggle credentials** (configured ✅)

### Installation

#### Option 1: Docker (Recommended)
```bash
# Install Docker Desktop from:
# https://www.docker.com/products/docker-desktop

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Option 2: Manual Setup
```bash
# Install PostgreSQL and Redis
brew install postgresql@15 redis

# Start services
brew services start postgresql@15
brew services start redis

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload
```

### Verify Installation
```bash
# Health check
curl http://localhost:8000/api/v1/health/detailed

# API documentation
open http://localhost:8000/api/v1/docs
```

---

## 📚 Documentation

- **[PROJECT_STATUS.md](PROJECT_STATUS.md)** - Detailed project status and completion
- **[NEXT_STEPS.md](NEXT_STEPS.md)** - Comprehensive implementation guide
- **[QUICK_START.md](QUICK_START.md)** - Quick reference for next AI session
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Installation and setup instructions
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System architecture and design
- **[API Documentation](http://localhost:8000/api/v1/docs)** - Interactive API docs (when running)

---

## 🧪 Research Features

### Model Training
- **Algorithms**: Logistic Regression, Random Forest, XGBoost, LightGBM, CatBoost, MLP
- **Metrics**: AUC, PR-AUC, F1, Log Loss, Calibration, Brier Score
- **Hyperparameter Tuning**: Optuna with YAML configuration

### XAI Methods
- **SHAP**: TreeExplainer, KernelExplainer
- **LIME**: Tabular explanations
- **DiCE**: Counterfactual explanations (Phase 2B)
- **Quantus**: Explanation quality metrics

### Human Study Module
- **Metrics**: Binary decisions, confidence (1-7), trust (1-7), response time
- **Design**: Randomized with/without explanations
- **Target**: 30 participants × 20 transactions = 600 interactions

---

## 🔑 Important Notes

### Kaggle Credentials
- **Status:** ✅ Configured at `~/.kaggle/kaggle.json`
- **Username:** jaakoob6
- **Ready to download IEEE-CIS dataset**

### Docker Status
- **Status:** ❌ Not installed
- **Impact:** Cannot use docker-compose for easy setup
- **Solution:** Install Docker Desktop or use manual PostgreSQL/Redis setup

### Next Priority
- **Install Docker or PostgreSQL/Redis**
- **Start backend services**
- **Implement model training utilities**
- **Test end-to-end model training**

---

## 🎓 Research Context

This platform supports the Master's thesis:
> *"Explainable AI in Financial Services: Benchmarking Predictive and Interpretability Performance"*

**Institution**: Nova School of Business and Economics  
**Focus**: Reproducible XAI evaluation in financial fraud detection  
**Compliance**: EU AI Act Articles 13 & 14, GDPR

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 For Next AI Session

**Read these files first:**
1. `PROJECT_STATUS.md` - Current status
2. `NEXT_STEPS.md` - What to implement
3. `QUICK_START.md` - Quick reference

**Then:**
1. Check if Docker is installed
2. Start backend services
3. Implement model training utilities
4. Test with one model (e.g., XGBoost)

---

**Built with ❤️ for explainable AI research**
