# XAI Platform - Complete Repository Structure & Cleanup Guide

> **Last Updated:** October 14, 2025  
> **Purpose:** Document all files, their purpose, and identify cleanup candidates

---

## 📁 Folder Structure Overview

```
XAI_Platform_Master_Thesis/
├── backend/                    # Python FastAPI backend application
│   ├── app/                   # Main application code
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality (config, database, security)
│   │   ├── datasets/         # Dataset loaders and registry
│   │   ├── models/           # Data models
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic services
│   │   └── utils/            # Utility functions
│   ├── config/               # Configuration files
│   ├── data/                 # Local data storage (gitignored)
│   ├── migrations/           # Database schema migrations
│   ├── scripts/              # Utility scripts
│   └── tests/                # Test files
├── frontend/                  # Next.js React frontend application
│   ├── public/               # Static assets
│   └── src/                  # Source code
│       ├── app/              # Next.js pages (App Router)
│       ├── components/       # React components
│       └── lib/              # Utilities and API client
├── config/                    # Project-wide configuration
├── data/                      # Local data (development)
├── docs/                      # Documentation
├── scripts/                   # Project-level scripts
├── screenshots/               # Documentation screenshots
└── supabase/                  # Supabase configuration

```

---

## 🗂️ Root Directory Files

### Configuration Files ✅ KEEP

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Environment variables (API keys, secrets) | ✅ KEEP |
| `.env.example` | Template for environment variables | ✅ KEEP |
| `.gitignore` | Git exclusion rules | ✅ KEEP |
| `docker-compose.yml` | Docker container orchestration | ✅ KEEP |
| `netlify.toml` | Netlify deployment configuration | ✅ KEEP |
| `LICENSE` | MIT License | ✅ KEEP |
| `README.md` | Project overview and setup instructions | ✅ KEEP |

### Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| `DAL_MIGRATION_STATUS.md` | Data Access Layer migration tracking | ⚠️ ARCHIVE (migration complete) |
| `DEPLOYMENT_STATUS.md` | Deployment checklist and bug fixes | ✅ KEEP (useful reference) |
| `IMPLEMENTATION_GUIDE.md` | Feature implementation guide | ✅ KEEP |
| `INTERPRETATION_SETUP.md` | LLM interpretation setup guide | ✅ KEEP |

### Root-Level Scripts ❌ DELETE

| File | Purpose | Status |
|------|---------|--------|
| `debug_shap.py` | One-time SHAP debugging script | ❌ DELETE |
| `quick_debug.sh` | Quick debugging helper | ❌ DELETE |
| `quick_health_check.sh` | Health check script | ❌ DELETE |
| `test_api.py` | API testing script | 🔄 MOVE to `backend/tests/` |
| `test_explanation_generation.sh` | Explanation testing | ❌ DELETE |
| `test_model_with_shap.sh` | Model testing | ❌ DELETE |
| `test_platform.sh` | Platform testing | ❌ DELETE |
| `PUSH_TO_GITHUB.sh` | Git push helper | ❌ DELETE |

### Root-Level SQL Files ❌ DELETE/MOVE

| File | Purpose | Status |
|------|---------|--------|
| `supabase_cleanup.sql` | Database cleanup script | 🔄 MOVE to `backend/migrations/archive/` |
| `supabase_tables.sql` | Old table definitions | ❌ DELETE (superseded) |

---

## 🔧 Backend Directory (`/backend`)

### Backend Root Files

| File | Purpose | Status |
|------|---------|--------|
| `.env` | Backend environment variables | ✅ KEEP |
| `.env.example` | Backend env template | ✅ KEEP |
| `Dockerfile` | Docker image definition | ✅ KEEP |
| `Procfile` | Railway deployment process file | ✅ KEEP |
| `requirements.txt` | Python dependencies | ✅ KEEP |
| `workers.py` | Celery background workers | ✅ KEEP |
| `nixpacks.toml` | Railway build configuration | ✅ KEEP |
| `railway.json` | Railway service configuration | ✅ KEEP |
| `railway.toml` | Railway deployment settings | ✅ KEEP |
| `CLEANUP_SUMMARY.md` | Old cleanup notes | ❌ DELETE |
| `test_dataset_registry.py` | Dataset registry tests | 🔄 MOVE to `tests/` |
| `test_explanation_local.py` | Explanation tests | 🔄 MOVE to `tests/` |
| `test_supabase_connection.py` | Supabase connection tests | 🔄 MOVE to `tests/` |

