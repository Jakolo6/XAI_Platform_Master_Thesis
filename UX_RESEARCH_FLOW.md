# XAI Platform - Research-Oriented User Flow Documentation

## 🎯 Overview

This document describes the **research-driven workflow** designed for ML specialists and researchers to compare, evaluate, and understand explainable AI models for fraud detection.

---

## 🧠 Design Philosophy

### Core Principles

1. **Research-First Design**
   - Prioritize scientific rigor over aesthetics
   - Clear data visualization and comparison tools
   - Traceability and reproducibility

2. **Progressive Disclosure**
   - Show high-level insights first
   - Allow drill-down into detailed metrics
   - Collapsible sections for advanced features

3. **Consistency & Clarity**
   - Unified color scheme (Blue for SHAP, Orange for LIME)
   - Consistent chart types and axes
   - Standard navigation patterns

4. **Academic Credibility**
   - Professional dark theme
   - High-contrast visualizations
   - Publication-ready exports

---

## 🚀 Complete User Journey

### **Step 1: Landing & Authentication**

**Page:** `/` (Landing Page)

**Goal:** Understand the platform and sign in

**User Actions:**
1. View hero section with platform overview
2. See three key features highlighted:
   - Train fraud detection models
   - Visualize explanations (SHAP/LIME)
   - Evaluate interpretability quality
3. Click "Start Research" CTA
4. Login or register

**Visual Design:**
- Dark academic theme (inspired by Hugging Face)
- Animated SHAP visualization in hero
- Gradient background with subtle motion
- Clean, professional typography

**Deliverables:**
- ✅ Landing page exists
- 🔄 Needs: Hero animation, updated copy

---

### **Step 2: Research Dashboard**

**Page:** `/dashboard`

**Goal:** Get overview of research activity and quick access to tools

**Layout Sections:**

#### A. Key Metrics Cards (Top)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│  Datasets   │   Models    │Explanations │ Avg Quality │
│      3      │     12      │     24      │    78.5%    │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### B. Recent Activity Feed
- Last 3 model trainings with status
- Last 3 explanation generations
- Timestamp and quick links

#### C. Leaderboard Snapshot
- Top 3 models by AUC-ROC
- Top 3 models by explanation quality
- 🏆 icon for best performers

#### D. Quick Actions
```
┌─────────────────┬─────────────────┬─────────────────┐
│ Upload Dataset  │  Train Model    │Compare Methods  │
└─────────────────┴─────────────────┴─────────────────┘
```

**Current Status:**
- ✅ Basic dashboard exists
- 🔄 Needs: Enhanced metrics cards, activity feed, leaderboard snapshot

---

### **Step 3: Dataset Management**

**Page:** `/datasets`

**Goal:** Upload custom datasets or select pre-loaded ones

**Features:**

#### A. Upload Button (Top Right)
- Opens `UploadDatasetModal`
- Drag-and-drop CSV interface
- Validates file format and size
- Collects metadata:
  - Dataset name
  - Target column
  - Description
  - Task type (classification/regression)

#### B. Dataset Cards
```
┌─────────────────────────────────────┐
│ IEEE-CIS Fraud Detection            │
│ 590,540 samples | 50 features       │
│ Class Balance: 96.5% / 3.5%         │
│ Status: ✅ Processed                │
│ [Use for Training]                  │
└─────────────────────────────────────┘
```

#### C. Dataset Preview (Optional)
- First 10 rows in table
- Feature types and distributions
- Missing value summary

**Current Status:**
- ✅ Dataset listing exists
- ✅ Upload modal component created
- 🔄 Needs: Backend upload endpoint, R2 integration

---

### **Step 4: Model Training**

**Page:** `/models/train`

**Goal:** Train models with reproducible configuration

**Form Layout:**

```
Dataset Selection:     [Dropdown: IEEE-CIS Fraud ▼]
Algorithm:            [Dropdown: XGBoost ▼]

☐ Optimize Hyperparameters (Optuna)
☐ Enable Early Stopping

[Advanced Settings ▼]
  - Max Trials: [50]
  - Timeout: [300s]
  - Random Seed: [42]

[Train Model]
```

