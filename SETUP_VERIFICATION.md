# ✅ Setup Verification Checklist

**Purpose:** Verify that a new user can successfully set up and run the XAI Platform

---

## 📋 Pre-Setup Checklist

### Required Software:
- [ ] Docker Desktop installed (4.0+)
- [ ] Git installed (2.30+)
- [ ] Kaggle account created
- [ ] 8GB+ RAM available
- [ ] 10GB+ disk space free

### Required Accounts:
- [ ] Kaggle account with API credentials
- [ ] GitHub account (to clone repository)

---

## 🚀 Setup Process Verification

### Step 1: Clone Repository
```bash
git clone https://github.com/Jakolo6/XAI_Platform_Master_Thesis.git
cd XAI_Platform_Master_Thesis
```

**Verify:**
- [ ] Repository cloned successfully
- [ ] All files present (check with `ls`)
- [ ] README.md exists and is readable

### Step 2: Get Kaggle Credentials
1. [ ] Go to https://www.kaggle.com/settings
2. [ ] Click "Create New API Token"
3. [ ] Download `kaggle.json`
4. [ ] Move to `~/.kaggle/kaggle.json`
5. [ ] Set permissions: `chmod 600 ~/.kaggle/kaggle.json`

**Verify:**
```bash
cat ~/.kaggle/kaggle.json
# Should show: {"username":"...","key":"..."}
```

### Step 3: Configure Environment
```bash
cp .env.example .env
nano .env  # or your preferred editor
```

**Required changes in .env:**
- [ ] Set `KAGGLE_USERNAME` (from kaggle.json)
- [ ] Set `KAGGLE_KEY` (from kaggle.json)
- [ ] Generate `JWT_SECRET_KEY` (use: `openssl rand -hex 32`)
- [ ] Optionally change database password

**Verify:**
```bash
grep "KAGGLE_USERNAME" .env
grep "KAGGLE_KEY" .env
grep "JWT_SECRET_KEY" .env
# Should show your actual values (not placeholders)
```

### Step 4: Start Services
```bash
docker-compose up -d
```

**Verify:**
- [ ] All containers start successfully
- [ ] No error messages in output
- [ ] Check status: `docker-compose ps`

**Expected output:**
```
NAME                STATUS
xai_backend         Up
xai_celery_worker   Up
xai_frontend        Up
xai_postgres        Up
xai_redis           Up
```

### Step 5: Check Logs
```bash
docker-compose logs backend | tail -20
```

**Verify:**
- [ ] No critical errors
- [ ] Backend started successfully
- [ ] Database connection established
- [ ] Redis connection established

### Step 6: Access Platform
Open browser and test each URL:

- [ ] **Frontend:** http://localhost:3000 (should load)
- [ ] **Backend:** http://localhost:8000 (should show JSON)
- [ ] **API Docs:** http://localhost:8000/api/v1/docs (should load Swagger UI)
- [ ] **Health Check:** http://localhost:8000/api/v1/health (should return `{"status":"healthy"}`)

### Step 7: Login
1. [ ] Go to http://localhost:3000
2. [ ] Click "Login" or navigate to login page
3. [ ] Enter credentials:
   - Email: `researcher@xai.com`
   - Password: `research123`
4. [ ] Login successful
5. [ ] Dashboard loads

---

## 🧪 Functionality Tests

### Test 1: View Models
- [ ] Navigate to Models page
- [ ] See list of 6 trained models
- [ ] Models show metrics (AUC-ROC, etc.)
- [ ] Can click on a model to view details

### Test 2: Generate SHAP Explanation
- [ ] Click on XGBoost model
- [ ] Click "Generate SHAP Explanation"
- [ ] Wait for generation (~3 seconds)
- [ ] Explanation appears with feature importance chart
- [ ] Top features displayed

### Test 3: Generate LIME Explanation
- [ ] On model detail page
- [ ] Click "Generate LIME Explanation" (if available)
- [ ] Wait for generation (~5-10 minutes)
- [ ] LIME explanation appears
- [ ] Feature importance displayed

### Test 4: Compare Methods
- [ ] Click "Compare SHAP vs LIME" button
- [ ] Comparison page loads
- [ ] See side-by-side tables
- [ ] See comparison chart
- [ ] See agreement metrics

### Test 5: API Access
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"researcher@xai.com","password":"research123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Test API
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/models
```

**Verify:**
- [ ] Token received
- [ ] API returns model list
- [ ] No authentication errors

---

## 🐛 Common Issues & Solutions

### Issue 1: Docker containers won't start
**Solution:**
```bash
docker-compose down
docker system prune -a
docker-compose up -d
```

### Issue 2: Port already in use
**Solution:**
```bash
# Find process using port
lsof -i :8000
# Kill it
kill -9 <PID>
# Restart
docker-compose up -d
```

### Issue 3: Database connection failed
**Solution:**
```bash
docker-compose restart postgres
docker-compose logs postgres
```

### Issue 4: Kaggle download fails
**Solution:**
- Verify kaggle.json exists: `cat ~/.kaggle/kaggle.json`
- Check permissions: `ls -la ~/.kaggle/kaggle.json` (should be 600)
- Test Kaggle CLI: `kaggle competitions list`

### Issue 5: Frontend won't load
**Solution:**
```bash
docker-compose logs frontend
docker-compose restart frontend
```

---

## 📊 Success Criteria

### Minimum Working Setup:
- [x] All containers running
- [x] Frontend accessible
- [x] Backend API responding
- [x] Can login
- [x] Can view models
- [x] Can view dashboard

### Full Functionality:
- [x] Can generate SHAP explanations
- [x] Can generate LIME explanations
- [x] Can compare methods
- [x] API authentication works
- [x] All pages load correctly

---

## 📝 Documentation Verification

### Check these files exist and are helpful:
- [ ] README.md - Clear overview
- [ ] INSTALLATION.md - Detailed setup
- [ ] START_HERE.md - Quick guide
- [ ] QUICK_REFERENCE.md - Cheat sheet
- [ ] CONTRIBUTING.md - Dev guidelines
- [ ] .env.example - All variables documented

---

## 🎯 New User Experience Score

Rate each aspect (1-5):

- **Clarity of instructions:** ___/5
- **Ease of setup:** ___/5
- **Documentation quality:** ___/5
- **Error messages:** ___/5
- **Overall experience:** ___/5

**Total Score:** ___/25

**Target:** 20+/25 (Excellent)

---

## 💡 Improvements Needed

If any issues were encountered, document them here:

1. **Issue:** _______________
   **Solution:** _______________

2. **Issue:** _______________
   **Solution:** _______________

3. **Issue:** _______________
   **Solution:** _______________

---

## ✅ Final Verification

**Date Tested:** _______________  
**Tested By:** _______________  
**OS:** _______________  
**Docker Version:** _______________  

**Result:** 
- [ ] ✅ PASS - Everything works
- [ ] ⚠️ PARTIAL - Some issues
- [ ] ❌ FAIL - Major problems

**Notes:**
_______________________________________________
_______________________________________________
_______________________________________________

---

## 🎉 Completion

If all checks pass, the repository is:
- ✅ Ready for new users
- ✅ Ready for collaboration
- ✅ Ready for thesis committee
- ✅ Ready for publication

**Congratulations! The setup is verified!** 🎉

---

*Last Updated: October 9, 2025*
