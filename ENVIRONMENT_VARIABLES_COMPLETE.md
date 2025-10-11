# 🔐 COMPLETE ENVIRONMENT VARIABLES GUIDE

**All environment variables needed for your XAI Platform across all services**

---

## 📊 OVERVIEW

| Service | Variables Needed | Status |
|---------|------------------|--------|
| **Netlify (Frontend)** | 3 variables | ⏳ NEEDS SETUP |
| **Railway (Backend)** | 11 variables | ✅ ALREADY SET |
| **Supabase** | 0 variables | ✅ NO VARIABLES NEEDED |
| **Cloudflare R2** | 0 variables | ✅ NO VARIABLES NEEDED |

---

## 🌐 NETLIFY (FRONTEND) - 3 VARIABLES NEEDED

### **Where to add:**
Netlify Dashboard → Your Site → Site configuration → Environment variables

### **Variables:**

```bash
# 1. Backend API URL (REQUIRED)
NEXT_PUBLIC_API_URL=https://xaiplatformmasterthesis-production.up.railway.app/api/v1

# 2. Supabase URL (REQUIRED for auth)
NEXT_PUBLIC_SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co

# 3. Supabase Anon Key (REQUIRED for auth)
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptcXRobnptcGZoY3pxemdicWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwNzU4NzcsImV4cCI6MjA3NTY1MTg3N30.oySQp9Kf6wbN_OtABiEDcZQcw6koywjX_EfbKGE66Cc
```

### **Why needed:**
- `NEXT_PUBLIC_API_URL` → Frontend needs to know where backend is
- `NEXT_PUBLIC_SUPABASE_URL` → For user authentication
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` → For user authentication

### **After adding:**
Trigger new deploy: Deploys → Trigger deploy → Clear cache and deploy site

---

## 🚂 RAILWAY (BACKEND) - 11 VARIABLES

### **Where to add:**
Railway Dashboard → Your Service → Variables tab

### **Variables:**

```bash
# === SUPABASE (3 variables) ===
SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptcXRobnptcGZoY3pxemdicWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwNzU4NzcsImV4cCI6MjA3NTY1MTg3N30.oySQp9Kf6wbN_OtABiEDcZQcw6koywjX_EfbKGE66Cc
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptcXRobnptcGZoY3pxemdicWtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDA3NTg3NywiZXhwIjoyMDc1NjUxODc3fQ.sHLhWleTQ0CJiEz6SMUCd2zVCbHy5GtWRGjw-45CCV8

# === CLOUDFLARE R2 (5 variables) ===
R2_ACCOUNT_ID=ff9c5d15c3296ba6a3aa9a96d1163cfe
R2_ACCESS_KEY_ID=58df651c2650ad40980aee11b9537146
R2_SECRET_ACCESS_KEY=e28f2e1d94035dfd814b79159dcadf82a33b926fe1f481becd1a50da9d2caa18
R2_BUCKET_NAME=xai-platform-datasets
R2_ENDPOINT_URL=https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com

# === KAGGLE API (2 variables) ===
KAGGLE_USERNAME=jaakoob6
KAGGLE_KEY=20564917d23bed39607e4e27250fb5bb