**After Training:**
- Progress bar with status
- "View Training Logs" link
- Auto-redirect to `/models/[id]` on completion

**Current Status:**
- ✅ Training form exists
- ✅ Async training with Celery
- 🔄 Needs: Live progress updates, training logs modal

---

### **Step 5: Model Detail Page**

**Page:** `/models/[id]`

**Goal:** Comprehensive model analysis and transparency

**Tab Structure:**

#### **Tab 1: Performance** 📊
- Key metrics cards (AUC-ROC, F1, Accuracy, Precision)
- ROC curve (interactive)
- PR curve (interactive)
- Confusion matrix heatmap
- Metrics comparison chart

#### **Tab 2: Explanations** 🧠
- Feature importance (top 15 with bars)
- SHAP global visualization
- LIME local visualization
- "Generate SHAP" / "Generate LIME" buttons
- Export to CSV

#### **Tab 3: Quality Evaluation** ⚡
- Faithfulness metrics
- Robustness metrics
- Complexity metrics
- Radar chart (SHAP vs LIME)
- Composite quality score

**Current Status:**
- ✅ Performance tab fully implemented
- ✅ Explanations generation exists
- ✅ Feature importance displayed
- 🔄 Needs: Tab navigation, quality evaluation tab

---

### **Step 6: XAI Research Lab**

**Page:** `/research` (NEW!)

**Goal:** Compare explainability methods across all models

**Sections:**

#### A. Filters Bar
```
Dataset: [All Datasets ▼]  Method: [All Methods ▼]  ☑ Show Pareto Frontier
```

#### B. Key Metrics Cards
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Model     │    SHAP     │    LIME     │    Best     │
│Performance  │Avg Quality  │Avg Quality  │  Model AUC  │
│   88.5%     │   80.2%     │   73.0%     │   90.2%     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### C. Trade-off Scatter Plot
- X-axis: Model Performance (AUC-ROC)
- Y-axis: Explanation Quality
- Points colored by method (Blue=SHAP, Orange=LIME)
- Pareto frontier line (optional)
- Interactive tooltips

#### D. Radar Comparison
- 5 dimensions: Faithfulness, Robustness, Complexity, Stability, Sparsity
- SHAP overlay (blue)
- LIME overlay (orange)
- Metric descriptions below

#### E. Global Leaderboard Table
```
Rank | Model | Dataset | Method | AUC | Faithfulness | Robustness | Complexity | Quality
  1  | XGB   | IEEE    | SHAP   | 90% |     85%      |    78%     |    83%     |  82%
  2  | RF    | IEEE    | SHAP   | 87% |     81%      |    75%     |    80%     |  79%
```

#### F. Research Insights Box
- Key findings (SHAP vs LIME)
- Advantages of each method
- Recommendations

**Current Status:**
- ✅ Research page created with all components
- ✅ Trade-off scatter implemented
- ✅ Radar chart implemented
- 🔄 Needs: Real data integration

---

### **Step 7: Benchmarking**

**Page:** `/benchmarks`

**Goal:** Cross-dataset model comparison

**Tab Structure:**

#### **Tab 1: Model Performance**
- Leaderboard by AUC-ROC
- Grouped by dataset
- Training time and model size

#### **Tab 2: Explanation Quality**
- Leaderboard by quality score
- Method comparison (SHAP vs LIME)
- Quality breakdown

#### **Tab 3: Correlation Analysis**
- Does interpretability reduce accuracy?
- Scatter plot: AUC vs Quality
- Statistical correlation coefficient

**Current Status:**
- ✅ Basic benchmarks page exists
- 🔄 Needs: Tab structure, quality leaderboard, correlation view

---

### **Step 8: Report Generation**

**Page:** `/reports` (NEW!)

**Goal:** Export publication-ready results

**Features:**

