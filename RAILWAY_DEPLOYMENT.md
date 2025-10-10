# 🚂 RAILWAY BACKEND DEPLOYMENT GUIDE

**Last Updated:** October 10, 2025

---

## ✅ CONFIGURATION FILES ADDED

I've added these files to your backend:

1. **`backend/railway.json`** - Railway configuration
2. **`backend/Procfile`** - Process file for deployment
3. **`backend/nixpacks.toml`** - Build configuration

These files are now on GitHub and Railway will detect them automatically! ✅

---

## 🚀 DEPLOY TO RAILWAY (5 MINUTES)

### Step 1: Create Railway Account

1. Go to: **https://railway.app/**
2. Click **"Start a New Project"**
3. Sign in with **GitHub**
4. Authorize Railway to access your repositories

### Step 2: Create New Project

1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Find and select: **`XAI_Platform_Master_Thesis`**
4. Railway will start detecting your project

### Step 3: Configure Root Directory

Railway might try to deploy the whole repo. You need to specify the backend folder:

1. Click on your service
2. Go to **Settings** tab
3. Find **"Root Directory"**
4. Set it to: **`backend`**
5. Click **"Save"**

### Step 4: Add Environment Variables

1. Go to **Variables** tab
2. Click **"+ New Variable"**
3. Add these variables:

```bash
# Supabase Configuration
SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co

SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptcXRobnptcGZoY3pxemdicWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwNzU4NzcsImV4cCI6MjA3NTY1MTg3N30.oySQp9Kf6wbN_OtABiEDcZQcw6koywjX_EfbKGE66Cc

# Get this from Supabase Dashboard → Settings → API → service_role key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# CORS - Add your Netlify domain
ALLOWED_ORIGINS=https://your-site.netlify.app,http://localhost:3000
```

### Step 5: Deploy

1. Railway will automatically start deploying
2. Wait 2-3 minutes for build to complete
3. Check **Deployments** tab for progress
4. Once deployed, you'll see a green checkmark ✅

### Step 6: Get Your Backend URL

1. Go to **Settings** tab
2. Find **"Domains"** section
3. Click **"Generate Domain"**
4. Copy the URL (e.g., `https://your-app.up.railway.app`)

### Step 7: Update Netlify

1. Go to **Netlify Dashboard**
2. Go to **Site settings** → **Environment variables**
3. Update `NEXT_PUBLIC_API_URL`:
   ```
   https://your-app.up.railway.app/api/v1
   ```
4. Go to **Deploys** tab
5. Click **"Trigger deploy"** → **"Deploy site"**

---

## 🔍 TROUBLESHOOTING

### Build Failed?

**Check these:**

1. **Root Directory** is set to `backend`
2. **Environment variables** are added
3. **requirements.txt** exists in backend folder
4. Check **Deploy Logs** for specific errors

### Can't Access API?

1. Make sure domain is generated
2. Check if deployment is successful (green checkmark)
3. Visit: `https://your-app.railway.app/docs` (should show FastAPI docs)
4. Check CORS settings in backend

### Port Issues?

Railway automatically sets `$PORT` environment variable. The configuration files I created use this correctly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 📋 ENVIRONMENT VARIABLES CHECKLIST

Make sure you add ALL of these to Railway:

- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_ANON_KEY`
- [ ] `SUPABASE_SERVICE_ROLE_KEY`
- [ ] `ALLOWED_ORIGINS`

---

## 🎯 AFTER DEPLOYMENT

### Test Your Backend

1. **Visit API docs:**
   ```
   https://your-app.railway.app/docs
   ```

2. **Test health endpoint:**
   ```
   https://your-app.railway.app/api/v1/health
   ```

3. **Test datasets endpoint:**
   ```
   https://your-app.railway.app/api/v1/datasets
   ```

### Update Frontend

Once backend is working, update Netlify:

1. Set `NEXT_PUBLIC_API_URL` to your Railway URL
2. Redeploy Netlify site
3. Test the full flow

---

## 💰 PRICING

Railway offers:
- **Free tier:** $5 credit per month
- **Hobby plan:** $5/month for more resources
- **Pro plan:** $20/month for production apps

Your backend should fit in the free tier for development! ✅

---

## 🔄 AUTO-DEPLOY

Railway automatically redeploys when you push to GitHub:

```bash
git add .
git commit -m "Update backend"
git push origin main
# Railway automatically redeploys! 🚀
```

---

## 📊 MONITORING

Railway provides:
- **Deployment logs** - See build output
- **Application logs** - See runtime logs
- **Metrics** - CPU, memory, network usage
- **Alerts** - Get notified of issues

---

## 🎓 FOR YOUR THESIS

**Deployment Architecture:**

```
GitHub Repository
    ↓
Railway (Backend - FastAPI)
    ↓
Supabase (Database)
    ↑
Netlify (Frontend - Next.js)
```

**Key Points:**
- ✅ Cloud-native deployment
- ✅ Automatic CI/CD
- ✅ Scalable infrastructure
- ✅ Production-ready

---

## ✅ SUCCESS CHECKLIST

- [ ] Railway account created
- [ ] Project deployed from GitHub
- [ ] Root directory set to `backend`
- [ ] All environment variables added
- [ ] Deployment successful (green checkmark)
- [ ] Domain generated
- [ ] API docs accessible
- [ ] Netlify updated with Railway URL
- [ ] Frontend can reach backend
- [ ] Full flow tested

---

## 🚀 QUICK SUMMARY

1. **Go to:** https://railway.app/
2. **Deploy from GitHub:** Select your repo
3. **Set root directory:** `backend`
4. **Add environment variables:** Supabase credentials
5. **Generate domain:** Get your backend URL
6. **Update Netlify:** Set `NEXT_PUBLIC_API_URL`
7. **Test:** Visit your Netlify site

---

**Your backend will be live in 5 minutes! 🎉**

**Railway URL format:** `https://your-app.up.railway.app`

**Then update Netlify and you're done!** ✅
