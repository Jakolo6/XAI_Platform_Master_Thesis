# 🔍 SYSTEM HEALTH CHECK - XAI Platform

**Complete verification checklist for all platform components**

---

## 🎯 QUICK HEALTH CHECK COMMANDS

Run these commands to verify each component:

### **1. Backend API Health**
```bash
# Basic health check
curl https://xaiplatformmasterthesis-production.up.railway.app/health

# Expected: {"status":"healthy"}
```

### **2. Backend Root Endpoint**
```bash
# Check API info
curl https://xaiplatformmasterthesis-production.up.railway.app/

# Expected: {"name":"XAI Finance Benchmark Platform","version":"1.0.0","status":"running","docs":"/api/v1/docs"}
```

### **3. Datasets Endpoint**
```bash
# List datasets
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# Expected: Array of 3 datasets (ieee-cis-fraud, givemesomecredit, german-credit)
```

### **4. CORS Preflight Check**
```bash
# Test CORS headers
curl -X OPTIONS \
  -H "Origin: https://xai-working-project.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -i https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# Expected: access-control-allow-origin: https://xai-working-project.netlify.app
```

### **5. API Documentation**
```bash
# Check if docs are accessible
curl -I https://xaiplatformmasterthesis-production.up.railway.app/api/v1/docs

# Expected: 200 OK
```

---

## 📊 DETAILED COMPONENT CHECKLIST

### ✅ **1. RAILWAY BACKEND**

#### **Environment Variables:**
- [ ] `SUPABASE_URL` - Set and working
- [ ] `SUPABASE_ANON_KEY` - Set and working
- [ ] `SUPABASE_SERVICE_KEY` - Set and working
- [ ] `R2_ACCOUNT_ID` - Set
- [ ] `R2_ACCESS_KEY_ID` - Set
- [ ] `R2_SECRET_ACCESS_KEY` - Set
- [ ] `R2_BUCKET_NAME` - Set to `xai-platform-datasets`
- [ ] `R2_ENDPOINT_URL` - Set to your R2 endpoint
- [ ] `KAGGLE_USERNAME` - (Optional) For dataset downloads
- [ ] `KAGGLE_KEY` - (Optional) For dataset downloads

#### **Check Railway Logs:**
```
Look for these messages:
✅ "Starting application"
✅ "Supabase storage client initialized"
✅ "R2 storage client initialized" (if R2 configured)
✅ "Setting up CORS middleware origins_count=3"
✅ "Application startup complete"
✅ "Uvicorn running on http://0.0.0.0:8080"
```

#### **Test Commands:**
```bash
# 1. Health check
curl https://xaiplatformmasterthesis-production.up.railway.app/health

# 2. List datasets
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# 3. Get specific dataset
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ieee-cis-fraud

# 4. Check API docs
open https://xaiplatformmasterthesis-production.up.railway.app/api/v1/docs
```

---

### ✅ **2. NETLIFY FRONTEND**

#### **Environment Variables:**
- [ ] `NEXT_PUBLIC_API_URL` - Set to `https://xaiplatformmasterthesis-production.up.railway.app`
- [ ] `NEXT_PUBLIC_SUPABASE_URL` - Set to your Supabase URL
- [ ] `NEXT_PUBLIC_SUPABASE_ANON_KEY` - Set to your Supabase anon key

#### **Check Netlify Build Logs:**
```
Look for:
✅ Build succeeded
✅ No TypeScript errors
✅ No missing environment variables warnings
✅ Deploy succeeded
```

#### **Test Frontend:**
```bash
# 1. Homepage loads
open https://xai-working-project.netlify.app

# 2. Check console for errors (F12)
# Should see NO errors

# 3. Test navigation
# - Click "Datasets" → Should load 3 datasets
# - Click "Models" → Should show training UI
# - Click "Benchmarks" → Should show benchmarks page
```

---

### ✅ **3. SUPABASE**

#### **Database Tables:**
Check if these tables exist in Supabase dashboard:
- [ ] `datasets` - For dataset metadata
- [ ] `models` - For trained model metadata
- [ ] `experiments` - For experiment tracking
- [ ] `benchmarks` - For benchmark results