#### A. Report Configuration
```
Select Models:     [☑ XGBoost IEEE-CIS] [☑ Random Forest IEEE-CIS]
Select Datasets:   [☑ IEEE-CIS Fraud]
Include Sections:  [☑ Summary] [☑ Metrics] [☑ Visualizations] [☑ Explanations]
Format:           [PDF ▼] or [CSV ▼]
```

#### B. Report Contents
- **Summary Table:** All selected models with key metrics
- **Feature Importances:** Top features for each model
- **Visualizations:** ROC curves, PR curves, confusion matrices
- **SHAP/LIME Charts:** Explanation visualizations
- **Quality Summary:** Faithfulness, robustness, complexity
- **Metadata:** Date, author, system version

#### C. Export Button
- Generates PDF (ReportLab) or CSV
- Downloads immediately
- Filename: `xai_report_YYYY-MM-DD.pdf`

**Current Status:**
- ❌ Not implemented
- 🔄 Needs: Full page creation, PDF generation backend

---

### **Step 9: User Profile**

**Page:** `/profile` (NEW!)

**Goal:** Researcher identity and resource management

**Sections:**

#### A. Profile Information
- Name, email, role
- Registration date
- Last login

#### B. API Access (Optional)
- API key for automation
- "Regenerate Key" button
- Usage statistics

#### C. My Resources
- List of uploaded datasets
- List of trained models
- Storage usage

#### D. Settings
- Theme preference (light/dark)
- Email notifications
- Export preferences

**Current Status:**
- ❌ Not implemented
- 🔄 Needs: Full page creation

---

## 🎨 Visual Design System

### Color Palette

#### Primary Colors
- **SHAP Blue:** `#3b82f6` (Blue-500)
- **LIME Orange:** `#f97316` (Orange-500)
- **Success Green:** `#10b981` (Green-500)
- **Warning Yellow:** `#fbbf24` (Yellow-400)
- **Error Red:** `#ef4444` (Red-500)

#### Neutral Colors
- **Background Light:** `#f9fafb` (Gray-50)
- **Background Dark:** `#111827` (Gray-900)
- **Text Primary:** `#111827` (Gray-900)
- **Text Secondary:** `#6b7280` (Gray-500)
- **Border:** `#e5e7eb` (Gray-200)

### Typography

- **Headings:** Inter, Bold, 24-32px
- **Body:** Inter, Regular, 14-16px
- **Code/Metrics:** JetBrains Mono, 12-14px

### Component Patterns

#### Cards
```css
background: white
border: 1px solid gray-200
border-radius: 8px
padding: 24px
shadow: sm
```

#### Buttons
```css
Primary: bg-blue-600, text-white, hover:bg-blue-700
Secondary: bg-gray-100, text-gray-700, hover:bg-gray-200
Danger: bg-red-600, text-white, hover:bg-red-700
```

#### Charts
- **Recharts** for standard charts (bar, line, scatter)
- **Plotly** for advanced interactive charts (optional)
- Consistent axis labels and tooltips
- High contrast colors for accessibility

---

## 🔄 Navigation Flow

### Primary Navigation (Top Bar)
```
[Logo] Dashboard | Datasets | Train Model | Research | Benchmarks | Reports
                                                              [Profile ▼] [Logout]
```

### Breadcrumbs
```
Dashboard > Models > XGBoost IEEE-CIS > Performance
```

### Quick Actions (Dashboard)
- Upload Dataset → `/datasets` with modal open
- Train Model → `/models/train`
- Compare Methods → `/research`

---

## 📊 Data Flow

### Model Training Flow
```
User selects dataset + algorithm
    ↓
POST /api/v1/models/train
    ↓
Celery task starts (async)
    ↓
User polls GET /api/v1/tasks/{task_id}
    ↓
Training completes
    ↓
Redirect to /models/{model_id}
```

### Explanation Generation Flow
```
User clicks "Generate SHAP"
    ↓
POST /api/v1/explanations/generate
    ↓
Celery task starts (async)
    ↓
Progress bar updates
    ↓
Explanation completes
    ↓
Display SHAP visualization
```

