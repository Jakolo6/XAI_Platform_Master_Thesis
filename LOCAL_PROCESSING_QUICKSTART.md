# 🚀 Local Dataset Processing - Quick Start Guide

Process large datasets on your computer and upload to the cloud!

---

## ⚡ 3-Step Setup

### Step 1: Create `.env` File

Create a file called `.env` in the project root:

```bash
# Kaggle (get from https://www.kaggle.com/settings/account)
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key

# Cloudflare R2 (copy from Railway)
R2_ACCOUNT_ID=ff9c5d15c3296ba6a3aa9a96d1163cfe
R2_ACCESS_KEY_ID=58df651c2650ad40980aee11b9537xxx
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET_NAME=xai-platform-datasets

# Supabase (copy from Railway)
SUPABASE_URL=https://jmqthnzmpfhczqzgbqkj.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

**💡 Tip:** Copy these values from your Railway environment variables!

---

### Step 2: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

---

### Step 3: Run the Script

```bash
# Process IEEE-CIS Fraud dataset (full 590k rows)
python scripts/process_dataset_local.py ieee-cis-fraud
```

**That's it!** ✨

---

## 📊 What You'll See

```
============================================================
🚀 LOCAL DATASET PROCESSING
============================================================
Dataset: ieee-cis-fraud
Mode: FULL DATASET
============================================================

📋 Step 1: Loading dataset configuration...
✅ Configuration loaded for: IEEE-CIS Fraud Detection

📝 Step 2: Updating status to 'processing'...
✅ Status updated in Supabase

📁 Step 3: Creating temporary directory...
✅ Temp directory: /tmp/ieee-cis-fraud_abc123

⬇️  Step 4: Downloading from Kaggle...
   Competition: ieee-fraud-detection
   [████████████████████] 100% - 118MB
✅ Download complete!

🔄 Step 5: Loading and preprocessing data...
   📊 Processing FULL dataset (no sampling)
   Loading transaction data...
   ✅ Loaded 590,540 transaction rows
   Loading identity data...
   ✅ Loaded 144,233 identity rows
   Merging datasets...
   ✅ Raw data loaded: 590,540 rows, 433 columns
   Preprocessing...
   ✅ Preprocessing complete: 50 features

✂️  Step 6: Splitting into train/val/test...
   ✅ Train: 413,378 samples
   ✅ Val:   88,581 samples
   ✅ Test:  88,581 samples

💾 Step 7: Saving to parquet files...
✅ Files saved locally

☁️  Step 8: Uploading to R2 storage...
   Uploading train.parquet...
   Uploading val.parquet...
   Uploading test.parquet...
✅ All files uploaded to R2!

📊 Step 9: Calculating statistics...
   Total samples: 590,540
   Features: 50
   Class balance: {'0': 569877, '1': 20663}

💾 Step 10: Updating Supabase metadata...
✅ Supabase updated successfully!

============================================================
🎉 SUCCESS! Dataset processing complete!
============================================================

✅ Dataset 'ieee-cis-fraud' is now ready for:
   - Model training
   - XAI analysis (SHAP, LIME)
   - Benchmarking

View it at: https://xai-working-project.netlify.app/datasets
```

---

## ⏱️ Processing Time

| Dataset | Rows | Time | Memory |
|---------|------|------|--------|
| **IEEE-CIS Fraud** | 590k | ~5-10 min | 3-4GB |
| **Give Me Some Credit** | 150k | ~2-3 min | 500MB |
| **German Credit** | 1k | ~30 sec | 50MB |

---

## 🎯 After Processing

1. **Go to frontend:** https://xai-working-project.netlify.app/datasets
2. **Click "Refresh"** button
3. **Dataset shows as "completed"** with full stats
4. **Start training models!**

---

## 🔧 Other Commands

```bash
# Process with sampling (faster, less memory)
python scripts/process_dataset_local.py ieee-cis-fraud --sample

# Process other datasets
python scripts/process_dataset_local.py givemesomecredit
python scripts/process_dataset_local.py german-credit

# Get help
python scripts/process_dataset_local.py --help
```

---

## ❓ Troubleshooting

### "Missing environment variables"
- Make sure `.env` file exists in project root
- Check all variables are set (no typos!)

### "Kaggle authentication failed"
- Go to https://www.kaggle.com/settings/account
- Create new API token
- Update `KAGGLE_USERNAME` and `KAGGLE_KEY`

### "R2 upload failed"
- Verify R2 credentials in Railway match your `.env`
- Check bucket name is correct

### "Out of memory"
- Use `--sample` flag
- Close other applications
- Or upgrade your RAM 😄

---

## 💡 Pro Tips

1. **Process once, use forever** - Uploaded datasets never need reprocessing
2. **Railway stays light** - Only serves API, no heavy processing
3. **Full platform works** - Training, XAI, benchmarks all use uploaded data
4. **Process multiple datasets** - Run script for each dataset you need

---

## 📚 More Info

- **Full documentation:** `scripts/README.md`
- **Environment variables:** `ENVIRONMENT_VARIABLES_COMPLETE.md`
- **Deployment guide:** `DEPLOYMENT_GUIDE.md`

---

**Ready to process? Run the command and watch the magic! ✨**

```bash
python scripts/process_dataset_local.py ieee-cis-fraud
```
