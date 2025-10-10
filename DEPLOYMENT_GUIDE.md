# 🚀 DEPLOYMENT GUIDE - GitHub & Netlify

**Last Updated:** October 10, 2025

---

## 📋 OVERVIEW

This guide will help you:
1. Push your code to GitHub
2. Deploy frontend to Netlify
3. Deploy backend (optional)
4. Configure environment variables

---

## 🔐 BEFORE YOU PUSH

### 1. Check Sensitive Files Are Ignored

Run this to verify:
```bash
git status
```

**Make sure these are NOT listed:**
- ❌ `.env` files
- ❌ `backend/data/` directory
- ❌ `node_modules/`
- ❌ API keys or credentials

**If they appear, they're in `.gitignore` ✅**

### 2. Remove Any Committed Secrets (if any)

```bash
# Check for accidentally committed secrets
git log --all --full-history -- "*/.env"

# If found, remove from history (careful!)
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch backend/.env" \
  --prune-empty --tag-name-filter cat -- --all
```

---

## 📤 STEP 1: PUSH TO GITHUB

### Option A: New Repository

```bash
# Navigate to project
cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis

# Initialize git (if not already)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: XAI Platform v1.0 - Multi-dataset research platform"

# Create repository on GitHub
# Go to: https://github.com/new
# Name: XAI_Platform_Master_Thesis
# Don't initialize with README (you have one)

# Add remote
git remote add origin https://github.com/Jakolo6/XAI_Platform_Master_Thesis.git

# Push
git branch -M main
git push -u origin main
```

### Option B: Existing Repository

```bash
# Add changes
git add .

# Commit
git commit -m "feat: Complete multi-dataset platform with Supabase integration"

# Push
git push origin main
```

---

## 🌐 STEP 2: DEPLOY FRONTEND TO NETLIFY

### Method 1: Netlify Dashboard (Recommended)

1. **Go to Netlify**
   ```
   https://app.netlify.com/
   ```

2. **Click "Add new site" → "Import an existing project"**

3. **Connect to GitHub**
   - Authorize Netlify
   - Select your repository: `XAI_Platform_Master_Thesis`

4. **Configure Build Settings**
   ```
   Base directory: frontend
   Build command: npm run build
   Publish directory: frontend/.next
   ```

5. **Add Environment Variables**
   - Go to: Site settings → Environment variables
   - Add:
     ```
     NEXT_PUBLIC_API_URL = https://your-backend-url.com/api/v1
     ```
   - (For now, use: `http://localhost:8000/api/v1` for testing)

6. **Deploy**
   - Click "Deploy site"
   - Wait 2-3 minutes
   - Your site will be live at: `https://random-name.netlify.app`

7. **Custom Domain (Optional)**
   - Go to: Site settings → Domain management
   - Add custom domain
   - Follow DNS instructions

### Method 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy from frontend directory
cd frontend
netlify deploy --prod

# Follow prompts:
# - Create new site or link existing
# - Build command: npm run build
# - Publish directory: .next
```

---

## 🖥️ STEP 3: DEPLOY BACKEND (OPTIONS)

### Option A: Railway (Recommended)

1. **Go to Railway**
   ```
   https://railway.app/
   ```

2. **New Project → Deploy from GitHub**
   - Select your repository
   - Select `backend` directory

3. **Add Environment Variables**
   - Add all from `backend/.env.example`
   - Use your actual Supabase credentials

4. **Deploy**
   - Railway will auto-deploy
   - Get your URL: `https://your-app.railway.app`

5. **Update Netlify Environment**
   - Go back to Netlify
   - Update `NEXT_PUBLIC_API_URL` to Railway URL

### Option B: Render

1. **Go to Render**
   ```
   https://render.com/
   ```

2. **New Web Service**
   - Connect GitHub
   - Select repository
   - Root directory: `backend`

3. **Configure**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

4. **Add Environment Variables**
   - Same as Railway

### Option C: Keep Backend Local (For Development)

```bash
# Run backend locally
cd backend
uvicorn app.main:app --reload

# Use ngrok for public URL (temporary)
ngrok http 8000

# Update Netlify with ngrok URL
NEXT_PUBLIC_API_URL=https://abc123.ngrok.io/api/v1
```

---

## ⚙️ STEP 4: CONFIGURE ENVIRONMENT VARIABLES

### Backend Environment Variables

**On Railway/Render, add these:**

