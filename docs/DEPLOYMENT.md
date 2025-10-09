# Deployment Guide

**Platform:** XAI Finance Benchmark  
**Frontend:** Netlify  
**Backend:** Render  
**Storage:** Supabase

---

## 🚀 Deployment Overview

### Architecture
```
Frontend (Netlify) → Backend (Render) → PostgreSQL (Render) + Redis (Render)
                   ↓
              Supabase Storage (Files, Backups)
```

### Services
1. **Frontend:** Next.js app on Netlify (auto-deploy from GitHub)
2. **Backend API:** FastAPI on Render (Docker container)
3. **Celery Workers:** Render background workers
4. **Database:** Render PostgreSQL or external provider
5. **Redis:** Render Redis or external provider
6. **Storage:** Supabase for file storage

---

## 📋 Pre-Deployment Checklist

### 1. Supabase Setup
- [ ] Create Supabase project at https://supabase.com
- [ ] Create storage buckets:
  - `datasets` - Public read, authenticated write
  - `models` - Private
  - `explanations` - Private
  - `reports` - Public read, authenticated write
- [ ] Get API credentials from Project Settings → API
- [ ] Configure CORS for your domains

### 2. GitHub Repository
- [ ] Push code to GitHub
- [ ] Set up branch protection for `main`
- [ ] Configure GitHub Actions secrets (see below)

### 3. Environment Variables
- [ ] Generate secure `JWT_SECRET_KEY`
- [ ] Configure all production URLs
- [ ] Set up monitoring credentials

---

## 🔧 Backend Deployment (Render)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Connect your repository

### Step 2: Create PostgreSQL Database
1. Dashboard → New → PostgreSQL
2. Name: `xai-finance-db`
3. Region: Choose closest to users
4. Plan: Starter ($7/month) or higher
5. Copy `Internal Database URL` for environment variables

### Step 3: Create Redis Instance
1. Dashboard → New → Redis
2. Name: `xai-finance-redis`
3. Region: Same as database
4. Plan: Starter ($10/month) or higher
5. Copy `Internal Redis URL`

### Step 4: Deploy Backend API
1. Dashboard → New → Web Service
2. Connect repository: `XAI_Platform_Master_Thesis`
3. Configuration:
   - **Name:** `xai-finance-backend`
   - **Region:** Same as database
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Docker
   - **Plan:** Standard ($25/month) or higher (need 2-4GB RAM)
   - **Docker Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. Environment Variables (add all from `.env.example`):
   ```
   DATABASE_URL={from_render_postgres}
   REDIS_URL={from_render_redis}
   JWT_SECRET_KEY={generate_secure_key}
   SUPABASE_URL={from_supabase}
   SUPABASE_ANON_KEY={from_supabase}
   SUPABASE_SERVICE_ROLE_KEY={from_supabase}
   KAGGLE_USERNAME=jaakoob6
   KAGGLE_KEY={your_kaggle_key}
   ENVIRONMENT=production
   DEBUG=false
   CORS_ORIGINS=https://your-app.netlify.app
   ```

5. Health Check Path: `/api/v1/health`

### Step 5: Deploy Celery Worker
1. Dashboard → New → Background Worker
2. Connect same repository
3. Configuration:
   - **Name:** `xai-finance-worker`
   - **Region:** Same as API
   - **Branch:** `main`
   - **Root Directory:** `backend`
   - **Runtime:** Docker
   - **Plan:** Standard ($25/month) or higher
   - **Docker Command:** `celery -A workers worker --loglevel=info --concurrency=2`

4. Environment Variables: Same as backend API

### Step 6: Deploy Celery Beat (Scheduler)
1. Dashboard → New → Background Worker
2. Configuration:
   - **Name:** `xai-finance-beat`
   - **Docker Command:** `celery -A workers beat --loglevel=info`
3. Environment Variables: Same as backend API

---

## 🌐 Frontend Deployment (Netlify)

### Step 1: Create Netlify Account
1. Go to https://www.netlify.com
2. Sign up with GitHub
3. Connect your repository

### Step 2: Configure Build Settings
1. Sites → Add new site → Import from Git
2. Connect repository: `XAI_Platform_Master_Thesis`
3. Configuration:
   - **Base directory:** `frontend`
   - **Build command:** `npm run build`
   - **Publish directory:** `frontend/.next`
   - **Branch:** `main`

