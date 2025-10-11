# 🚀 CLOUDFLARE R2 INTEGRATION PLAN

**Date:** October 11, 2025  
**Objective:** Integrate Cloudflare R2 for dataset and model file storage

---

## 📋 OVERVIEW

### **What is Cloudflare R2?**
- S3-compatible object storage
- Zero egress fees (unlike AWS S3)
- Perfect for large datasets and model files
- Your bucket: `xai-platform-datasets`

### **Why R2 Instead of Supabase Storage?**
- ✅ Better for large files (datasets can be 500MB+)
- ✅ S3-compatible API (industry standard)
- ✅ No egress fees (cost-effective)
- ✅ Better performance for ML workloads
- ✅ Keep Supabase for metadata only

---

## 🎯 ARCHITECTURE CHANGE

### **Before:**
```
Datasets → Local Storage (Railway) → Supabase Storage
Models → Local Storage (Railway) → Supabase Storage
Metadata → Supabase Database
```

### **After:**
```
Datasets → Cloudflare R2 (S3-compatible)
Models → Cloudflare R2 (S3-compatible)
Metadata → Supabase Database (unchanged)
```

---

## 📦 WHAT NEEDS TO CHANGE

### 1. **Dependencies** ✅
- Install `boto3` (AWS S3 SDK, works with R2)
- Add to `requirements.txt`

### 2. **Configuration** ✅
- Add R2 credentials to config
- Add R2 endpoint URL
- Add bucket name

### 3. **Storage Client** ✅
- Create new `R2StorageClient` class
- Implement S3-compatible operations
- Keep Supabase client for backward compatibility

### 4. **Dataset Processing** ✅
- Upload processed datasets to R2
- Download from R2 when needed
- Store metadata in Supabase

### 5. **Model Storage** ✅
- Save trained models to R2
- Load models from R2 for inference
- Store model metadata in Supabase

### 6. **Environment Variables** ✅
- Add to Railway dashboard
- Add to local `.env` for development

---

## 🔧 IMPLEMENTATION STEPS

### **Step 1: Get R2 Credentials**

You need these from Cloudflare:

1. **Account ID** - From R2 dashboard
2. **Access Key ID** - Create in R2 API tokens
3. **Secret Access Key** - Generated with Access Key
4. **Bucket Name** - `xai-platform-datasets`
5. **Endpoint URL** - Your provided URL

**Your R2 Endpoint:**
```
https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com
```

---

### **Step 2: Install boto3**

```bash
cd backend
pip install boto3
```

Add to `requirements.txt`:
```
boto3>=1.28.0
```

---

### **Step 3: Update Configuration**

Add to `backend/app/core/config.py`:

```python
# Cloudflare R2 Storage
R2_ACCOUNT_ID: str = ""
R2_ACCESS_KEY_ID: str = ""
R2_SECRET_ACCESS_KEY: str = ""
R2_BUCKET_NAME: str = "xai-platform-datasets"
R2_ENDPOINT_URL: str = "https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com"
R2_PUBLIC_URL: str = ""  # If you set up public access
```

---

### **Step 4: Create R2 Storage Client**

Create `backend/app/utils/r2_storage.py`:

```python
import boto3
from botocore.client import Config
from pathlib import Path
import structlog

class R2StorageClient:
    """Cloudflare R2 storage client (S3-compatible)."""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=settings.R2_ENDPOINT_URL,
            aws_access_key_id=settings.R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        self.bucket = settings.R2_BUCKET_NAME
    
    def upload_file(self, local_path: str, remote_path: str):
        """Upload file to R2."""
        self.client.upload_file(local_path, self.bucket, remote_path)
    
    def download_file(self, remote_path: str, local_path: str):
        """Download file from R2."""
        Path(local_path).parent.mkdir(parents=True, exist_ok=True)
        self.client.download_file(self.bucket, remote_path, local_path)
    
    def delete_file(self, remote_path: str):
        """Delete file from R2."""
        self.client.delete_object(Bucket=self.bucket, Key=remote_path)
    
    def list_files(self, prefix: str = ""):
        """List files in R2 bucket."""
        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=prefix
        )
        return response.get('Contents', [])
```

---

### **Step 5: Update Dataset Processing**

Modify dataset processing to use R2:

```python
# After processing dataset locally
r2_client = R2StorageClient()

# Upload processed files
r2_client.upload_file(
    local_path="data/processed/ieee-cis-fraud/train.parquet",
    remote_path="datasets/ieee-cis-fraud/train.parquet"
)

# Store metadata in Supabase
supabase.table('datasets').insert({
    'id': 'ieee-cis-fraud',
    'r2_path': 'datasets/ieee-cis-fraud/',
    'status': 'processed',
    'size_mb': 250,
    'processed_at': datetime.now()
})
```