---

## 📂 Backend Application (`/backend/app`)

### Core Module (`/backend/app/core`) ✅ ALL KEEP

| File | Purpose | Details |
|------|---------|---------|
| `__init__.py` | Package initializer | Empty file |
| `config.py` | Application configuration | Loads env vars, API keys, database URLs |
| `database.py` | Database setup | SQLAlchemy setup (deprecated, raises errors) |
| `security.py` | Authentication & security | JWT tokens, password hashing |
| `data_access.py` | **Data Access Layer (DAL)** | Main database interface for Supabase |
| `logging_config.py` | Logging configuration | Structured logging with structlog |

**Purpose:** Core functionality that the entire application depends on.

---

### API Module (`/backend/app/api`) ✅ ALL KEEP

#### `/backend/app/api/dependencies.py`
**Purpose:** FastAPI dependency injection for authentication  
**Key Functions:**
- `get_current_user()` - Validates JWT tokens
- `get_current_researcher()` - Checks researcher role
- `get_current_admin()` - Checks admin role

#### `/backend/app/api/v1/api.py`
**Purpose:** Aggregates all API routers  
**Routes:** Combines all endpoint modules into single API

#### API Endpoints (`/backend/app/api/v1/endpoints/`)

| File | Purpose | Key Endpoints | Status |
|------|---------|---------------|--------|
| `auth.py` | Authentication | `/register`, `/login`, `/refresh` | ✅ KEEP (returns 501, using Supabase Auth) |
| `benchmarks.py` | Model benchmarks | `/benchmarks/`, `/compare`, `/leaderboard` | ✅ KEEP |
| `datasets.py` | Dataset management | `/datasets/`, `/process`, `/upload` | ✅ KEEP |
| `health.py` | Health checks | `/health/`, `/health/db` | ✅ KEEP |
| `home_credit.py` | Home Credit dataset | `/home-credit/status`, `/process` | ✅ KEEP |
| `humanstudy.py` | Human study | `/session/start`, `/response` | ✅ KEEP (future research) |
| `interpretation.py` | LLM interpretation | `/interpret`, `/feedback` | ✅ KEEP |
| `models.py` | Model training | `/train`, `/models/`, `/models/{id}` | ✅ KEEP |
| `research.py` | Research data | `/leaderboard`, `/quality-metrics` | ✅ KEEP |
| `sandbox.py` | Sandbox/playground | `/sample`, `/local`, `/rating` | ✅ KEEP |

---

### Services Module (`/backend/app/services`) ✅ ALL KEEP

| File | Purpose | Key Functions |
|------|---------|---------------|
| `dataset_service.py` | Dataset processing pipeline | `process_dataset()`, `upload_to_r2()` |
| `kaggle_service.py` | Kaggle integration | `download_dataset()`, `load_and_preprocess()` |
| `model_service.py` | Model training | `train_model()`, `_train_xgboost()`, `_train_random_forest()` |
| `r2_service.py` | Cloudflare R2 storage | `upload_file()`, `download_file()`, `upload_directory()` |
| `explanation_service.py` | SHAP & LIME generation | `generate_explanation()`, `generate_shap()`, `generate_lime()` |
| `interpretation_service.py` | OpenAI GPT interpretation | `interpret_explanation()`, `compare_methods()` |
| `metrics_service.py` | Model metrics | `calculate_metrics()`, `calculate_advanced_metrics()` |

**Purpose:** Business logic layer - all core functionality

---

### Utils Module (`/backend/app/utils`) ✅ ALL KEEP

