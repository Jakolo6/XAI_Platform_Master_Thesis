# 🔧 Installation Guide

Complete installation instructions for the XAI Platform.

---

## 📋 System Requirements

### Minimum Requirements
- **OS:** macOS 10.15+, Ubuntu 20.04+, or Windows 10+ (with WSL2)
- **RAM:** 8GB (16GB recommended)
- **Disk Space:** 10GB free space
- **Internet:** Required for downloading datasets

### Software Prerequisites
- **Docker Desktop** 4.0+ ([Download](https://www.docker.com/products/docker-desktop))
- **Git** 2.30+ ([Download](https://git-scm.com/downloads))
- **Kaggle Account** ([Sign up](https://www.kaggle.com/))

---

## 🚀 Quick Installation (Recommended)

### 1. Install Docker Desktop

**macOS:**
```bash
# Download from https://www.docker.com/products/docker-desktop
# Or install via Homebrew:
brew install --cask docker
```

**Ubuntu/Linux:**
```bash
# Install Docker Engine
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

**Windows:**
```powershell
# Download Docker Desktop from:
# https://www.docker.com/products/docker-desktop
# Requires WSL2 - follow installation prompts
```

### 2. Get Kaggle API Credentials

1. Go to [Kaggle Account Settings](https://www.kaggle.com/settings)
2. Scroll to **API** section
3. Click **Create New API Token**
4. Save the downloaded `kaggle.json` file

**macOS/Linux:**
```bash
mkdir -p ~/.kaggle
mv ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

**Windows:**
```powershell
mkdir C:\Users\<YourUsername>\.kaggle
move Downloads\kaggle.json C:\Users\<YourUsername>\.kaggle\
```

### 3. Clone Repository

```bash
git clone https://github.com/Jakolo6/XAI_Platform_Master_Thesis.git
cd XAI_Platform_Master_Thesis
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

**Required variables in `.env`:**
```bash
# Kaggle Credentials (from step 2)
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key

# Database (use defaults or customize)
POSTGRES_USER=xai_user
POSTGRES_PASSWORD=xai_password
POSTGRES_DB=xai_finance_db

# JWT Secret (generate a random string)
JWT_SECRET_KEY=your_random_secret_key_here

# Optional: Change ports if needed
BACKEND_PORT=8000
FRONTEND_PORT=3000
```

**Generate JWT Secret:**
```bash
# macOS/Linux
openssl rand -hex 32

# Or use Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Start Platform

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs (optional)
docker-compose logs -f
```

**Expected output:**
```
✔ Container xai_postgres       Started
✔ Container xai_redis          Started
✔ Container xai_backend        Started
✔ Container xai_celery_worker  Started
✔ Container xai_frontend       Started
```

### 6. Verify Installation

```bash
# Check backend health
curl http://localhost:8000/api/v1/health

# Expected response:
# {"status":"healthy","timestamp":"..."}
```

**Access the platform:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/v1/docs
- **Celery Monitor:** http://localhost:5555

### 7. First Login

**Default credentials:**
```
Email: researcher@xai.com
Password: research123
```

⚠️ **Change these credentials in production!**

---

## 🛠️ Manual Installation (Without Docker)

### Prerequisites

**macOS:**
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.11 postgresql@15 redis node@20
```

**Ubuntu/Linux:**
```bash
# Update package list
sudo apt update

# Install dependencies
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql-15 redis-server nodejs npm
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup database
createdb xai_finance_db

# Run migrations (if applicable)
# alembic upgrade head

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Celery Worker Setup

```bash
# In a new terminal, activate venv
cd backend
source venv/bin/activate

# Start Celery worker
celery -A workers worker --loglevel=info

# In another terminal, start Celery Beat (for scheduled tasks)
celery -A workers beat --loglevel=info
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Redis Setup

```bash
# macOS
brew services start redis

# Ubuntu/Linux
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### PostgreSQL Setup

```bash
# macOS
brew services start postgresql@15

# Ubuntu/Linux
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
psql postgres
CREATE DATABASE xai_finance_db;
CREATE USER xai_user WITH PASSWORD 'xai_password';
GRANT ALL PRIVILEGES ON DATABASE xai_finance_db TO xai_user;
\q
```

---

## 📊 Download Dataset

### Option 1: Via API (Recommended)

1. Login to the platform
2. Navigate to **Datasets** page
3. Click **Download IEEE-CIS Dataset**
4. Wait for download to complete (~2GB)
5. Click **Preprocess Dataset**
6. Wait for preprocessing (~10-15 minutes)

### Option 2: Manual Download

```bash
# Using Kaggle CLI
kaggle competitions download -c ieee-fraud-detection

# Extract files
unzip ieee-fraud-detection.zip -d backend/data/raw/

# Run preprocessing via API
curl -X POST http://localhost:8000/api/v1/datasets/{dataset_id}/preprocess \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Train Models

### Via Dashboard (Recommended)

1. Login to platform
2. Navigate to **Models** page
3. Click **Train New Model**
4. Select algorithm (e.g., XGBoost)
5. Configure hyperparameters (or use defaults)
6. Click **Start Training**
7. Monitor progress in real-time

### Via API

```bash
# Get auth token
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"researcher@xai.com","password":"research123"}' \
  | jq -r '.access_token')

# Train model
curl -X POST http://localhost:8000/api/v1/models/train \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "YOUR_DATASET_ID",
    "model_type": "xgboost",
    "hyperparameters": {}
  }'
```

---

## 🔍 Generate Explanations

### SHAP Explanations

```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/explanations/generate?model_id=MODEL_ID&method=shap" \
  -H "Authorization: Bearer $TOKEN"
```

### LIME Explanations

```bash
# Via API
curl -X POST "http://localhost:8000/api/v1/explanations/generate?model_id=MODEL_ID&method=lime" \
  -H "Authorization: Bearer $TOKEN"
```

### Via Dashboard

1. Navigate to **Models** page
2. Click on a trained model
3. Scroll to **Explanations** section
4. Click **Generate SHAP Explanation** or **Generate LIME Explanation**
5. Wait for generation (~10-30 seconds for SHAP, ~5-10 minutes for LIME)
6. View results automatically

---

## 🐛 Troubleshooting

### Docker Issues

**Problem:** Docker containers won't start
```bash
# Check Docker is running
docker info

# Restart Docker Desktop
# macOS: Click Docker icon → Restart
# Linux: sudo systemctl restart docker

# Clean up and restart
docker-compose down
docker-compose up -d
```

**Problem:** Port already in use
```bash
# Find process using port
lsof -i :8000  # or :3000, :5432, etc.

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Database Issues

**Problem:** Database connection failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

**Problem:** Database migrations needed
```bash
# Access backend container
docker-compose exec backend bash

# Run migrations
alembic upgrade head
```

### Celery Issues

**Problem:** Tasks not processing
```bash
# Check Celery worker is running
docker-compose ps celery_worker

# View worker logs
docker-compose logs -f celery_worker

# Restart worker
docker-compose restart celery_worker
```

**Problem:** Redis connection failed
```bash
# Check Redis is running
docker-compose ps redis

# Test Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart Redis
docker-compose restart redis
```

### Frontend Issues

**Problem:** Frontend won't load
```bash
# Check frontend is running
docker-compose ps frontend

# View logs
docker-compose logs -f frontend

# Rebuild frontend
docker-compose up -d --build frontend
```

**Problem:** API connection failed
```bash
# Check backend is accessible
curl http://localhost:8000/api/v1/health

# Check CORS settings in backend/.env
# Ensure FRONTEND_URL is set correctly
```

### Dataset Issues

**Problem:** Kaggle download fails
```bash
# Verify Kaggle credentials
cat ~/.kaggle/kaggle.json

# Test Kaggle CLI
kaggle competitions list

# Re-download manually
kaggle competitions download -c ieee-fraud-detection
```

**Problem:** Out of disk space
```bash
# Check disk space
df -h

# Clean up Docker
docker system prune -a

# Remove old datasets
rm -rf backend/data/raw/*
rm -rf backend/data/processed/*
```

---

## 🔄 Updating the Platform

```bash
# Pull latest changes
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Or for manual installation
cd backend
source venv/bin/activate
pip install -r requirements.txt --upgrade

cd ../frontend
npm install
```

---

## 🧹 Uninstallation

### Docker Installation

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Remove repository
cd ..
rm -rf XAI_Platform_Master_Thesis
```

### Manual Installation

```bash
# Stop services
# macOS
brew services stop postgresql@15
brew services stop redis

# Ubuntu/Linux
sudo systemctl stop postgresql
sudo systemctl stop redis-server

# Remove virtual environment
rm -rf backend/venv

# Remove node modules
rm -rf frontend/node_modules

# Remove repository
cd ..
rm -rf XAI_Platform_Master_Thesis
```

---

## 📞 Getting Help

### Documentation
- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Quick setup guide
- [THESIS_ENHANCEMENT_PLAN.md](THESIS_ENHANCEMENT_PLAN.md) - Development roadmap
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - System architecture

### Support
- **GitHub Issues:** [Report a bug](https://github.com/Jakolo6/XAI_Platform_Master_Thesis/issues)
- **Email:** [your.email@novasbe.pt]
- **Documentation:** Check `/api/v1/docs` when backend is running

### Common Resources
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Kaggle API Documentation](https://github.com/Kaggle/kaggle-api)

---

## ✅ Installation Checklist

- [ ] Docker Desktop installed and running
- [ ] Kaggle credentials configured
- [ ] Repository cloned
- [ ] `.env` file configured
- [ ] Services started with `docker-compose up -d`
- [ ] Backend health check passes
- [ ] Frontend accessible at http://localhost:3000
- [ ] Logged in successfully
- [ ] Dataset downloaded
- [ ] Dataset preprocessed
- [ ] First model trained
- [ ] Explanation generated

---

**Installation complete! You're ready to start using the XAI Platform.** 🎉
