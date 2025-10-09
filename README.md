# 🧠 XAI Platform for Financial Fraud Detection

> **Master's Thesis Project:** Explainable AI in Financial Services - Benchmarking Predictive and Interpretability Performance

A production-ready research platform for comparing explainable AI (XAI) methods in financial fraud detection. Built with FastAPI, Next.js, and Docker.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)

**Institution:** Nova School of Business and Economics  
**Status:** 85% Complete 🚀 | Thesis-Ready ✅  
**Last Updated:** October 9, 2025

## 🎉 What's New (October 9, 2025)

**Major Update:** LIME Integration & Method Comparison Complete!

- 🍋 **LIME Explainer** - Local interpretable explanations (3-5 min, optimized 5x!)
- 🔄 **Method Comparison** - Side-by-side SHAP vs LIME analysis
- 📊 **Quality Metrics** - Quantus evaluation (Faithfulness, Robustness, Complexity)
- 🎛️ **Method Switcher** - Toggle between SHAP 🔮 and LIME 🍋 instantly
- 📈 **Progress Tracking** - Real-time updates with visual progress bar
- 📚 **Documentation** - 2,370+ lines of comprehensive guides
- 🧪 **Testing Framework** - Complete validation system ready

**Research Findings:**
- 40% feature overlap between SHAP and LIME
- 0.617 Spearman correlation
- Both methods identify C13 as top feature
- Complementary insights for comprehensive XAI

---

## 🎯 Overview

This platform enables researchers and practitioners to:
- **Train** 6 ML models on fraud detection data (CatBoost, XGBoost, RF, LightGBM, MLP, LogReg)
- **Explain** predictions using multiple XAI methods (SHAP ✅, LIME ✅)
- **Compare** explanation methods side-by-side with quantitative metrics ✅
- **Evaluate** explanation quality using Quantus framework ✅
- **Switch** between methods with interactive UI ✅
- **Track** progress with real-time updates ✅

### Key Features
✅ **590,540 transactions** from IEEE-CIS Fraud Detection dataset  
✅ **94.3% AUC-ROC** best model performance (XGBoost)  
✅ **SHAP explanations** in 3 seconds  
✅ **LIME explanations** in 3-5 minutes (optimized!)  
✅ **Method comparison** with 40% agreement, 0.617 correlation  
✅ **Quality metrics** (Faithfulness, Robustness, Complexity)  
✅ **Interactive switcher** between SHAP and LIME  
✅ **Real-time progress** tracking with visual indicators  
✅ **Docker deployment** for reproducibility  
✅ **Comprehensive documentation** (2,370+ lines)  

---

## 📊 Current Status

### ✅ Phase 1: Foundation (Complete)
- Full-stack architecture (FastAPI + Next.js + PostgreSQL + Redis)
- 6 trained models with comprehensive metrics
- SHAP explanations working end-to-end
- Interactive dashboard with real-time updates
- Authentication and authorization
- Docker containerization

### ✅ Phase 2: Multi-Method XAI (95% Complete)
- ✅ SHAP integration complete
- ✅ LIME integration complete (optimized 5x faster!)
- ✅ Comparison dashboard with side-by-side analysis
- ✅ Quality metrics using Quantus framework
- ✅ Method switcher with interactive UI
- ✅ Progress tracking for long-running tasks
- ⏳ DiCE counterfactuals (future work)

### 📋 Roadmap
See [THESIS_ENHANCEMENT_PLAN.md](THESIS_ENHANCEMENT_PLAN.md) for the complete 9-phase roadmap.

---

## 🏗️ Architecture

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Frontend  │ ───> │   Backend    │ ───> │  Database   │
│  (Next.js)  │ <─── │  (FastAPI)   │ <─── │ (Postgres)  │
└─────────────┘      └──────────────┘      └─────────────┘
                            │
                            ↓
                     ┌──────────────┐      ┌─────────────┐
                     │    Celery    │ ───> │    Redis    │
                     │   Workers    │ <─── │   (Cache)   │
                     └──────────────┘      └─────────────┘