| File | Purpose | Details |
|------|---------|---------|
| `supabase_client.py` | Supabase database client | Wrapper for Supabase operations |
| `r2_storage.py` | R2 storage client | Wrapper for Cloudflare R2 |
| `openai_client.py` | OpenAI API client | GPT-4 integration |
| `logger.py` | Logging utilities | Structured logging helpers |

---

### Models Module (`/backend/app/models`) ✅ ALL KEEP

| File | Purpose | Details |
|------|---------|---------|
| `user.py` | User model | SQLAlchemy model (used for types) |
| `dataset.py` | Dataset model | Dataset metadata structure |
| `model.py` | ML model model | Model metadata structure |

---

### Datasets Module (`/backend/app/datasets`) ✅ ALL KEEP

| File | Purpose | Details |
|------|---------|---------|
| `registry.py` | Dataset registry | Loads and manages dataset configurations |
| `loaders/base.py` | Base loader class | Abstract base for dataset loaders |
| `loaders/german_credit.py` | German Credit loader | Loads and preprocesses German Credit dataset |
| `loaders/home_credit.py` | Home Credit loader | Loads and preprocesses Home Credit dataset |

---

### Schemas Module (`/backend/app/schemas`) ✅ KEEP

| File | Purpose | Details |
|------|---------|---------|
| `dataset.py` | Pydantic schemas | Validation schemas for datasets |

---

## 🗄️ Backend Migrations (`/backend/migrations`)

### Active Migrations ✅ KEEP

| File | Purpose | Status |
|------|---------|--------|
| `FINAL_supabase_schema.sql` | **MAIN DATABASE SCHEMA** | ✅ KEEP - Complete schema with all tables |
| `1_supabase_reset.sql` | Database reset script | ✅ KEEP - Drops all tables |

### Deprecated Migrations ❌ DELETE

| File | Purpose | Status |
|------|---------|--------|
| `2_supabase_complete_schema.sql` | Old complete schema | ❌ DELETE (superseded by FINAL) |
| `3_sandbox_schema.sql` | Old sandbox tables | ❌ DELETE (included in FINAL) |
| `4_interpretation_feedback.sql` | Old feedback table | ❌ DELETE (included in FINAL) |
| `5_add_dal_metadata_columns.sql` | Old DAL columns | ❌ DELETE (included in FINAL) |

**Why FINAL is the only one needed:**
- Contains ALL tables from migrations 2-5
- Includes DAL metadata columns (`last_updated`, `source_module`)
- Has all indexes, views, and triggers
- Single source of truth for database structure

---

## 📜 Backend Scripts (`/backend/scripts`)

| File | Purpose | Status |
|------|---------|--------|
| `move_home_credit_data.py` | One-time R2 data migration | ❌ DELETE |
| Other test scripts | Various testing scripts | 🔄 MOVE to `tests/` or ❌ DELETE |

---

## ⚙️ Backend Config (`/backend/config`)

| File | Purpose | Status |
|------|---------|--------|
| `datasets.yaml` | Dataset registry configuration | ✅ KEEP - Defines available datasets |

**Contents:**
```yaml
datasets:
  - id: german-credit
    name: German Credit Risk
    source: kaggle
    ...
  - id: home-credit-default-risk
    ...
```

---

## 📦 Backend Data (`/backend/data`) ✅ KEEP (gitignored)

| Directory | Purpose | Details |
|-----------|---------|---------|
| `raw/` | Raw datasets | Downloaded from Kaggle (ephemeral) |
| `processed/` | Processed datasets | Train/val/test splits (ephemeral) |
| `models/` | Trained models | Pickled model files (ephemeral) |

**Note:** All files here are temporary and uploaded to R2 for persistence.

---

## 🎨 Frontend Directory (`/frontend`)

### Frontend Root Files ✅ ALL KEEP