### Step 3: Environment Variables
Add in Site Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://xai-finance-backend.onrender.com
NEXT_PUBLIC_SUPABASE_URL={from_supabase}
NEXT_PUBLIC_SUPABASE_ANON_KEY={from_supabase}
NEXT_PUBLIC_GA_MEASUREMENT_ID={from_google_analytics}
NODE_ENV=production
```

### Step 4: Configure Domain (Optional)
1. Site Settings → Domain Management
2. Add custom domain if available
3. Configure DNS records

---

## 🔐 Security Configuration

### Render Security
1. **Environment Variables:** Use Render's secret management
2. **Network:** Enable private networking between services
3. **SSL:** Automatic HTTPS with Let's Encrypt
4. **IP Allowlisting:** Configure if needed

### Netlify Security
1. **Headers:** Configure security headers in `netlify.toml`
2. **HTTPS:** Automatic SSL
3. **Deploy Previews:** Enable for PR testing

### Supabase Security
1. **RLS Policies:** Enable Row Level Security
2. **API Keys:** Use service role key only in backend
3. **CORS:** Configure allowed origins
4. **Bucket Policies:** Set proper access controls

---

## 📊 Monitoring & Logging

### Application Monitoring
1. **Render Logs:** Available in dashboard
2. **Structured Logging:** JSON logs with correlation IDs
3. **Error Tracking:** Consider Sentry integration
4. **Performance:** Monitor response times

### Infrastructure Monitoring
1. **Render Metrics:** CPU, memory, network usage
2. **Database:** Query performance, connection pool
3. **Redis:** Memory usage, cache hit rate
4. **Celery:** Task queue length, worker status

### Analytics
1. **Google Analytics 4:** Frontend user tracking
2. **API Metrics:** Request counts, response times
3. **Business Metrics:** Models trained, explanations generated

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

**Trigger:** Push to `main` or PR

**Steps:**
1. **Test:** Run unit and integration tests
2. **Security:** Bandit and safety scans
3. **Build:** Create Docker image
4. **Deploy:** Trigger Render deployment
5. **Verify:** Health check on deployed service

**Secrets Required:**
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password
- `RENDER_DEPLOY_HOOK` - Render deploy webhook URL
- `BACKEND_URL` - Production backend URL

### Deployment Flow
```
Code Push → GitHub → Tests Pass → Build Docker → Deploy to Render → Health Check
                                                ↓
                                          Netlify Auto-Deploy
```

---

## 🧪 Testing Environments

### Development
- **URL:** http://localhost:8000
- **Database:** Local PostgreSQL
- **Redis:** Local Redis
- **Storage:** Supabase dev project

### Staging (Optional)
- **URL:** https://xai-finance-backend-staging.onrender.com
- **Database:** Render PostgreSQL (separate)
- **Branch:** `develop`

### Production
- **URL:** https://xai-finance-backend.onrender.com
- **Database:** Render PostgreSQL
- **Branch:** `main`

---

## 📦 Backup Strategy

### Nightly Backups (Automated)
- **Schedule:** 2 AM UTC daily
- **Task:** `app.tasks.report_tasks.backup_data`
- **Destination:** Supabase storage
- **Retention:** 30 days

### Weekly Exports (Automated)
- **Schedule:** Sunday 3 AM UTC
- **Task:** `app.tasks.report_tasks.weekly_export`
- **Destination:** S3 bucket (configure separately)
- **Retention:** 6 months

### Manual Backups
```bash
# Database backup
render pg:backups:create xai-finance-db

