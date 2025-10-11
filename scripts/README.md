# Local Dataset Processing Scripts

Process large datasets locally (using your computer's RAM) and upload to cloud storage, bypassing Railway's memory limits.

---

## 🚀 Quick Start

### 1. Set Up Environment Variables

Create a `.env` file in the project root with your credentials:

```bash
# Copy from Railway environment variables
KAGGLE_USERNAME=your-username
KAGGLE_KEY=your-api-key

R2_ACCOUNT_ID=ff9c5d15c3296ba6a3aa9a96d1163cfe
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=xai-platform-datasets

SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

Or export them:

```bash
export KAGGLE_USERNAME=your-username
export KAGGLE_KEY=your-api-key
# ... etc
```

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Process a Dataset

```bash
# Process full IEEE-CIS dataset (590k rows, all features)
python scripts/process_dataset_local.py ieee-cis-fraud

# Process with sampling (faster, less memory)
python scripts/process_dataset_local.py ieee-cis-fraud --sample

# Process other datasets
python scripts/process_dataset_local.py givemesomecredit
python scripts/process_dataset_local.py german-credit
```

---

## 📊 What It Does

1. ✅ **Downloads** dataset from Kaggle
2. ✅ **Processes** data (cleaning, feature engineering, splitting)
3. ✅ **Uploads** to Cloudflare R2 storage
4. ✅ **Updates** Supabase metadata
5. ✅ **Ready** for model training and XAI analysis

---

## 💾 Memory Usage

### Full Dataset Mode (default)
- **IEEE-CIS**: ~3-4GB RAM, 590k samples, 433 features
- **Give Me Some Credit**: ~500MB RAM, 150k samples, 11 features
- **German Credit**: ~50MB RAM, 1k samples, 20 features

### Sampled Mode (`--sample`)
- **IEEE-CIS**: ~500MB RAM, 100k samples, 50 features
- Faster processing, still statistically significant

---

## 🎯 Benefits

### vs Railway Processing
- ✅ **No memory limits** - Use your computer's RAM
- ✅ **Full datasets** - Process all 590k rows
- ✅ **All features** - No feature reduction
- ✅ **Faster** - No container restarts

### vs Manual Upload
- ✅ **Automated** - One command does everything
- ✅ **Consistent** - Same preprocessing as platform
- ✅ **Metadata** - Supabase automatically updated
- ✅ **Validated** - Uses same loaders as backend

---

## 📁 Output

Files are uploaded to R2 at:
```
datasets/{dataset_id}/processed/
  ├── train.parquet
  ├── val.parquet
  └── test.parquet
```

Metadata is stored in Supabase `datasets` table:
- Status: `completed`
- Sample counts
- Feature counts
- Class balance
- R2 paths

---

## 🔍 Troubleshooting

### "Missing environment variables"
Make sure all required variables are set in `.env` or exported.

### "Kaggle credentials not found"
Check your `KAGGLE_USERNAME` and `KAGGLE_KEY` are correct.

### "Failed to upload to R2"
Verify your R2 credentials and bucket name.

### "Out of memory"
Use `--sample` flag to process with reduced memory usage.

---

## 🎓 Example Workflow

```bash
# 1. Process IEEE-CIS locally (full dataset)
python scripts/process_dataset_local.py ieee-cis-fraud

# 2. Go to frontend
open https://xai-working-project.netlify.app/datasets

# 3. Click "Refresh" - dataset shows as "completed"

# 4. Train a model on the dataset
# 5. Generate SHAP/LIME explanations
# 6. Run benchmarks
```

---

## 📝 Notes

- **One-time processing**: Once uploaded, you never need to process again
- **Railway stays lightweight**: Only serves API, no heavy processing
- **Full platform functionality**: Training, XAI, benchmarks all work normally
- **Reusable**: Process any dataset in the registry

---

## 🆘 Need Help?

Check the main documentation:
- `ENVIRONMENT_VARIABLES_COMPLETE.md` - All env vars explained
- `DEPLOYMENT_GUIDE.md` - Full deployment guide
- `SETUP_INSTRUCTIONS.md` - Initial setup

---

**Happy processing! 🚀**