# === OPTIONAL (1 variable) ===
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptcXRobnptcGZoY3pxemdicWtqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MDA3NTg3NywiZXhwIjoyMDc1NjUxODc3fQ.sHLhWleTQ0CJiEz6SMUCd2zVCbHy5GtWRGjw-45CCV8
# (Same as SUPABASE_SERVICE_KEY - legacy compatibility)
```

### **Status:**
✅ **ALL ALREADY SET** - You don't need to do anything here!

---

## 🗄️ SUPABASE - NO VARIABLES NEEDED

### **What you need to do:**
✅ Create database tables (run SQL)
✅ That's it!

### **No environment variables needed in Supabase itself**

The credentials are used BY your backend and frontend, not IN Supabase.

---

## ☁️ CLOUDFLARE R2 - NO VARIABLES NEEDED

### **What you need to do:**
✅ Create bucket: `xai-platform-datasets`
✅ Generate API tokens (already done)
✅ That's it!

### **No environment variables needed in Cloudflare itself**

The credentials are used BY your backend, not IN Cloudflare.

---

## 📋 COMPLETE CHECKLIST

### **✅ Already Done:**
- [x] Railway has all 11 variables
- [x] Supabase tables created
- [x] Cloudflare R2 bucket exists
- [x] Kaggle API credentials obtained

### **⏳ Still Needed:**
- [ ] **Add 3 variables to Netlify** ← THIS IS THE ONLY THING LEFT!

---

## 🎯 WHAT TO DO NOW

### **Step 1: Add Variables to Netlify**

1. Go to: https://app.netlify.com/sites/xai-working-project/configuration/env
2. Click "Add a variable"
3. Add these 3 variables:

```
NEXT_PUBLIC_API_URL=https://xaiplatformmasterthesis-production.up.railway.app/api/v1
NEXT_PUBLIC_SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImptcXRobnptcGZoY3pxemdicWtqIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAwNzU4NzcsImV4cCI6MjA3NTY1MTg3N30.oySQp9Kf6wbN_OtABiEDcZQcw6koywjX_EfbKGE66Cc
```

### **Step 2: Redeploy Netlify**

1. Go to: Deploys tab
2. Click "Trigger deploy"
3. Select "Clear cache and deploy site"
4. Wait 2-3 minutes

### **Step 3: Test**

1. Go to: https://xai-working-project.netlify.app/datasets
2. Hard refresh: Cmd/Ctrl + Shift + R
3. See 3 datasets!
4. Click "Process Dataset"
5. Watch real ML magic! ✨

---

## 🔍 HOW TO GET THESE VALUES

### **If you need to find them again:**

**Supabase:**
- Go to: https://supabase.com/dashboard/project/jmqthnzmpfhczqzgbqkj/settings/api
- Copy: URL, anon key, service_role key

**Cloudflare R2:**
- Go to: https://dash.cloudflare.com/ → R2
- Manage R2 API Tokens
- Copy: Account ID, Access Key, Secret Key

**Kaggle:**
- Go to: https://www.kaggle.com/settings/account
- API section → Create New Token
- Downloads kaggle.json with username and key

**Railway Backend URL:**
- Go to: Railway dashboard → Your service → Settings
- Copy the public domain

---

## 📊 VARIABLE SUMMARY TABLE

| Variable | Where to Add | Purpose | Status |
|----------|-------------|---------|--------|
| `NEXT_PUBLIC_API_URL` | Netlify | Frontend → Backend | ⏳ NEEDED |
| `NEXT_PUBLIC_SUPABASE_URL` | Netlify | Frontend auth | ⏳ NEEDED |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Netlify | Frontend auth | ⏳ NEEDED |
| `SUPABASE_URL` | Railway | Backend → Supabase | ✅ SET |
| `SUPABASE_ANON_KEY` | Railway | Backend auth | ✅ SET |
| `SUPABASE_SERVICE_KEY` | Railway | Backend admin | ✅ SET |
| `R2_ACCOUNT_ID` | Railway | Backend → R2 | ✅ SET |
| `R2_ACCESS_KEY_ID` | Railway | Backend → R2 | ✅ SET |
| `R2_SECRET_ACCESS_KEY` | Railway | Backend → R2 | ✅ SET |
| `R2_BUCKET_NAME` | Railway | Backend → R2 | ✅ SET |
| `R2_ENDPOINT_URL` | Railway | Backend → R2 | ✅ SET |
| `KAGGLE_USERNAME` | Railway | Download datasets | ✅ SET |
| `KAGGLE_KEY` | Railway | Download datasets | ✅ SET |

---

## 🎉 SUMMARY

**You only need to add 3 variables to Netlify!**

Everything else is already configured:
- ✅ Railway: 11 variables (done)
- ✅ Supabase: Tables created (done)
- ✅ Cloudflare: Bucket created (done)

**After adding to Netlify:**
- Your platform will be 100% functional
- Real dataset processing from Kaggle
- Real model training
- Real benchmarks
- No mock data anywhere!

---

**Add the 3 Netlify variables now and you're done!** 🚀
