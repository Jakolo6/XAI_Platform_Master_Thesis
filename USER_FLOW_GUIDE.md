# 🎯 Complete User Flow Guide - XAI Platform

## **📱 How to Access All New Features**

### **1️⃣ Starting Point: Dashboard**

**URL:** `/dashboard`

**What You'll See:**
```
┌─────────────────────────────────────────────┐
│ Welcome back!                               │
│ your-email@example.com                      │
│                                             │
│ Quick Actions:                              │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ Manage       │  │ Train Model  │        │
│ │ Datasets     │  │              │        │
│ └──────────────┘  └──────────────┘        │
│ ┌──────────────┐  ┌──────────────┐        │
│ │ View         │  │ XAI Research │ ← NEW! │
│ │ Benchmarks   │  │ Lab          │        │
│ └──────────────┘  └──────────────┘        │
│                                             │
│ Complete XAI Workflow:                      │
│ 1. Browse datasets                          │
│ 2. Train models - SHAP auto-generated!     │
│ 3. View Global & Local explanations        │
│ 4. Evaluate quality, compare SHAP vs LIME  │
│ 5. Export results as CSV/JSON               │
└─────────────────────────────────────────────┘
```

**Action:** Click on **"XAI Research Lab"** card (has NEW badge)

---

### **2️⃣ Navigation Bar (Always Visible)**

**Top of every page:**
```
┌─────────────────────────────────────────────┐
│ XAI Finance                                 │
│ [Dashboard] [Datasets] [Train] [Research]  │
│                         ↑ NEW!              │
└─────────────────────────────────────────────┘
```

**Action:** Click **"Research"** in navbar to access leaderboard anytime

---

### **3️⃣ Research Page - XAI Leaderboard**

**URL:** `/research`

**What You'll See:**
```
┌─────────────────────────────────────────────┐
│ XAI Research Lab                            │
│ [Export Leaderboard CSV] ← Works now!      │
│                                             │
│ Filters:                                    │
│ Dataset: [All ▼]  Method: [All ▼]         │
│                                             │
│ XAI Leaderboard:                            │
│ ┌─────────────────────────────────────────┐ │
│ │ Model    │ Type │ AUC-ROC │ Quality    │ │
│ │ XGBoost  │ xgb  │ 0.911   │ -         │ │
│ │ RF       │ rf   │ 1.000   │ -         │ │
│ └─────────────────────────────────────────┘ │
│                                             │
│ Performance vs Quality Scatter Plot         │
│ SHAP vs LIME Comparison                     │
└─────────────────────────────────────────────┘
```

**Features:**
- ✅ Real data from backend
- ✅ Export leaderboard as CSV
- ✅ Filter by dataset/method
- ✅ Compare SHAP vs LIME

---

### **4️⃣ Model Detail Page - Global/Local Explanations**

**URL:** `/models/[id]` (click any model from dashboard/benchmarks)

**What You'll See:**

#### **A. Action Buttons (Top)**
```
┌─────────────────────────────────────────────┐
│ [Generate SHAP] [Generate LIME]             │
│ [Compare Methods]                           │
│ [Export Model Report] ← NEW! (Green)       │
│ [Export Comparison] ← NEW! (Purple)        │
└─────────────────────────────────────────────┘
```

#### **B. Feature Highlight Banner**
```
┌─────────────────────────────────────────────┐
│ ✨ New: Global & Local Explanations         │
│                                             │
│ Global: Average importance across all       │
│ Local: Explain ONE specific prediction      │
│ Try entering a sample index below!          │
└─────────────────────────────────────────────┘
```

#### **C. Explanation Type Toggle**
```
┌─────────────────────────────────────────────┐
│ Explanation Type:                           │
│ [🌍 Global] [🎯 Local]                     │
│                                             │
│ Global: Average importance across all       │
│ Local: Explanation for one specific         │
└─────────────────────────────────────────────┘
```

#### **D. When You Click "🎯 Local"**
```
┌─────────────────────────────────────────────┐
│ Sample Index: [5]                           │
│ [Generate Local SHAP]                       │
│ Enter a sample index (0-999) from test set  │
└─────────────────────────────────────────────┘
```