```bash
# Supabase (Required)
SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# Kaggle (Required for dataset download)
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-key

# Application
ENVIRONMENT=production
DEBUG=false

# CORS (Important!)
BACKEND_CORS_ORIGINS=["https://your-netlify-app.netlify.app"]
```

### Frontend Environment Variables

**On Netlify, add:**

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app/api/v1
```

---

## 🔒 SECURITY CHECKLIST

Before deploying:

- [ ] All `.env` files in `.gitignore`
- [ ] No API keys in code
- [ ] CORS configured correctly
- [ ] Supabase RLS policies enabled
- [ ] JWT secret is strong and random
- [ ] Debug mode off in production
- [ ] HTTPS enabled (automatic on Netlify/Railway)

---

## 🧪 TESTING DEPLOYMENT

### 1. Test Frontend

```bash
# Visit your Netlify URL
https://your-app.netlify.app

# Check pages:
- / (home)
- /datasets
- /models/train
- /benchmarks
```

### 2. Test Backend

```bash
# Health check
curl https://your-backend.railway.app/api/v1/health

# Datasets endpoint
curl https://your-backend.railway.app/api/v1/datasets/
```

### 3. Test Integration

```bash
# Open browser console on Netlify site
# Check for API calls in Network tab
# Verify data loads from backend
```

---

## 🐛 TROUBLESHOOTING

### Frontend Issues

**Build fails on Netlify:**
```bash
# Check build logs
# Common issues:
- Missing dependencies → npm install
- TypeScript errors → fix in code
- Environment variables → add in Netlify
```

**API calls fail:**
```bash
# Check CORS settings in backend
# Verify NEXT_PUBLIC_API_URL is correct
# Check browser console for errors
```

### Backend Issues

**Deployment fails:**
```bash
# Check requirements.txt is complete
# Verify Python version (3.11+)
# Check environment variables
```

**Database connection fails:**
```bash
# Verify Supabase credentials
# Check Supabase project is active
# Test connection locally first
```

---

## 📊 DEPLOYMENT COSTS

### Free Tier Limits

**Netlify (Frontend):**
- ✅ 100 GB bandwidth/month
- ✅ 300 build minutes/month
- ✅ Automatic HTTPS
- ✅ Custom domain
- **Cost:** FREE

**Railway (Backend):**
- ✅ $5 free credit/month
- ✅ ~500 hours runtime
- ✅ Automatic HTTPS
- **Cost:** FREE (with credit)

**Supabase (Database):**
- ✅ 500 MB database
- ✅ 1 GB file storage
- ✅ 2 GB bandwidth
- **Cost:** FREE

**Total:** $0/month for small projects ✅

---

## 🚀 QUICK DEPLOYMENT COMMANDS

```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy: Production-ready platform"
git push origin main

# 2. Deploy Frontend (Netlify CLI)
cd frontend
netlify deploy --prod

# 3. Deploy Backend (Railway CLI)
cd backend
railway up

# 4. Test
curl https://your-app.netlify.app
curl https://your-backend.railway.app/api/v1/health
```

---

## 📝 POST-DEPLOYMENT CHECKLIST

- [ ] Frontend accessible at Netlify URL
- [ ] Backend accessible at Railway URL
- [ ] API calls work from frontend
- [ ] Datasets load correctly
- [ ] Training workflow works
- [ ] Benchmarks display
- [ ] No console errors
- [ ] HTTPS working
- [ ] Custom domain configured (optional)
- [ ] README updated with live URLs

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

1. **Update README** with live URLs
2. **Test all features** on production
3. **Monitor logs** for errors
4. **Set up analytics** (optional)
5. **Share with advisor** for feedback
6. **Add to thesis** as live demo

---

## 💡 TIPS

### For Thesis Demo
- Use custom domain for professional look
- Add screenshots of live site
- Include live URL in thesis
- Record video demo

### For Open Source
- Add "Deploy to Netlify" button in README
- Document deployment process
- Provide example environment variables
- Include troubleshooting guide

---

## 📞 SUPPORT

**If deployment fails:**
1. Check build logs carefully
2. Verify all environment variables
3. Test locally first
4. Check service status pages
5. Review this guide again

**Common Resources:**
- Netlify Docs: https://docs.netlify.com
- Railway Docs: https://docs.railway.app
- Supabase Docs: https://supabase.com/docs

---

**Ready to deploy? Follow the steps above!** 🚀

**Estimated time: 15-30 minutes**
