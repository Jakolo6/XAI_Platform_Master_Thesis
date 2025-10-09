# 🧪 Test SHAP Feature - Quick Guide

**Time:** 5 minutes
**Goal:** Generate your first SHAP explanation!

---

## ✅ Pre-flight Check

### 1. Services Running?
```bash
# Check backend
curl http://localhost:8000/api/v1/health

# Check frontend
curl http://localhost:3000
```

### 2. Frontend Running?
Open: http://localhost:3000
Should see: Beautiful landing page

---

## 🚀 Step-by-Step Test

### Step 1: Login (30 seconds)
1. Go to http://localhost:3000
2. Click "Login" or "Dashboard"
3. Enter credentials:
   - Email: `researcher@xai.com`
   - Password: `research123`
4. Click "Sign In"
5. Should redirect to Dashboard

### Step 2: Navigate to Model (30 seconds)
1. On Dashboard, you'll see 6 model cards
2. Click on **"XGBoost Fraud Detector v1"** (fastest for testing)
3. Should see model detail page with:
   - Performance metrics cards
   - Performance chart
   - Detailed metrics table
   - Confusion matrix heatmap

### Step 3: Generate SHAP Explanation (30 seconds)
1. Scroll down to the actions section
2. Look for purple button: **"Generate SHAP Explanation"**
3. Click the button
4. Button changes to: "Generating..."
5. Wait 10-30 seconds (backend is processing)

### Step 4: View Results (2 minutes)
Once complete, you'll see:

#### Feature Importance Chart
- Horizontal bar chart
- Top 20 features
- Blue gradient colors
- Interactive tooltips

#### Summary Stats
- Total features: 452
- Top features shown: 20
- Samples analyzed: 1,000

#### Feature Importance Table
Shows features like:
1. **TransactionAmt** - Most important
2. **card1** - Card identifier
3. **addr1** - Address
4. **dist1** - Distance
5. **C1** - Count feature

### Step 5: Explore (2 minutes)
1. **Hover** over bars to see exact values
2. **Click** "Show All Features" to expand
3. **Scroll** through the feature list
4. **Take screenshots** for your thesis!

---

## 📸 Screenshots to Take

### For Your Thesis:
1. **Dashboard** - Model overview
2. **Model Detail** - Performance metrics
3. **Confusion Matrix** - Visual representation
4. **Feature Importance Chart** - SHAP results
5. **Feature Table** - Top contributing features

---

## 🐛 Troubleshooting

### Button is Disabled?
**Reason:** Model type not supported
**Solution:** Use XGBoost, CatBoost, LightGBM, or Random Forest

### "Generating..." Never Completes?
**Check:**
```bash
# Check Celery worker logs
docker-compose logs celery_worker

# Check if task is running
open http://localhost:5555
```

### Error Message Appears?
**Common issues:**
1. Model file not found - Re-train the model
2. Validation data missing - Check data/processed/
3. Memory error - Restart Celery worker

### Fix: Restart Services
```bash
# Restart backend
docker-compose restart celery_worker

# Refresh frontend
# Just refresh browser (Ctrl+R or Cmd+R)
```

---

## 🎯 What You Should See

### Feature Importance Chart:
```
TransactionAmt  ████████████████████ 0.2340
card1          ████████████████ 0.1870
addr1          ████████████ 0.1230
dist1          ██████████ 0.0980
C1             ████████ 0.0820
C2             ███████ 0.0750
...
```

### Key Insights:
- **TransactionAmt** is most important (23.4%)
- **Card identity** matters significantly (18.7%)
- **Location features** are relevant (12.3%)
- **Behavioral patterns** help detection (8.2%)

---

## ✅ Success Criteria

You've successfully tested SHAP if you can:
- ✅ Click "Generate SHAP Explanation"
- ✅ See "Generating..." state
- ✅ Wait for completion
- ✅ View feature importance chart
- ✅ See top 20 features
- ✅ Hover for tooltips
- ✅ Expand to see all features

---

## 🎓 For Your Thesis

### What to Document:
1. **Top 5 features** and their importance
2. **Feature categories** (transaction, card, location, etc.)
3. **Business interpretation** of results
4. **Comparison** across different models

### Example Analysis:
"SHAP analysis reveals that TransactionAmt (23.4% importance) is the strongest fraud indicator, followed by card identity (18.7%) and location features (12.3%). This aligns with domain knowledge that high-value transactions from unusual locations are fraud risk factors."

---

## 🚀 Next Steps After Testing

### If It Works:
1. ✅ Generate explanations for other models
2. ✅ Compare feature importance across models
3. ✅ Take screenshots for thesis
4. ✅ Document insights

### If You Want More:
1. ⏳ Implement human study module
2. ⏳ Add report generation
3. ⏳ Create additional visualizations

---

## 💡 Pro Tips

### Tip 1: Compare Models
Generate SHAP for multiple models to see:
- Which features each model prioritizes
- How feature importance differs
- Which model is most interpretable

### Tip 2: Document Everything
Take screenshots and notes:
- Feature rankings
- Importance values
- Visual charts
- Key insights

### Tip 3: Business Context
Relate features to business:
- TransactionAmt → Transaction value
- card1 → Card identity
- addr1 → Customer location
- dist1 → Distance from home

---

## 🎉 Ready to Test!

**Open http://localhost:3000 and start exploring!**

**Remember:**
1. Login first
2. Click XGBoost model
3. Generate SHAP explanation
4. View beautiful results!

**Good luck! 🚀🧠**
