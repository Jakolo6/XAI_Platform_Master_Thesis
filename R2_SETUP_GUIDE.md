# 🚀 CLOUDFLARE R2 SETUP GUIDE

**Quick Start Guide for R2 Integration**

---

## 📋 WHAT YOU NEED TO DO

### **Step 1: Get R2 Credentials from Cloudflare**

1. **Go to Cloudflare Dashboard:**
   - Visit: https://dash.cloudflare.com/
   - Login to your account

2. **Navigate to R2:**
   - Click "R2" in the left sidebar
   - You should see your bucket: `xai-platform-datasets`

3. **Create API Token:**
   - Click "Manage R2 API Tokens"
   - Click "Create API Token"
   - **Permissions:** Select "Object Read & Write"
   - **TTL:** Set to "Forever" or desired duration
   - Click "Create API Token"

4. **Copy Credentials:**
   You'll get:
   ```
   Access Key ID: xxxxxxxxxxxxxxxxxxxxx
   Secret Access Key: yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy
   ```
   **⚠️ IMPORTANT:** Save these immediately! Secret key is only shown once!

5. **Get Account ID:**
   - Still in R2 dashboard
   - Look for "Account ID" in the right sidebar
   - Copy it (format: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)

---

## 🔧 STEP 2: ADD TO RAILWAY

### **Railway Environment Variables:**

1. Go to Railway dashboard: https://railway.app/
2. Click on your backend service
3. Go to **"Variables"** tab
4. Click **"+ New Variable"**
5. Add these **5 variables**:

```bash
R2_ACCOUNT_ID=your-account-id-here
R2_ACCESS_KEY_ID=your-access-key-id-here
R2_SECRET_ACCESS_KEY=your-secret-access-key-here
R2_BUCKET_NAME=xai-platform-datasets
R2_ENDPOINT_URL=https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com
```

**Replace:**
- `your-account-id-here` → Your Cloudflare Account ID
- `your-access-key-id-here` → Your R2 Access Key ID
- `your-secret-access-key-here` → Your R2 Secret Access Key

6. Railway will **auto-redeploy** after adding variables

---

## 💻 STEP 3: ADD TO LOCAL .ENV (Optional)

For local development, add to `backend/.env`:

```bash
# Cloudflare R2 Storage
R2_ACCOUNT_ID=your-account-id-here
R2_ACCESS_KEY_ID=your-access-key-id-here
R2_SECRET_ACCESS_KEY=your-secret-access-key-here
R2_BUCKET_NAME=xai-platform-datasets
R2_ENDPOINT_URL=https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com
```

---

## ✅ WHAT'S ALREADY DONE

I've implemented:

1. ✅ **Added boto3 to requirements.txt**
   - S3-compatible library for R2

2. ✅ **Updated config.py**
   - Added R2 configuration settings
   - Your endpoint URL is pre-configured

3. ✅ **Created R2 Storage Client**
   - `backend/app/utils/r2_storage.py`
   - Full S3-compatible API
   - Upload, download, delete, list files
   - Presigned URLs for temporary access
   - Proper error handling and logging

---

## 🧪 HOW TO TEST

### **After adding credentials to Railway:**

1. **Check Railway Logs:**
   ```
   Look for: "R2 storage client initialized"
   ```

2. **Test Upload (Python):**
   ```python
   from app.utils.r2_storage import r2_storage_client
   
   # Upload a test file
   success = r2_storage_client.upload_file(
       local_path="test.txt",
       remote_path="test/test.txt"
   )
   print(f"Upload successful: {success}")
   ```

3. **Test Download:**
   ```python
   # Download the file
   success = r2_storage_client.download_file(
       remote_path="test/test.txt",
       local_path="downloaded_test.txt"
   )
   print(f"Download successful: {success}")
   ```

4. **List Files:**
   ```python
   # List all files
   files = r2_storage_client.list_files(prefix="test/")
   print(f"Found {len(files)} files")
   ```

---

## 📁 R2 BUCKET STRUCTURE

Your bucket will be organized like this:

