# 📖 XAI Platform User Guide

**Version:** 1.0.0  
**Last Updated:** October 9, 2025  
**Target Audience:** Researchers, Data Scientists, ML Engineers

---

## 📚 Table of Contents

1. [Getting Started](#getting-started)
2. [Understanding the Dashboard](#understanding-the-dashboard)
3. [Generating Explanations](#generating-explanations)
4. [Comparing Methods](#comparing-methods)
5. [Interpreting Results](#interpreting-results)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)
8. [FAQ](#faq)

---

## 🚀 Getting Started

### First Time Setup

1. **Access the Platform**
   ```
   URL: http://localhost:3000
   ```

2. **Login Credentials**
   ```
   Email: researcher@xai.com
   Password: research123
   ```

3. **Navigate to Models**
   - Click "Models" in the navigation bar
   - You'll see 6 pre-trained fraud detection models

### Platform Overview

The XAI Platform provides:
- ✅ **6 ML Models** (XGBoost, LightGBM, CatBoost, Random Forest, Logistic Regression, Neural Network)
- ✅ **2 XAI Methods** (SHAP and LIME)
- ✅ **Comparison Tools** (Side-by-side analysis)
- ✅ **Quality Metrics** (Quantus evaluation)

---

## 📊 Understanding the Dashboard

### Main Dashboard

When you open the platform, you'll see:

```
┌─────────────────────────────────────────┐
│  XAI Finance Platform                   │
├─────────────────────────────────────────┤
│  📊 Models Overview                     │
│  ┌─────────┬─────────┬─────────┐       │
│  │ XGBoost │ LightGBM│ CatBoost│       │
│  │ 94.3%   │ 93.8%   │ 93.5%   │       │
│  └─────────┴─────────┴─────────┘       │
│                                         │
│  🔍 Recent Explanations                 │
│  • SHAP - XGBoost (2 min ago)          │
│  • LIME - LightGBM (5 min ago)         │
└─────────────────────────────────────────┘
```

### Model Card

Each model shows:
- **Model Name** (e.g., "XGBoost Classifier")
- **Performance Metrics** (AUC-ROC, Precision, Recall)
- **Training Date**
- **Status** (Ready, Training, Error)
- **Actions** (View Details, Generate Explanation)

---

## 🔬 Generating Explanations

### Step 1: Select a Model

1. Navigate to the Models page
2. Click on any model card (e.g., "XGBoost Classifier")
3. You'll see the model detail page

### Step 2: Generate SHAP Explanation

**SHAP (SHapley Additive exPlanations)** provides global feature importance.

**Steps:**
1. Click the **"Generate SHAP"** button
2. Wait ~3-5 seconds
3. View the feature importance chart

**What You'll See:**
```
Feature Importance (SHAP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
C13              ████████████ 0.258
TransactionAmt   ██████████   0.220
C1               █████████    0.210
C14              █████████    0.203
V70              ████████     0.161
```

**Interpretation:**
- **Bars:** Longer = more important
- **Values:** SHAP importance score (0-1)
- **Color:** Blue = positive impact, Red = negative impact

### Step 3: Generate LIME Explanation

**LIME (Local Interpretable Model-agnostic Explanations)** provides local interpretability.

**Steps:**
1. Click the **"Generate LIME"** button
2. Monitor the progress bar (3-5 minutes)
3. View the feature importance chart

**Progress Indicator:**
```
🔬 LIME Explanation Generation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LIME generation in progress... (2/5 min, ~3 min remaining)
[████████████░░░░░░░░] 60%

• LIME analyzes 200 samples with perturbations
• This process takes approximately 3-5 minutes ⚡
• You can leave this page and come back later
• Progress is saved automatically ✓
```

**What You'll See:**
```
Feature Importance (LIME)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
V339             ████████████ 0.245
C13              ███████████  0.198
TransactionAmt   ██████████   0.187
card1            █████████    0.165
V258             ████████     0.142
```

### Step 4: Switch Between Methods

Once both are generated, you'll see the **Method Switcher**:

```
┌─────────────────────────────────────┐
│ View Explanation:                   │
│ [🔮 SHAP] [🍋 LIME]                 │
│ ✓ Both methods available            │
└─────────────────────────────────────┘
```

**Usage:**
- Click **🔮 SHAP** to view SHAP explanation
- Click **🍋 LIME** to view LIME explanation
- Switch instantly between methods
- Active button is highlighted

---

## 🔄 Comparing Methods

### Step 1: Navigate to Comparison

1. Generate both SHAP and LIME explanations
2. Click **"Compare Methods"** button
3. View the comparison dashboard

### Step 2: Understand the Comparison

The comparison page shows:

#### **Side-by-Side Feature Rankings**

```
┌──────────────────┬──────────────────┐
│ SHAP Top 10      │ LIME Top 10      │
├──────────────────┼──────────────────┤
│ 1. C13 (0.258)   │ 1. V339 (0.245)  │
│ 2. TransAmt      │ 2. C13 (0.198)   │
│ 3. C1            │ 3. TransAmt      │
│ 4. C14           │ 4. card1         │
│ 5. V70           │ 5. V258          │
└──────────────────┴──────────────────┘
```

#### **Agreement Metrics**

```
📊 Method Agreement Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Top-10 Overlap:     40% (4 features)
Top-20 Overlap:     55% (11 features)
Spearman Corr:      0.617
Kendall Tau:        0.524
```

**Interpretation:**
- **40% overlap** = 4 out of 10 features agree
- **0.617 correlation** = Moderate positive agreement
- **Higher is better** = More method consistency

#### **Quality Metrics**

```
🎯 Explanation Quality (Quantus)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           SHAP    LIME
Faithfulness  0.85    0.78
Robustness    0.92    0.81
Complexity    0.73    0.68
```

**Interpretation:**
- **Faithfulness:** How accurate is the explanation? (higher = better)
- **Robustness:** How stable across perturbations? (higher = better)
- **Complexity:** How simple is the explanation? (higher = simpler)

---

## 🧠 Interpreting Results

### Understanding SHAP Values

**What is SHAP?**
- Based on game theory (Shapley values)
- Shows each feature's contribution to prediction
- Global importance across all predictions

**How to Read:**
```
Feature: C13
SHAP Value: 0.258
Meaning: C13 contributes 25.8% to fraud detection
```

**Key Insights:**
- **Positive SHAP** = Increases fraud probability
- **Negative SHAP** = Decreases fraud probability
- **Magnitude** = Importance strength

### Understanding LIME Values

**What is LIME?**
- Local linear approximation
- Explains individual predictions
- Shows feature impact for specific instances

**How to Read:**
```
Feature: V339
LIME Weight: 0.245
Meaning: V339 has 24.5% local importance
```

**Key Insights:**
- **Positive weight** = Pushes toward fraud
- **Negative weight** = Pushes toward legitimate
- **Magnitude** = Local importance

### When to Use Which Method?

| Use Case | Recommended Method |
|----------|-------------------|
| **Global Understanding** | SHAP |
| **Model Debugging** | SHAP |
| **Feature Selection** | SHAP |
| **Individual Cases** | LIME |
| **Local Interpretability** | LIME |
| **Quick Explanations** | LIME |
| **Comprehensive Analysis** | Both (Compare) |

---

## ✅ Best Practices

### 1. Generate Both Methods

**Why?**
- SHAP and LIME provide complementary insights
- Comparison reveals method biases
- Increases confidence in findings

**How?**
```
1. Generate SHAP first (faster)
2. Generate LIME second (slower)
3. Compare results
4. Document findings
```

### 2. Check Quality Metrics

**Why?**
- Validates explanation reliability
- Identifies potential issues
- Ensures trustworthy insights

**What to Look For:**
- Faithfulness > 0.7 ✅
- Robustness > 0.7 ✅
- Complexity > 0.6 ✅

### 3. Document Your Findings

**Template:**
```markdown
## Explanation Analysis

**Model:** XGBoost Classifier
**Date:** October 9, 2025

### SHAP Results:
- Top Feature: C13 (0.258)
- Key Insight: Transaction characteristics dominate

### LIME Results:
- Top Feature: V339 (0.245)
- Key Insight: Velocity features important locally

### Agreement:
- Overlap: 40%
- Correlation: 0.617
- Conclusion: Methods partially agree

### Quality:
- Faithfulness: 0.85 (SHAP), 0.78 (LIME)
- Recommendation: Both methods reliable
```

### 4. Iterate and Refine

**Process:**
1. Generate initial explanations
2. Analyze disagreements
3. Investigate surprising features
4. Validate with domain knowledge
5. Refine model if needed

---

## 🔧 Troubleshooting

### Issue 1: SHAP Generation Fails

**Symptoms:**
- Error message appears
- No feature importance shown
- Button stays disabled

**Solutions:**
1. **Check model status**
   ```
   Status should be "Ready"
   If "Training" or "Error", wait or retrain
   ```

2. **Refresh the page**
   ```
   Press F5 or Cmd+R
   Try generating again
   ```

3. **Check logs**
   ```bash
   docker-compose logs backend | grep SHAP
   ```

### Issue 2: LIME Takes Too Long

**Symptoms:**
- Progress bar stuck
- Timeout message appears
- No results after 5 minutes

**Solutions:**
1. **Wait longer**
   ```
   LIME can take 3-5 minutes
   Check if still "processing"
   ```

2. **Check Celery worker**
   ```bash
   docker-compose logs celery_worker | tail -50
   ```

3. **Restart worker**
   ```bash
   docker-compose restart celery_worker
   ```

### Issue 3: Comparison Page Empty

**Symptoms:**
- No data shown
- "Generate explanations first" message
- Empty charts

**Solutions:**
1. **Generate both methods**
   ```
   Must have BOTH SHAP and LIME
   Check model detail page
   ```

2. **Verify completion**
   ```
   Both should show "✓ Complete"
   No "pending" or "failed" status
   ```

3. **Clear cache**
   ```
   Refresh page (F5)
   Log out and log back in
   ```

### Issue 4: Method Switcher Not Appearing

**Symptoms:**
- Can't toggle between SHAP/LIME
- Only one method shown
- Switcher missing

**Solutions:**
1. **Generate both methods**
   ```
   Switcher only appears when both exist
   Check if both completed successfully
   ```

2. **Refresh page**
   ```
   Press F5 to reload
   Switcher should appear
   ```

---

## ❓ FAQ

### Q1: How long does SHAP take?

**A:** SHAP typically completes in **3-5 seconds** for most models.

### Q2: How long does LIME take?

**A:** LIME takes **3-5 minutes** as it analyzes 200 samples with perturbations.

### Q3: Can I leave the page during LIME generation?

**A:** Yes! LIME runs in the background. You can:
- Close the browser
- Navigate to other pages
- Come back later to check results

### Q4: Which method is more accurate?

**A:** Both are accurate but serve different purposes:
- **SHAP:** Better for global understanding
- **LIME:** Better for local interpretability
- **Best:** Use both and compare!

### Q5: What if methods disagree?

**A:** Disagreement is normal and informative:
- **40% agreement** is typical
- Shows different perspectives
- Investigate disagreements for insights
- Use domain knowledge to validate

### Q6: How do I export results?

**A:** Currently, you can:
- Take screenshots (Cmd+Shift+4 on Mac)
- Copy data from tables
- Export functionality coming soon!

### Q7: Can I use my own models?

**A:** Not yet, but planned for future release:
- Model upload interface
- Custom dataset support
- API integration

### Q8: What are the system requirements?

**A:** Minimum requirements:
- **RAM:** 8GB (16GB recommended)
- **CPU:** 4 cores
- **Storage:** 10GB free space
- **Browser:** Chrome, Firefox, Safari (latest)

### Q9: Is my data secure?

**A:** Yes:
- All data processed locally
- No external API calls
- Docker isolation
- No data leaves your machine

### Q10: How do I cite this platform?

**A:** Use this format:
```
Lindner, J. (2025). XAI Platform for Financial Fraud Detection: 
A Comparative Analysis of SHAP and LIME. Master's Thesis, 
[Your University]. GitHub: github.com/Jakolo6/XAI_Platform_Master_Thesis
```

---

## 📞 Support

### Need Help?

1. **Check Documentation**
   - START_HERE.md
   - QUICK_REFERENCE.md
   - SETUP_VERIFICATION.md

2. **Check Logs**
   ```bash
   docker-compose logs backend
   docker-compose logs celery_worker
   ```

3. **GitHub Issues**
   - Report bugs
   - Request features
   - Ask questions

4. **Contact**
   - Email: [your-email]
   - GitHub: @Jakolo6

---

## 🎓 Learning Resources

### Recommended Reading:

1. **SHAP**
   - Original Paper: Lundberg & Lee (2017)
   - Documentation: shap.readthedocs.io
   - Tutorial: shap-tutorial.readthedocs.io

2. **LIME**
   - Original Paper: Ribeiro et al. (2016)
   - Documentation: lime-ml.readthedocs.io
   - Tutorial: marcotcr.github.io/lime

3. **Quantus**
   - Documentation: quantus.readthedocs.io
   - Paper: Hedström et al. (2023)

### Video Tutorials:

1. **XAI Fundamentals** (YouTube)
2. **SHAP in Practice** (Coursera)
3. **LIME Explained** (DataCamp)

---

## 🎯 Quick Reference Card

```
┌─────────────────────────────────────────┐
│  XAI Platform Quick Reference           │
├─────────────────────────────────────────┤
│  Login:                                 │
│  • Email: researcher@xai.com            │
│  • Password: research123                │
│                                         │
│  Generate Explanations:                 │
│  1. Select model                        │
│  2. Click "Generate SHAP" (~3 sec)      │
│  3. Click "Generate LIME" (~3-5 min)    │
│  4. Use switcher to toggle              │
│                                         │
│  Compare Methods:                       │
│  1. Generate both SHAP & LIME           │
│  2. Click "Compare Methods"             │
│  3. View side-by-side analysis          │
│                                         │
│  Interpret Results:                     │
│  • Higher value = More important        │
│  • Positive = Increases fraud prob      │
│  • Negative = Decreases fraud prob      │
│                                         │
│  Troubleshooting:                       │
│  • Refresh page (F5)                    │
│  • Check logs (docker-compose logs)     │
│  • Restart worker if needed             │
└─────────────────────────────────────────┘
```

---

## 📝 Changelog

### Version 1.0.0 (October 9, 2025)
- ✅ Initial release
- ✅ SHAP integration
- ✅ LIME integration
- ✅ Method comparison
- ✅ Quality metrics
- ✅ User guide

### Upcoming Features:
- ⏳ Export functionality
- ⏳ Batch processing
- ⏳ Custom model upload
- ⏳ API access
- ⏳ Human study module

---

**Happy Explaining! 🎉**

*For more information, see START_HERE.md or QUICK_REFERENCE.md*
