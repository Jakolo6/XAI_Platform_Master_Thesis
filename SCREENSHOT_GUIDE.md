# 📸 Screenshot Capture Guide

**Goal:** Capture professional screenshots for thesis documentation  
**Time Required:** 1 hour  
**Priority:** 🔴 CRITICAL

---

## 🚀 Quick Start

### Step 1: Prepare Platform (5 minutes)

```bash
# 1. Start all services
cd /Users/jakob.lindner/Documents/XAI_Platform_Master_Thesis
docker-compose up -d

# 2. Wait for services to be ready
sleep 10

# 3. Open browser
open http://localhost:3000

# 4. Login
# Email: researcher@xai.com
# Password: research123
```

### Step 2: Navigate and Capture (45 minutes)

Follow the sequence below, capturing each screenshot.

---

## 📋 Screenshot Sequence

### Part 1: Platform Overview (10 minutes)

#### Screenshot 1: Login Page
**File:** `01_login_page.png`  
**URL:** http://localhost:3000/login  
**Actions:**
1. Navigate to login page
2. Ensure clean UI (no errors)
3. Capture full page
4. **Shortcut:** Cmd + Shift + 4

**What to Show:**
- Login form
- Platform branding
- Clean, professional appearance

---

#### Screenshot 2: Dashboard
**File:** `02_dashboard.png`  
**URL:** http://localhost:3000/dashboard  
**Actions:**
1. Login first
2. Navigate to dashboard
3. Wait for data to load
4. Capture full page

**What to Show:**
- Overview statistics
- Recent activity
- Navigation menu

---

#### Screenshot 3: Models List
**File:** `03_models_list.png`  
**URL:** http://localhost:3000/models  
**Actions:**
1. Navigate to models page
2. Ensure all 9 models visible
3. Capture full page

**What to Show:**
- All 6 model types
- Performance metrics
- Action buttons

---

### Part 2: Model Details (5 minutes)

#### Screenshot 4: Model Detail Page
**File:** `04_model_detail.png`  
**URL:** http://localhost:3000/models/[id]  
**Actions:**
1. Click on XGBoost model
2. Wait for page to load
3. Scroll to show full view
4. Capture

**What to Show:**
- Model name and type
- Performance metrics
- Action buttons (Generate SHAP, Generate LIME)

---

#### Screenshot 5: Model Metrics
**File:** `05_model_metrics.png`  
**URL:** Same as above  
**Actions:**
1. Scroll to metrics section
2. Ensure charts visible
3. Capture metrics area

**What to Show:**
- AUC-ROC score
- Precision, Recall, F1
- Confusion matrix

---

### Part 3: SHAP Explanations (10 minutes)

#### Screenshot 6: SHAP Generation
**File:** `06_shap_generation.png`  
**Actions:**
1. Click "Generate SHAP" button
2. Immediately capture (within 1 second)
3. Show loading state

**What to Show:**
- Button in loading state
- "Generating..." message

---

#### Screenshot 7: SHAP Results
**File:** `07_shap_results.png`  
**Actions:**
1. Wait for SHAP to complete (~5 seconds)
2. Scroll to show full chart
3. Capture

**What to Show:**
- Feature importance chart
- Top 20 features
- SHAP values
- Clear visualization

---

#### Screenshot 8: SHAP Top Features
**File:** `08_shap_top_features.png`  
**Actions:**
1. Focus on top features table
2. Capture table area

**What to Show:**
- Feature names
- SHAP values
- Rankings

---

### Part 4: LIME Explanations (15 minutes)

#### Screenshot 9: LIME Generation Start
**File:** `09_lime_generation.png`  
**Actions:**
1. Click "Generate LIME" button
2. Capture immediately

**What to Show:**
- Button clicked
- Progress indicator appearing

---

#### Screenshot 10: LIME Progress
**File:** `10_lime_progress.png`  
**Actions:**
1. Wait ~2 minutes
2. Capture progress bar at 40-60%

**What to Show:**
- Progress bar
- Time remaining
- Helpful tips
- Professional progress UI

---

#### Screenshot 11: LIME Results
**File:** `11_lime_results.png`  
**Actions:**
1. Wait for LIME to complete (~3-5 minutes)
2. Scroll to show full chart
3. Capture

**What to Show:**
- Feature importance chart
- Top 20 features
- LIME weights
- Clear visualization

---

#### Screenshot 12: LIME Top Features
**File:** `12_lime_top_features.png`  
**Actions:**
1. Focus on top features table
2. Capture table area

**What to Show:**
- Feature names
- LIME weights
- Rankings

---

### Part 5: Method Switcher (5 minutes)

#### Screenshot 13: Method Switcher
**File:** `13_method_switcher.png`  
**Actions:**
1. Ensure both SHAP and LIME complete
2. Focus on switcher UI
3. Capture