#### **E. After Generating Local Explanation**
```
┌─────────────────────────────────────────────┐
│ Prediction Info:                            │
│ ┌─────────────┬──────────────┬────────────┐ │
│ │ Prediction  │ Probability  │ True Label │ │
│ │ Not Fraud   │ 99.7%        │ Not Fraud  │ │
│ └─────────────┴──────────────┴────────────┘ │
│                                             │
│ Feature Contributions (SHAP Values):        │
│ TransactionAmt: -0.61 ████████ (red)       │
│ C2: -0.37 █████ (red)                      │
│ card2: -0.34 ████ (red)                    │
│ TransactionDT: +0.16 ███ (blue)            │
│                                             │
│ Base value: -3.89 (Expected model output)   │
└─────────────────────────────────────────────┘
```

---

### **5️⃣ Export Functionality**

#### **A. Export Model Report (CSV)**
**Button:** Green "Export Model Report" on model detail page

**Downloads:**
```csv
Metric,Value
Model ID,ieee-cis-fraud_xgboost_413d3682
Model Name,xgboost_ieee-cis-fraud
AUC-ROC,0.911
F1 Score,0.568
Feature Importance,
C8,0.120
C4,0.057
...
```

#### **B. Export Comparison (JSON)**
**Button:** Purple "Export Comparison" (appears when both SHAP & LIME exist)

**Downloads:**
```json
{
  "model": {
    "id": "...",
    "name": "..."
  },
  "shap": { ... },
  "lime": { ... }
}
```

#### **C. Export Leaderboard (CSV)**
**Button:** Blue "Export Leaderboard CSV" on research page

**Downloads:**
```csv
Model ID,Model Name,Model Type,AUC-ROC,F1 Score
xgb_1,XGBoost,xgboost,0.911,0.568
rf_1,Random Forest,random_forest,1.000,1.000
```

---

## **🎯 Complete User Journey Example**

### **Scenario: Train a model and explore explanations**

1. **Login** → Go to Dashboard
2. **Click "Train Model"** → Select dataset, model type, train
3. **Wait for training** → SHAP automatically generated!
4. **Click model name** → Go to model detail page
5. **See purple banner** → "New: Global & Local Explanations"
6. **Click "🎯 Local"** → Enter sample index: 5
7. **Click "Generate Local SHAP"** → See force plot in 2 seconds!
8. **Click "Export Model Report"** → CSV downloads
9. **Go to Research** (navbar) → See leaderboard
10. **Click "Export Leaderboard CSV"** → CSV downloads

---

## **🚀 Quick Access Checklist**

| Feature | How to Access |
|---------|---------------|
| **Research Page** | Navbar → Research OR Dashboard → XAI Research Lab card |
| **Global/Local Toggle** | Model detail page → Scroll to explanations section |
| **Local SHAP** | Model detail → Click "🎯 Local" → Enter index → Generate |
| **Export Model** | Model detail → Green "Export Model Report" button |
| **Export Comparison** | Model detail → Purple "Export Comparison" button |
| **Export Leaderboard** | Research page → Blue "Export Leaderboard CSV" button |
| **Quality Metrics** | Model detail → Scroll to "Quality Metrics" → Click "Show" |

---

## **💡 Pro Tips**

1. **Try different sample indices** (0-999) to see how explanations vary
2. **Compare Global vs Local** - Global shows overall, Local shows specific
3. **Export everything** for your thesis - CSV files are ready for analysis
4. **Use Research page** to compare models across datasets
5. **SHAP is auto-generated** - just train and it's ready!

---

## **🔧 Troubleshooting**

**Q: I don't see the Research link in navbar**
- A: Hard refresh (Cmd+Shift+R) or wait for Netlify deployment

**Q: Local SHAP button doesn't appear**
- A: Need at least one explanation (SHAP or LIME) first

**Q: Export buttons are grayed out**
- A: Make sure model training is complete

**Q: Quality metrics show "N/A"**
- A: Click "Show Quality Metrics" to trigger evaluation

---

**🎉 You're all set! The platform is ready for your thesis research.**
