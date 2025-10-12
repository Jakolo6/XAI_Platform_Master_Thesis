# 🔑 KAGGLE API SETUP

## ⚠️ REQUIRED FOR HOME CREDIT DATASET

The backend now has endpoints to download the Home Credit dataset from Kaggle, but you need to configure Kaggle API credentials first.

---

## 📝 STEP 1: GET KAGGLE API CREDENTIALS

1. **Go to:** https://www.kaggle.com/
2. **Sign in** to your Kaggle account
3. **Click** on your profile picture (top right)
4. **Select** "Settings"
5. **Scroll down** to "API" section
6. **Click** "Create New API Token"
7. **Download** `kaggle.json` file

---

## 🚀 STEP 2: CONFIGURE ON RAILWAY

Since your backend is deployed on Railway, you need to add the Kaggle credentials as environment variables:

### **Option A: Upload kaggle.json (Recommended)**

1. **Open** Railway dashboard
2. **Select** your backend service
3. **Go to** "Variables" tab
4. **Add** these variables from your `kaggle.json`:

```
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key
```

### **Option B: Create kaggle.json in container**

Add a build script to create the file:

```bash
mkdir -p ~/.kaggle
echo '{"username":"YOUR_USERNAME","key":"YOUR_KEY"}' > ~/.kaggle/kaggle.json
chmod 600 ~/.kaggle/kaggle.json
```

---

## 🔧 STEP 3: REDEPLOY BACKEND

After adding the environment variables:

1. **Railway** will auto-redeploy
2. **Or manually trigger** a redeploy
3. **Wait** for deployment to complete

---

## ✅ STEP 4: TEST

1. **Open:** https://xaiplatformmasterthesis-production.up.railway.app/datasets
2. **Click:** "Download Dataset" button
3. **Should work** now (no more 404 errors)

---

## 🧪 ALTERNATIVE: LOCAL TESTING

If you want to test locally first:

```bash
# 1. Create ~/.kaggle directory
mkdir -p ~/.kaggle

# 2. Copy your kaggle.json
cp /path/to/downloaded/kaggle.json ~/.kaggle/kaggle.json

# 3. Set permissions
chmod 600 ~/.kaggle/kaggle.json

# 4. Start backend locally
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 5. Test download endpoint
curl -X POST http://localhost:8000/api/v1/datasets/home-credit/download
```

---

## 📊 WHAT HAPPENS WHEN YOU DOWNLOAD

1. **Backend** connects to Kaggle API
2. **Downloads** `home-credit-default-risk.zip` (~200MB)
3. **Extracts** `application_train.csv` and other files
4. **Saves** to `backend/data/raw/home_credit/`

Then when you **preprocess**:

1. **Loads** `application_train.csv`
2. **Handles** missing values
3. **Encodes** categorical features
4. **Scales** numerical features
5. **Splits** into train/val/test (70/15/15)
6. **Saves** to `backend/data/processed/`
7. **Generates** EDA statistics
8. **Stores** metadata in Supabase

---

## ⚠️ IMPORTANT NOTES

### **Kaggle Competition Rules:**
- You must **accept the competition rules** on Kaggle first
- Go to: https://www.kaggle.com/c/home-credit-default-risk
- Click "Join Competition" or "I Understand and Accept"

### **File Size:**
- Dataset is ~200MB compressed
- ~1GB uncompressed
- Make sure Railway has enough storage

### **Processing Time:**
- Download: 2-5 minutes
- Preprocessing: 5-10 minutes (depending on server)

---

## 🐛 TROUBLESHOOTING

### **Error: "Kaggle API not configured"**
- Make sure `KAGGLE_USERNAME` and `KAGGLE_KEY` are set
- Check environment variables in Railway

### **Error: "403 Forbidden"**
- You haven't accepted the competition rules
- Go to Kaggle and join the competition

### **Error: "404 Not Found"**
- Competition name might be wrong
- Check: https://www.kaggle.com/c/home-credit-default-risk

### **Error: "Out of disk space"**
- Railway free tier has limited storage
- May need to upgrade plan

---

## ✅ VERIFICATION

After setup, you should see:

1. **No 404 errors** on /datasets page
2. **Download button works**
3. **Preprocessing completes**
4. **EDA statistics display**
5. **Checklist turns green** ✅

---

## 🎯 NEXT STEPS

Once Kaggle is configured and dataset is downloaded:

1. ✅ Dataset page works
2. ✅ Can train models (Chunk 2)
3. ✅ Can generate explanations (Chunk 3)
4. ✅ Full platform functional

**The backend code is ready - just needs Kaggle credentials!** 🚀