### Quality Evaluation Flow
```
User clicks "Evaluate Quality"
    ↓
POST /api/v1/explanations/{id}/evaluate
    ↓
Calculate faithfulness, robustness, complexity
    ↓
Display radar chart and metrics
```

---

## 🎯 Implementation Status

### ✅ Fully Implemented
- Authentication & Authorization
- Dataset listing (pre-loaded)
- Model training (5 algorithms)
- Model evaluation (10+ metrics)
- ROC/PR curves
- Feature importance
- SHAP/LIME generation
- Confusion matrix
- Benchmarking (basic)

### 🔄 Partially Implemented
- Dashboard (needs enhancement)
- Model detail page (needs tabs)
- Explanation quality (demo data)

### ❌ Not Yet Implemented
- Landing page hero animation
- Dataset upload backend
- Research/XAI Evaluation page (frontend created, needs data)
- Report generation
- Profile page
- Real-time training progress
- Quality metric calculation (real)

---

## 🚀 Next Steps for Full Implementation

### Priority 1: Core Research Features
1. ✅ Create research page with visualizations
2. ✅ Implement trade-off scatter plot
3. ✅ Implement quality radar chart
4. ✅ Create upload dataset modal
5. 🔄 Add tab navigation to model detail page
6. 🔄 Integrate real quality metrics

### Priority 2: Enhanced UX
1. 🔄 Upgrade landing page with hero
2. 🔄 Enhance dashboard with activity feed
3. 🔄 Add dataset upload backend
4. 🔄 Create report generation page
5. 🔄 Add profile page

### Priority 3: Advanced Features
1. 🔄 Real-time training progress (WebSockets)
2. 🔄 Batch explanation generation
3. 🔄 Advanced filtering and search
4. 🔄 PDF report generation
5. 🔄 Collaboration features

---

## 📚 Component Library

### New Components Created

1. **`QualityMetricsRadar.tsx`** ✅
   - Radar chart for 5-dimensional quality comparison
   - SHAP vs LIME overlay
   - Metric descriptions

2. **`TradeOffScatter.tsx`** ✅
   - Scatter plot for performance vs quality
   - Pareto frontier calculation
   - Interactive tooltips

3. **`UploadDatasetModal.tsx`** ✅
   - Drag-and-drop file upload
   - Form validation
   - Metadata collection

4. **`ROCCurveChart.tsx`** ✅
   - Interactive ROC curve
   - AUC score display
   - Performance categories

5. **`PRCurveChart.tsx`** ✅
   - Precision-Recall curve
   - Baseline comparison
   - Fraud detection context

### Existing Components (Enhanced)
- `MetricsChart.tsx` - Bar chart for metrics
- `ConfusionMatrixChart.tsx` - Heatmap
- `FeatureImportanceChart.tsx` - Horizontal bars
- `ExplanationViewer.tsx` - SHAP/LIME display

---

## 🎓 Research Workflow Summary

```
1. LOGIN → Dashboard overview
2. DATASETS → Upload or select dataset
3. TRAIN → Select algorithm, configure, train
4. EVALUATE → View performance metrics, ROC/PR curves
5. EXPLAIN → Generate SHAP/LIME explanations
6. QUALITY → Evaluate explanation quality
7. COMPARE → Research page for cross-model comparison
8. BENCHMARK → Cross-dataset leaderboards
9. EXPORT → Generate PDF/CSV reports
```

---

## 🏆 Success Criteria

A successful research workflow implementation means:

✅ **Clarity:** Researchers can immediately understand model performance and explanation quality  
✅ **Comparability:** Easy to compare SHAP vs LIME across models and datasets  
✅ **Traceability:** Every result links back to source model and configuration  
✅ **Reproducibility:** All settings and versions are visible and exportable  
✅ **Credibility:** Professional design suitable for academic publication  

---

**Last Updated:** January 11, 2025  
**Version:** 2.0.0  
**Platform:** XAI Finance - Research-Oriented Workflow