#### **Storage Buckets:**
Check if these buckets exist (optional, using R2 instead):
- [ ] `datasets` - For dataset files
- [ ] `models` - For model files
- [ ] `explanations` - For explanation files

#### **Authentication:**
- [ ] Email/Password auth enabled
- [ ] Test user can register
- [ ] Test user can login

#### **Test Supabase Connection:**
```bash
# From backend logs, look for:
✅ "Supabase storage client initialized"

# Test auth (in browser):
1. Go to https://xai-working-project.netlify.app/register
2. Register a new user
3. Check Supabase → Authentication → Users
4. Should see new user
```

---

### ✅ **4. CLOUDFLARE R2**

#### **Bucket Configuration:**
- [ ] Bucket name: `xai-platform-datasets`
- [ ] Bucket exists in Cloudflare dashboard
- [ ] API tokens created with Read & Write permissions

#### **Test R2 Connection:**
```bash
# From backend logs, look for:
✅ "R2 storage client initialized"

# Test upload (Python):
python3 << EOF
from backend.app.utils.r2_storage import r2_storage_client

# Test if R2 is available
print(f"R2 Available: {r2_storage_client.is_available()}")

# Try to list files
files = r2_storage_client.list_files()
print(f"Files in bucket: {len(files)}")
EOF
```

---

### ✅ **5. CORS CONFIGURATION**

#### **Test CORS Headers:**
```bash
# Test OPTIONS (preflight)
curl -X OPTIONS \
  -H "Origin: https://xai-working-project.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -i https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# Expected headers:
# access-control-allow-origin: https://xai-working-project.netlify.app
# access-control-allow-credentials: true
# access-control-allow-methods: DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT
```

```bash
# Test GET request
curl -H "Origin: https://xai-working-project.netlify.app" \
  -i https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# Expected headers:
# access-control-allow-origin: https://xai-working-project.netlify.app
# access-control-allow-credentials: true
```

---

### ✅ **6. API ENDPOINTS**

Test each endpoint:

#### **Datasets:**
```bash
# List all datasets
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# Get specific dataset
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ieee-cis-fraud

# Preprocess dataset (will fail without Kaggle API, but should return proper error)
curl -X POST https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ieee-cis-fraud/preprocess
```

#### **Models:**
```bash
# List models
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/models/

# Train model (will fail without processed data, but should return proper error)
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"dataset_id":"ieee-cis-fraud","model_type":"xgboost"}' \
  https://xaiplatformmasterthesis-production.up.railway.app/api/v1/models/train
```

#### **Benchmarks:**
```bash
# List benchmarks
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/benchmarks/
```

---

## 🧪 BROWSER TESTING CHECKLIST

### **1. Homepage**
- [ ] Loads without errors
- [ ] Hero section displays correctly
- [ ] Navigation works
- [ ] CTAs link to correct pages
- [ ] Animations work smoothly

### **2. Authentication**
- [ ] Register page loads
- [ ] Can create new account
- [ ] Login page loads
- [ ] Can login with credentials
- [ ] Redirects to dashboard after login
- [ ] Logout works

### **3. Dashboard**
- [ ] Loads after login
- [ ] Shows user info
- [ ] Quick actions work
- [ ] Navigation to other pages works

### **4. Datasets Page**
- [ ] Loads 3 datasets
- [ ] Dataset cards display correctly
- [ ] Click on dataset shows details
- [ ] "Process Dataset" button exists
- [ ] Shows proper error when clicked (expected)

### **5. Models Page**
- [ ] Training form displays
- [ ] Dataset dropdown works
- [ ] Model type selection works
- [ ] "Train Model" button exists
- [ ] Shows proper error when clicked (expected)

### **6. Benchmarks Page**
- [ ] Page loads
- [ ] Shows message about no benchmarks (expected)
- [ ] UI is responsive

---

## 🔍 COMMON ISSUES & SOLUTIONS