| File | Purpose | Details |
|------|---------|---------|
| `package.json` | Node dependencies | React, Next.js, TailwindCSS, etc. |
| `package-lock.json` | Dependency lock file | Ensures consistent installs |
| `next.config.js` | Next.js configuration | API proxy, image optimization |
| `tailwind.config.ts` | TailwindCSS config | Custom colors, themes |
| `postcss.config.js` | PostCSS config | CSS processing |
| `tsconfig.json` | TypeScript config | Compiler options |
| `next-env.d.ts` | Next.js types | Auto-generated type definitions |
| `tsconfig.tsbuildinfo` | TS build cache | Auto-generated build info |

---

## 📱 Frontend Pages (`/frontend/src/app`)

### Core Pages ✅ ALL KEEP

| File | Purpose | Key Features |
|------|---------|--------------|
| `page.tsx` | Landing page | Hero, features, pricing, testimonials |
| `layout.tsx` | Root layout | Navigation, Supabase auth provider |
| `globals.css` | Global styles | TailwindCSS base styles |

### Application Pages ✅ ALL KEEP

| Page | Route | Purpose |
|------|-------|---------|
| `dashboard/page.tsx` | `/dashboard` | Main dashboard with stats and quick actions |
| `models/page.tsx` | `/models` | List all models, train new models |
| `models/[id]/page.tsx` | `/models/{id}` | Model details, generate SHAP/LIME |
| `datasets/page.tsx` | `/datasets` | Dataset management, upload, process |
| `benchmarks/page.tsx` | `/benchmarks` | Cross-dataset model comparison |
| `sandbox/page.tsx` | `/sandbox` | Interactive explanation playground |
| `interpretation/page.tsx` | `/interpretation` | LLM vs rule-based interpretation |
| `research/page.tsx` | `/research` | Research leaderboard, quality metrics |
| `reports/page.tsx` | `/reports` | Export data as CSV |
| `study/page.tsx` | `/study` | Human study interface (future) |

---

## 🧩 Frontend Components (`/frontend/src/components`)

### Reusable Components ✅ ALL KEEP

| File | Purpose | Used In |
|------|---------|---------|
| `Header.tsx` | Top navigation bar | All pages |
| `Footer.tsx` | Footer with links | All pages |
| `Sidebar.tsx` | Side navigation | Dashboard, models, datasets |
| `ModelCard.tsx` | Model display card | Models list, dashboard |
| `DatasetCard.tsx` | Dataset display card | Datasets list |
| `ExplanationVisualization.tsx` | SHAP/LIME charts | Model detail, sandbox |

---

## 🛠️ Frontend Utilities (`/frontend/src/lib`)

### API Client (`/frontend/src/lib/api.ts`) ✅ KEEP

**Purpose:** Centralized API client with all backend endpoints

**Key Exports:**
- `modelsAPI` - Model operations
- `datasetsAPI` - Dataset operations
- `explanationsAPI` - SHAP/LIME operations
- `benchmarksAPI` - Benchmark operations
- `researchAPI` - Research operations

### Supabase (`/frontend/src/lib/supabase/`)

| File | Purpose | Status |
|------|---------|--------|
| `client.ts` | Supabase client | ✅ KEEP - Auth and database |
| `middleware.ts` | Auth middleware | ✅ KEEP - Protected routes |

### Utils (`/frontend/src/lib/utils.ts`) ✅ KEEP

**Purpose:** Utility functions (classnames, formatting, etc.)

---

## 🌐 Frontend Public (`/frontend/public`)

| File | Purpose | Status |
|------|---------|--------|
| `favicon.ico` | Site favicon | ✅ KEEP |
| `logo.png` | Platform logo | ✅ KEEP |

---

## 📚 Other Directories

### `/config` ✅ KEEP
Project-wide configuration files

### `/data` ✅ KEEP (gitignored)
Local development data storage

### `/docs` ✅ KEEP
Additional documentation and guides

### `/scripts` ⚠️ REVIEW
Utility scripts - most are one-time use

### `/screenshots` ✅ KEEP
Documentation screenshots

### `/supabase` ✅ KEEP
Supabase project configuration