---

### **Step 6: Update Model Storage**

Save trained models to R2:

```python
# After training model
r2_client = R2StorageClient()

# Upload model file
r2_client.upload_file(
    local_path="models/ieee-cis-fraud_xgboost.pkl",
    remote_path="models/ieee-cis-fraud/xgboost_v1.pkl"
)

# Store metadata in Supabase
supabase.table('models').insert({
    'id': model_id,
    'r2_path': 'models/ieee-cis-fraud/xgboost_v1.pkl',
    'accuracy': 0.95,
    'trained_at': datetime.now()
})
```

---

### **Step 7: Environment Variables**

#### **Local Development (`backend/.env`):**
```bash
# Cloudflare R2
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=xai-platform-datasets
R2_ENDPOINT_URL=https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com
```

#### **Railway Dashboard:**
Add these variables in Railway → Variables tab:
```
R2_ACCOUNT_ID=your-account-id
R2_ACCESS_KEY_ID=your-access-key-id
R2_SECRET_ACCESS_KEY=your-secret-access-key
R2_BUCKET_NAME=xai-platform-datasets
R2_ENDPOINT_URL=https://ff9c5d15c3296ba6a3aa9a96d1163cfe.r2.cloudflarestorage.com
```

---

## 📁 FILE STRUCTURE IN R2

```
xai-platform-datasets/
├── datasets/
│   ├── ieee-cis-fraud/
│   │   ├── raw/
│   │   │   ├── train_transaction.csv
│   │   │   └── train_identity.csv
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
│       ├── xgboost_v1.pkl
│       └── logistic_regression_v1.pkl
└── explanations/
    ├── ieee-cis-fraud/
    │   ├── shap_values.pkl
    │   └── lime_explanations.pkl
    └── givemesomecredit/
        └── shap_values.pkl
```

---

## 🔒 SECURITY BEST PRACTICES

### **1. Access Keys**
- ✅ Never commit to Git
- ✅ Use environment variables
- ✅ Rotate keys regularly
- ✅ Use separate keys for dev/prod

### **2. Bucket Permissions**
- ✅ Private by default
- ✅ Use signed URLs for temporary access
- ✅ Enable CORS for frontend access (if needed)

### **3. Cost Management**
- ✅ Monitor storage usage
- ✅ Set up lifecycle policies
- ✅ Delete old/unused files

---

## 📊 BENEFITS OF R2 INTEGRATION

### **Performance:**
- ✅ Faster uploads/downloads than Supabase
- ✅ Better for large files (500MB+ datasets)
- ✅ Parallel uploads/downloads

### **Cost:**
- ✅ Zero egress fees (vs AWS S3)
- ✅ Cheaper storage than Supabase
- ✅ Predictable pricing

### **Scalability:**
- ✅ Unlimited storage
- ✅ High throughput
- ✅ Global CDN

### **Compatibility:**
- ✅ S3-compatible API
- ✅ Works with existing tools (boto3, AWS CLI)
- ✅ Easy migration

---

## 🎓 FOR YOUR THESIS

### **What to Highlight:**

1. **Cloud-Native Storage**
   - Modern object storage solution
   - S3-compatible API (industry standard)
   - Separation of concerns (data vs metadata)

2. **Cost Optimization**
   - Zero egress fees
   - Efficient for ML workloads
   - Scalable architecture

3. **Best Practices**
   - Environment-based configuration
   - Secure credential management
   - Proper error handling

---

## ✅ IMPLEMENTATION CHECKLIST

- [ ] Install boto3
- [ ] Get R2 credentials from Cloudflare
- [ ] Update config.py with R2 settings
- [ ] Create r2_storage.py client
- [ ] Update dataset processing to use R2
- [ ] Update model storage to use R2
- [ ] Add R2 variables to Railway
- [ ] Test upload/download operations
- [ ] Update documentation
- [ ] Deploy to production

---

## 🚀 NEXT STEPS

1. **Get R2 Credentials** (from Cloudflare dashboard)
2. **I'll implement the code changes**
3. **You add credentials to Railway**
4. **Test with one dataset**
5. **Deploy and verify**

---

## 📝 NOTES

- Keep Supabase for metadata (dataset info, model metrics)
- Use R2 for large files (datasets, models, explanations)
- This is the industry-standard approach for ML platforms
- Shows understanding of cloud architecture in your thesis

---

**Ready to implement? Let me know and I'll start with the code changes!** 🚀