```
xai-platform-datasets/
├── datasets/
│   ├── ieee-cis-fraud/
│   │   ├── raw/
│   │   │   └── train_transaction.csv
│   │   └── processed/
│   │       ├── train.parquet
│   │       ├── val.parquet
│   │       └── test.parquet
│   ├── givemesomecredit/
│   │   └── processed/
│   │       ├── train.parquet
│   │       ├── val.parquet
│   │       └── test.parquet
│   └── german-credit/
│       └── processed/
│           └── data.parquet
├── models/
│   ├── ieee-cis-fraud/
│   │   ├── xgboost_v1.pkl
│   │   ├── random_forest_v1.pkl
│   │   └── neural_net_v1.h5
│   └── givemesomecredit/
│       └── xgboost_v1.pkl
└── explanations/
    ├── ieee-cis-fraud/
    │   ├── shap_values.pkl
    │   └── lime_explanations.pkl
    └── givemesomecredit/
        └── shap_values.pkl
```

---

## 🔒 SECURITY NOTES

### **DO:**
- ✅ Keep credentials in environment variables
- ✅ Never commit credentials to Git
- ✅ Use separate tokens for dev/prod
- ✅ Rotate keys regularly

### **DON'T:**
- ❌ Hardcode credentials in code
- ❌ Share credentials publicly
- ❌ Use production keys in development
- ❌ Commit `.env` files

---

## 💡 USAGE EXAMPLES

### **Upload Dataset:**
```python
from app.utils.r2_storage import r2_storage_client

# After processing a dataset
r2_storage_client.upload_file(
    local_path="data/processed/ieee-cis-fraud/train.parquet",
    remote_path="datasets/ieee-cis-fraud/processed/train.parquet",
    content_type="application/parquet"
)
```

### **Upload Model:**
```python
# After training a model
r2_storage_client.upload_file(
    local_path="models/xgboost_model.pkl",
    remote_path="models/ieee-cis-fraud/xgboost_v1.pkl",
    metadata={
        "model_type": "xgboost",
        "dataset": "ieee-cis-fraud",
        "accuracy": "0.95"
    }
)
```

### **Download for Inference:**
```python
# Download model for predictions
r2_storage_client.download_file(
    remote_path="models/ieee-cis-fraud/xgboost_v1.pkl",
    local_path="/tmp/model.pkl"
)
```

### **Generate Temporary URL:**
```python
# Share dataset with collaborator (1 hour access)
url = r2_storage_client.generate_presigned_url(
    remote_path="datasets/ieee-cis-fraud/processed/train.parquet",
    expiration=3600  # 1 hour
)
print(f"Download URL: {url}")
```

---

## 🎓 FOR YOUR THESIS

### **What to Highlight:**

1. **Modern Cloud Architecture:**
   - Object storage for large files
   - S3-compatible API (industry standard)
   - Separation of data and metadata

2. **Cost Optimization:**
   - Zero egress fees (vs AWS S3)
   - Efficient for ML workloads
   - Scalable and predictable pricing

3. **Best Practices:**
   - Environment-based configuration
   - Secure credential management
   - Proper error handling and logging
   - Presigned URLs for secure sharing

---

## ✅ CHECKLIST

- [ ] Get R2 credentials from Cloudflare
- [ ] Add 5 environment variables to Railway
- [ ] Wait for Railway to redeploy (2-3 min)
- [ ] Check logs for "R2 storage client initialized"
- [ ] Test upload/download (optional)
- [ ] Update thesis documentation

---

## 🚀 NEXT STEPS

### **After Setup:**

1. **Dataset Processing will use R2:**
   - Processed datasets uploaded to R2
   - Metadata stored in Supabase
   - Files accessible via presigned URLs

2. **Model Training will use R2:**
   - Trained models uploaded to R2
   - Model metrics in Supabase
   - Easy model versioning

3. **Explanations will use R2:**
   - SHAP values stored in R2
   - LIME explanations in R2
   - Efficient retrieval for visualization

---

## 📞 TROUBLESHOOTING

### **"R2 not available" in logs:**
- Check if credentials are added to Railway
- Verify credentials are correct
- Check if boto3 is installed

### **"Failed to upload file to R2":**
- Check bucket name is correct
- Verify endpoint URL
- Check file permissions

### **"Access Denied":**
- Verify API token has Read & Write permissions
- Check if token is expired
- Regenerate token if needed

---

## 📚 RESOURCES

- **Cloudflare R2 Docs:** https://developers.cloudflare.com/r2/
- **boto3 Documentation:** https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
- **S3 API Reference:** https://docs.aws.amazon.com/AmazonS3/latest/API/Welcome.html

---

**That's it! Once you add the credentials to Railway, R2 will be fully integrated!** 🎉