### **Issue 1: "Failed to load datasets"**
**Check:**
- [ ] Backend is running (Railway logs)
- [ ] CORS is configured correctly
- [ ] `NEXT_PUBLIC_API_URL` is set in Netlify
- [ ] Datasets endpoint returns data

**Fix:**
```bash
# Test backend directly
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/
```

---

### **Issue 2: CORS errors**
**Check:**
- [ ] Railway logs show "Setting up CORS middleware"
- [ ] Netlify domain is in CORS origins
- [ ] OPTIONS request returns CORS headers

**Fix:**
```bash
# Test CORS
curl -X OPTIONS -H "Origin: https://xai-working-project.netlify.app" -i \
  https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/
```

---

### **Issue 3: "Supabase credentials not configured"**
**Check:**
- [ ] `SUPABASE_URL` set in Railway
- [ ] `SUPABASE_ANON_KEY` set in Railway
- [ ] `SUPABASE_SERVICE_KEY` set in Railway (not SERVICE_ROLE_KEY)

**Fix:**
Add/rename variables in Railway dashboard.

---

### **Issue 4: "R2 not available"**
**Check:**
- [ ] All R2 variables set in Railway
- [ ] R2 credentials are correct
- [ ] R2 bucket exists

**Fix:**
Verify credentials in Cloudflare dashboard.

---

### **Issue 5: 500 errors on POST requests**
**Check:**
- [ ] Railway logs for actual error
- [ ] CORS headers present on error response
- [ ] Error message is descriptive

**Expected:**
- Dataset processing fails without Kaggle API (normal)
- Model training fails without processed data (normal)

---

## ✅ FINAL VERIFICATION SCRIPT

Run this complete test:

```bash
#!/bin/bash

echo "🔍 XAI Platform Health Check"
echo "=============================="

# 1. Backend Health
echo "1. Testing Backend Health..."
curl -s https://xaiplatformmasterthesis-production.up.railway.app/health | jq .

# 2. Datasets Endpoint
echo "2. Testing Datasets Endpoint..."
curl -s https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ | jq 'length'

# 3. CORS Check
echo "3. Testing CORS..."
curl -s -X OPTIONS \
  -H "Origin: https://xai-working-project.netlify.app" \
  -H "Access-Control-Request-Method: POST" \
  -i https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ \
  | grep -i "access-control-allow-origin"

# 4. Frontend Check
echo "4. Testing Frontend..."
curl -s -I https://xai-working-project.netlify.app | grep "HTTP"

echo "=============================="
echo "✅ Health Check Complete!"
```

---

## 📊 EXPECTED RESULTS

### **All Green ✅:**
- Backend: Running on Railway
- Frontend: Deployed on Netlify
- Supabase: Connected and initialized
- R2: Configured (optional)
- CORS: Working correctly
- API: All endpoints accessible
- Auth: Registration and login work

### **Expected Limitations ⚠️:**
- Dataset processing fails (no Kaggle API)
- Model training fails (no processed data)
- Benchmarks empty (no trained models)

**This is NORMAL for a demo/thesis!**

---

## 🎓 FOR YOUR THESIS DEFENSE

### **What to Demonstrate:**

1. **Architecture:**
   - Show Railway backend logs
   - Show Netlify deployment
   - Explain Supabase + R2 storage

2. **Functionality:**
   - Navigate through UI
   - Show datasets loading
   - Explain training workflow
   - Show error handling

3. **Technical Decisions:**
   - Why FastAPI (async, modern)
   - Why Next.js (SSR, performance)
   - Why R2 (cost-effective)
   - Why Supabase (BaaS, rapid dev)

---

## ✅ SUMMARY

**Run these 3 commands to verify everything:**

```bash
# 1. Backend health
curl https://xaiplatformmasterthesis-production.up.railway.app/health

# 2. Datasets loading
curl https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/

# 3. CORS working
curl -X OPTIONS -H "Origin: https://xai-working-project.netlify.app" -i \
  https://xaiplatformmasterthesis-production.up.railway.app/api/v1/datasets/ \
  | grep "access-control-allow-origin"
```

**If all 3 work, your platform is healthy!** ✅

---

**Need help with any specific component? Let me know!** 🚀
