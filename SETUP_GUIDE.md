# XAI Finance Benchmark Platform - Setup Guide

This guide will help you set up the development environment and get the platform running locally.

## Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose**
- **Kaggle API credentials** (for dataset download)
- **Git**

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd XAI_Platform_Master_Thesis
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and configure the following **required** variables:

```bash
# Database
DATABASE_URL=postgresql://xai_user:xai_password@localhost:5432/xai_finance_db
POSTGRES_USER=xai_user
POSTGRES_PASSWORD=xai_password
POSTGRES_DB=xai_finance_db

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=your_secure_jwt_secret_key_here

# Supabase (create a project at supabase.com)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# Kaggle API (IMPORTANT - see below)
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_api_key
```

### 3. Configure Kaggle API Credentials

You mentioned you have a `kaggle.json` file. Set it up:

```bash
# Create .kaggle directory
mkdir -p ~/.kaggle

# Copy your kaggle.json file
cp /path/to/your/kaggle.json ~/.kaggle/kaggle.json

# Set proper permissions
chmod 600 ~/.kaggle/kaggle.json
```

**OR** add credentials to `.env`:

```bash
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### 4. Start Services with Docker

```bash
# Start all services (PostgreSQL, Redis, Backend, Celery)
docker-compose up -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 5. Access the Services

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Celery Flower (Task Monitor)**: http://localhost:5555
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

## Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if using Alembic)
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Celery Worker (in separate terminal)

```bash
cd backend
source venv/bin/activate

# Start Celery worker
celery -A workers worker --loglevel=info --concurrency=2

# Start Celery Beat (scheduler) in another terminal
celery -A workers beat --loglevel=info

# Start Flower (monitoring) in another terminal
celery -A workers flower --port=5555
```

### Frontend Setup (Coming in Phase 3)

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

## Database Setup

### Create Database Manually (if needed)

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE xai_finance_db;
CREATE USER xai_user WITH PASSWORD 'xai_password';
GRANT ALL PRIVILEGES ON DATABASE xai_finance_db TO xai_user;
```

### Initialize Database Tables

The application will automatically create tables on first run. To verify:

```bash
# Check health endpoint
curl http://localhost:8000/api/v1/health/detailed
```

## Download IEEE-CIS Dataset

### Option 1: Via API (Recommended)

Once the backend is running:

```bash
# Register a researcher account
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "researcher@example.com",
    "password": "secure_password",
    "full_name": "Your Name",
    "institution": "Nova SBE"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=researcher@example.com&password=secure_password"

# Download dataset (use token from login)
curl -X POST http://localhost:8000/api/v1/datasets/download-ieee-cis \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Option 2: Manual Download

```bash
# Using Kaggle CLI
cd data/raw
kaggle competitions download -c ieee-fraud-detection
unzip ieee-fraud-detection.zip
```

## Verify Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/api/v1/health/detailed
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "database": {"status": "healthy"},
    "redis": {"status": "healthy"}
  }
}
```

### 2. Check Celery Worker

```bash
# Check Flower dashboard
open http://localhost:5555

# Or check worker status
celery -A workers inspect active
```

### 3. Test Dataset Processing

```bash
# Trigger preprocessing (after dataset download)
curl -X POST http://localhost:8000/api/v1/datasets/{dataset_id}/preprocess \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Common Issues & Solutions

### Issue: Kaggle API Authentication Failed

**Solution**: Verify your `kaggle.json` file:
```bash
cat ~/.kaggle/kaggle.json
# Should show: {"username":"your_username","key":"your_key"}
```

### Issue: Database Connection Error

**Solution**: Check PostgreSQL is running:
```bash
docker-compose ps postgres
# Or manually: pg_isready -h localhost -p 5432
```

### Issue: Redis Connection Error

**Solution**: Check Redis is running:
```bash
docker-compose ps redis
# Or manually: redis-cli ping
```

### Issue: Celery Worker Not Processing Tasks

**Solution**: Check worker logs:
```bash
docker-compose logs celery_worker
# Or manually: celery -A workers inspect active
```

### Issue: Port Already in Use

**Solution**: Stop conflicting services or change ports in `docker-compose.yml`

## Development Workflow

### 1. Make Code Changes

Edit files in `backend/app/` directory

### 2. Restart Services

```bash
# Restart specific service
docker-compose restart backend

# Or restart all
docker-compose restart
```

### 3. View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### 4. Run Tests

```bash
cd backend
pytest tests/ -v
```

## Supabase Setup

1. **Create a Supabase project** at https://supabase.com
2. **Get your credentials** from Project Settings → API
3. **Create storage buckets**:
   - `datasets` - for dataset files
   - `models` - for trained models
   - `explanations` - for explanation data
   - `reports` - for generated reports

4. **Update `.env`** with your Supabase credentials

## Next Steps

After successful setup:

1. ✅ **Register a researcher account** via API
2. ✅ **Download IEEE-CIS dataset** 
3. ✅ **Trigger preprocessing** to prepare data
4. ⏳ **Train models** (Phase 2 - in progress)
5. ⏳ **Generate explanations** (Phase 2 - in progress)
6. ⏳ **Access frontend** (Phase 3 - upcoming)

## Getting Help

- **Check logs**: `docker-compose logs -f`
- **API Documentation**: http://localhost:8000/api/v1/docs
- **Health Check**: http://localhost:8000/api/v1/health/detailed
- **Task Monitor**: http://localhost:5555

## Project Status

- ✅ **Phase 1**: Infrastructure & Scaffold - COMPLETED
- 🔄 **Phase 2**: Backend Core Development - IN PROGRESS
  - ✅ Dataset preprocessing utilities
  - ✅ Kaggle API integration
  - ✅ Dataset management endpoints
  - ⏳ Model training (next)
  - ⏳ XAI explanation generation (next)
- ⏳ **Phase 3**: Frontend Development
- ⏳ **Phase 4**: Human Study Module
- ⏳ **Phase 5**: Reporting & Deployment

---

**Ready to continue?** The platform is now set up and ready for Phase 2 development!