```

**Tech Stack:**
- **Frontend:** Next.js 15, TypeScript, TailwindCSS, Recharts, Zustand
- **Backend:** FastAPI, SQLAlchemy, Celery, Structlog
- **Database:** PostgreSQL (async with asyncpg)
- **Cache:** Redis (Celery broker + explanation storage)
- **ML:** scikit-learn, XGBoost, LightGBM, CatBoost
- **XAI:** SHAP, LIME, Quantus
- **Deployment:** Docker Compose

---

## 📁 Project Structure

```
xai-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # API routes
│   │   ├── core/                # Config & database
│   │   ├── models/              # SQLAlchemy models
│   │   ├── tasks/               # Celery tasks
│   │   └── utils/
│   │       ├── explainers/      # SHAP, LIME, DiCE
│   │       ├── preprocessing.py # Data pipeline
│   │       └── training.py      # Model training
│   ├── data/                    # Datasets & models (gitignored)
│   ├── requirements.txt
│   └── workers.py               # Celery config
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js pages
│   │   ├── components/          # React components
│   │   ├── lib/                 # API client
│   │   └── store/               # Zustand stores
│   └── package.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── API.md
│   └── DATASETS.md
├── docker-compose.yml
├── .env.example
├── THESIS_ENHANCEMENT_PLAN.md   # 9-phase roadmap
├── IMPLEMENTATION_CHECKLIST.md  # Task tracking
├── PROJECT_STATUS.md            # Current status
└── README.md                    # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop ([Download](https://www.docker.com/products/docker-desktop))
- Kaggle API credentials ([Setup Guide](https://www.kaggle.com/docs/api))
- 8GB+ RAM recommended

### 1. Clone Repository
```bash
git clone https://github.com/Jakolo6/XAI_Platform_Master_Thesis.git
cd XAI_Platform_Master_Thesis
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Add your Kaggle credentials to .env
# KAGGLE_USERNAME=your_username
# KAGGLE_KEY=your_api_key
```

### 3. Start Services
```bash
# Start all services (backend, frontend, database, redis, celery)
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 4. Access Platform
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/v1/docs
- **Celery Flower:** http://localhost:5555

### 5. Login
```
Email: researcher@xai.com
Password: research123
```

---

## 📖 How to Use This Repository

### For Researchers & Students

1. **Clone and Install** - Follow [INSTALLATION.md](INSTALLATION.md) for complete setup
2. **Explore the Platform** - Login and navigate the dashboard
3. **Train Models** - Use the UI to train fraud detection models
4. **Generate Explanations** - Create SHAP/LIME explanations for model predictions
5. **Analyze Results** - Compare model performance and explanation quality
6. **Extend the Platform** - Add new XAI methods or models (see [CONTRIBUTING.md](CONTRIBUTING.md))

### For Thesis Committee

1. **Review Documentation** - Start with [PROJECT_STATUS.md](PROJECT_STATUS.md)
2. **Understand Architecture** - Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. **See Implementation Plan** - Check [THESIS_ENHANCEMENT_PLAN.md](THESIS_ENHANCEMENT_PLAN.md)
4. **Test the Platform** - Follow Quick Start above
5. **Review Code Quality** - Explore backend/frontend structure

### For Practitioners

1. **Deploy Platform** - Use Docker Compose for production deployment
2. **Upload Your Data** - Replace IEEE-CIS with your fraud detection dataset
3. **Train Custom Models** - Configure hyperparameters via API or UI
4. **Generate Reports** - Export XAI audit reports for compliance
5. **Integrate with Systems** - Use REST API for integration

### For Contributors

1. **Read Guidelines** - See [CONTRIBUTING.md](CONTRIBUTING.md)
2. **Setup Development** - Follow [INSTALLATION.md](INSTALLATION.md)
3. **Pick an Issue** - Check [GitHub Issues](https://github.com/Jakolo6/XAI_Platform_Master_Thesis/issues)
4. **Submit PR** - Follow the contribution workflow
5. **Get Recognition** - Be listed in contributors

---

## 📚 Documentation

| Document | Description | Audience |
|----------|-------------|----------|
| **[README.md](README.md)** | Project overview and quick start | Everyone |
| **[INSTALLATION.md](INSTALLATION.md)** | Complete installation guide | New users |
| **[CONTRIBUTING.md](CONTRIBUTING.md)** | Contribution guidelines | Contributors |
| **[THESIS_ENHANCEMENT_PLAN.md](THESIS_ENHANCEMENT_PLAN.md)** | 9-phase development roadmap | Researchers |
| **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** | Daily task tracking | Developers |
| **[PROJECT_STATUS.md](PROJECT_STATUS.md)** | Current implementation status | Committee |
| **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** | System architecture | Technical |
| **[docs/API.md](docs/API.md)** | API endpoint documentation | Developers |
| **[docs/DATASETS.md](docs/DATASETS.md)** | Dataset information | Researchers |

---

## 🧪 Features

### Machine Learning Models
- **Logistic Regression** - Baseline (47.8% AUC-ROC)
- **Random Forest** - 93.2% AUC-ROC
- **XGBoost** - 94.1% AUC-ROC 🥈
- **LightGBM** - 93.0% AUC-ROC
- **CatBoost** - 94.3% AUC-ROC 🥇
- **MLP Neural Network** - 55.2% AUC-ROC

### XAI Methods
| Method | Status | Description |
|--------|--------|-------------|
| **SHAP** | ✅ Complete | TreeExplainer for global feature importance |
| **LIME** | 🔄 In Progress | Local interpretable model-agnostic explanations |
| **DiCE** | ⏳ Planned | Counterfactual explanations |
| **Quantus** | ⏳ Planned | Explanation quality metrics |

### Dashboard Features
- ✅ Model leaderboard with performance metrics
- ✅ Confusion matrix visualization
- ✅ Feature importance charts (SHAP)
- ✅ Real-time explanation generation
- ✅ Interactive data exploration
- 🔄 Multi-method comparison (in progress)

---

## 🎓 Research Context

**Master's Thesis:**  
*"Explainable AI in Financial Services: Benchmarking Predictive and Interpretability Performance"*

**Institution:** Nova School of Business and Economics  
**Supervisor:** [Advisor Name]  
**Timeline:** 8 weeks to completion  

**Research Questions:**
1. How do different XAI methods compare in financial fraud detection?
2. What quantitative metrics best measure explanation quality?
3. How do human evaluators perceive different explanation methods?
4. Can we establish a framework for XAI benchmarking in finance?

**Compliance:** EU AI Act Articles 13 & 14, GDPR Article 22

---

## 🤝 Contributing

This is a research project, but contributions are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **IEEE-CIS Fraud Detection Dataset** - Kaggle competition dataset
- **SHAP Library** - Scott Lundberg and team
- **LIME Library** - Marco Tulio Ribeiro and team
- **FastAPI** - Sebastián Ramírez
- **Next.js** - Vercel team

---

## 📧 Contact

**Jakob Lindner**  
Nova School of Business and Economics  
Email: [57322@novasbe.pt]  
GitHub: [@Jakolo6](https://github.com/Jakolo6)

---

**Built with ❤️ for explainable AI research**