---

## 🗑️ CLEANUP ACTION PLAN

### Step 1: Delete One-Time Scripts (Safe)

```bash
cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis

# Root level
rm debug_shap.py
rm quick_debug.sh
rm quick_health_check.sh
rm test_explanation_generation.sh
rm test_model_with_shap.sh
rm test_platform.sh
rm PUSH_TO_GITHUB.sh
rm supabase_tables.sql

# Backend
rm backend/CLEANUP_SUMMARY.md
rm backend/migrations/2_supabase_complete_schema.sql
rm backend/migrations/3_sandbox_schema.sql
rm backend/migrations/4_interpretation_feedback.sql
rm backend/migrations/5_add_dal_metadata_columns.sql
rm backend/scripts/move_home_credit_data.py
```

### Step 2: Archive Completed Documentation

```bash
# Create archive directories
mkdir -p docs/archive
mkdir -p backend/migrations/archive

# Move to archive
mv DAL_MIGRATION_STATUS.md docs/archive/
mv supabase_cleanup.sql backend/migrations/archive/
```

### Step 3: Reorganize Tests

```bash
# Ensure tests directory exists
mkdir -p backend/tests

# Move test files
mv test_api.py backend/tests/
mv backend/test_dataset_registry.py backend/tests/
mv backend/test_explanation_local.py backend/tests/
mv backend/test_supabase_connection.py backend/tests/
```

### Step 4: Commit Changes

```bash
git add -A
git commit -m "chore: cleanup repository - remove outdated scripts and migrations"
git push origin main
```

---

## 📊 Cleanup Summary

### Files to Delete: 15 files
- 8 root-level test/debug scripts
- 1 root-level SQL file
- 1 backend cleanup doc
- 4 backend migration files (superseded)
- 1 backend script

### Files to Archive: 2 files
- 1 migration status doc
- 1 cleanup SQL script

### Files to Move: 4 files
- 4 test files to proper location

### Files to Keep: ~180 files
- All application code
- All configuration files
- Active documentation
- Main database schema

---

## ✅ Essential Files Checklist

### Must Keep - Core Application
- ✅ All files in `/backend/app/` (60+ files)
- ✅ All files in `/frontend/src/` (40+ files)
- ✅ `backend/migrations/FINAL_supabase_schema.sql`
- ✅ `backend/requirements.txt`
- ✅ `frontend/package.json`

### Must Keep - Configuration
- ✅ `.env` and `.env.example` files
- ✅ `netlify.toml`, `railway.json`, `railway.toml`
- ✅ `docker-compose.yml`, `Dockerfile`, `Procfile`
- ✅ `backend/config/datasets.yaml`

### Must Keep - Documentation
- ✅ `README.md`
- ✅ `DEPLOYMENT_STATUS.md`
- ✅ `IMPLEMENTATION_GUIDE.md`
- ✅ `INTERPRETATION_SETUP.md`

---

## 🎯 Post-Cleanup Verification

After cleanup, verify everything still works:

```bash
# Backend tests
cd backend
python -m pytest tests/

# Frontend build
cd frontend
npm run build

# Start development servers
# Backend: cd backend && uvicorn app.main:app --reload
# Frontend: cd frontend && npm run dev
```

---

## 📈 Impact Analysis

### Before Cleanup
- **Total Files:** ~200
- **Repository Size:** ~500MB (with dependencies)
- **Maintenance Burden:** High (outdated files cause confusion)

### After Cleanup
- **Total Files:** ~185
- **Repository Size:** ~490MB (minimal change)
- **Maintenance Burden:** Low (clear structure)

### Benefits
- ✅ Clearer repository structure
- ✅ Easier onboarding for new developers
- ✅ Reduced confusion about which files are active
- ✅ Faster searches and navigation
- ✅ Better Git history clarity

---

**Last Updated:** October 14, 2025  
**Status:** Ready for cleanup  
**Estimated Time:** 10 minutes  
**Risk Level:** Low (all deletions are safe)