**What to Show:**
- Both buttons (SHAP 🔮 and LIME 🍋)
- "Both methods available" badge
- Clean UI

---

#### Screenshot 14: SHAP Selected
**File:** `14_shap_selected.png`  
**Actions:**
1. Click SHAP button
2. Capture with SHAP active

**What to Show:**
- SHAP button highlighted
- SHAP explanation visible

---

#### Screenshot 15: LIME Selected
**File:** `15_lime_selected.png`  
**Actions:**
1. Click LIME button
2. Capture with LIME active

**What to Show:**
- LIME button highlighted
- LIME explanation visible

---

#### Screenshot 16: Both Available
**File:** `16_both_available.png`  
**Actions:**
1. Show full switcher with badge
2. Capture

**What to Show:**
- Success indicator
- Professional UI

---

### Part 6: Comparison Dashboard (10 minutes)

#### Screenshot 17: Comparison Page
**File:** `17_comparison_page.png`  
**URL:** http://localhost:3000/models/[id]/compare  
**Actions:**
1. Click "Compare Methods" button
2. Wait for page to load
3. Capture full page

**What to Show:**
- Side-by-side comparison
- Agreement metrics
- Both visualizations

---

#### Screenshot 18: Side-by-Side
**File:** `18_side_by_side.png`  
**Actions:**
1. Focus on comparison tables
2. Capture both columns

**What to Show:**
- SHAP top 10
- LIME top 10
- Highlighting common features

---

#### Screenshot 19: Agreement Metrics
**File:** `19_agreement_metrics.png`  
**Actions:**
1. Scroll to metrics section
2. Capture

**What to Show:**
- Top-10 overlap: 40%
- Spearman correlation: 0.617
- Statistical metrics

---

#### Screenshot 20: Correlation Chart
**File:** `20_correlation_chart.png`  
**Actions:**
1. Focus on visualization
2. Capture chart

**What to Show:**
- Correlation visualization
- Clear labels

---

### Part 7: Quality Metrics (5 minutes)

#### Screenshot 21: Quality Metrics
**File:** `21_quality_metrics.png`  
**Actions:**
1. Navigate to quality metrics section
2. Capture

**What to Show:**
- Faithfulness: 0.85
- Robustness: 0.92
- Complexity: 0.73

---

## 🎨 Post-Processing

### After Capturing All Screenshots

1. **Review Quality**
   ```bash
   cd screenshots/
   open .
   # Review each screenshot
   ```

2. **Check Resolution**
   ```bash
   # Should be >1920x1080
   file *.png
   ```

3. **Optimize File Size**
   ```bash
   # Optional: compress without quality loss
   # Use ImageOptim or similar tool
   ```

4. **Add Annotations** (if needed)
   - Use Preview or Skitch
   - Add arrows to highlight features
   - Add text labels for clarity

---

## ✅ Quality Checklist

Before marking complete:
- [ ] All screenshots captured
- [ ] High resolution (>1920px width)
- [ ] Clear and readable text
- [ ] No personal information visible
- [ ] Professional appearance
- [ ] Consistent styling
- [ ] Properly named
- [ ] Saved in PNG format
- [ ] No browser chrome (unless needed)
- [ ] Focused on relevant content

---

## 📊 Expected Results

After completion, you should have:
- **29 screenshots** total
- **~50-100 MB** total size
- **Professional quality** for thesis
- **Ready to use** in documentation

---

## 🚨 Troubleshooting

### Issue: Platform Not Running
```bash
docker-compose up -d
sleep 10
```

### Issue: No Data Visible
```bash
# Check if models exist
curl http://localhost:8000/api/v1/models

# Re-run data seeding if needed
docker-compose exec backend python -m app.scripts.seed_data
```

### Issue: SHAP/LIME Not Generating
```bash
# Check Celery worker
docker-compose logs celery_worker

# Restart if needed
docker-compose restart celery_worker
```

---

## 📝 Notes

### Tips for Best Results
1. Use **light mode** for better printing
2. **Full screen** browser for maximum space
3. **Hide bookmarks bar** for cleaner look
4. **Zoom to 100%** for consistency
5. **Wait for animations** to complete

### For Thesis
- Reference screenshots in text
- Add figure captions
- Number figures sequentially
- Explain what each shows

---

## 🎯 Success Criteria

**Complete when:**
- ✅ All 29 screenshots captured
- ✅ Quality checked
- ✅ Files properly named
- ✅ Saved in screenshots/ directory
- ✅ Ready for thesis inclusion

---

**Time Budget:** 1 hour  
**Priority:** HIGH  
**Status:** Ready to start  

**Start capturing now!** 📸