# Download backup
render pg:backups:download xai-finance-db {backup_id}
```

---

## 🔍 Health Checks

### Render Health Checks
Configure in service settings:
- **Path:** `/api/v1/health`
- **Interval:** 30 seconds
- **Timeout:** 10 seconds
- **Threshold:** 3 failures

### Monitoring Endpoints
- `/api/v1/health` - Basic health
- `/api/v1/health/detailed` - Service health
- `/api/v1/health/readiness` - Kubernetes-style readiness
- `/api/v1/health/liveness` - Kubernetes-style liveness

---

## 🚨 Troubleshooting

### Backend Not Starting
1. Check Render logs
2. Verify environment variables
3. Check database connectivity
4. Verify Redis connectivity

### Database Connection Issues
1. Check `DATABASE_URL` format
2. Verify database is running
3. Check connection limits
4. Review firewall rules

### Celery Workers Not Processing
1. Check worker logs in Render
2. Verify Redis connection
3. Check task queue status
4. Restart worker service

### High Memory Usage
1. Monitor Render metrics
2. Reduce `SHAP_SAMPLE_SIZE`
3. Implement more aggressive caching
4. Scale up worker instance

---

## 💰 Cost Estimates

### Render (Monthly)
- **PostgreSQL:** $7 (Starter) - $50 (Standard)
- **Redis:** $10 (Starter) - $50 (Standard)
- **Backend API:** $25 (Standard 2GB) - $85 (Pro 4GB)
- **Celery Worker:** $25 (Standard 2GB)
- **Celery Beat:** $7 (Starter)
- **Total:** ~$74-$217/month

### Netlify
- **Starter:** Free (100GB bandwidth)
- **Pro:** $19/month (400GB bandwidth)

### Supabase
- **Free:** 500MB storage, 2GB bandwidth
- **Pro:** $25/month (8GB storage, 50GB bandwidth)

### Total Estimated Cost
- **Minimum:** ~$74/month (Render only, free tiers for others)
- **Recommended:** ~$120/month (Standard tiers)

---

## 🎯 Production Readiness Checklist

### Security
- [ ] All secrets in environment variables
- [ ] HTTPS enabled everywhere
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] SQL injection protection (SQLAlchemy ORM)
- [ ] XSS protection (FastAPI defaults)

### Performance
- [ ] Database indexes created
- [ ] Redis caching enabled
- [ ] GZip compression enabled
- [ ] Static assets on CDN
- [ ] Query optimization

### Monitoring
- [ ] Structured logging configured
- [ ] Error tracking setup
- [ ] Health checks enabled
- [ ] Metrics collection
- [ ] Alerting configured

### Compliance
- [ ] GDPR consent mechanism
- [ ] Data retention policies
- [ ] Audit logging
- [ ] Privacy policy
- [ ] Terms of service

### Documentation
- [ ] API documentation published
- [ ] User guide created
- [ ] Admin guide created
- [ ] Troubleshooting guide

---

## 🔗 Useful Links

### Render
- **Dashboard:** https://dashboard.render.com
- **Docs:** https://render.com/docs
- **Status:** https://status.render.com

### Netlify
- **Dashboard:** https://app.netlify.com
- **Docs:** https://docs.netlify.com
- **Status:** https://www.netlifystatus.com

### Supabase
- **Dashboard:** https://app.supabase.com
- **Docs:** https://supabase.com/docs
- **Status:** https://status.supabase.com

---

## 📝 Deployment Commands

### Deploy Backend to Render
```bash
# Automatic via GitHub push to main
git push origin main

# Or trigger manual deploy
curl -X POST {RENDER_DEPLOY_HOOK}
```

### Deploy Frontend to Netlify
```bash
# Automatic via GitHub push to main
git push origin main

# Or manual deploy
cd frontend
npm run build
netlify deploy --prod
```

### Run Database Migrations
```bash
# SSH into Render service
render shell xai-finance-backend

# Run migrations
alembic upgrade head
```

---

## 🎬 First Deployment Steps

1. **Setup Supabase:**
   - Create project
   - Create buckets
   - Get credentials

2. **Setup Render:**
   - Create PostgreSQL database
   - Create Redis instance
   - Deploy backend API
   - Deploy Celery worker
   - Deploy Celery beat

3. **Setup Netlify:**
   - Connect repository
   - Configure build settings
   - Add environment variables
   - Deploy

4. **Verify Deployment:**
   - Check backend health: `https://your-backend.onrender.com/api/v1/health`
   - Check frontend: `https://your-app.netlify.app`
   - Test API endpoints
   - Verify Celery tasks

5. **Initial Data Setup:**
   - Register admin account
   - Download IEEE-CIS dataset
   - Preprocess dataset
   - Train baseline models

---

**Status:** Deployment configuration complete, ready for production deployment after Phase 2-3 completion.
