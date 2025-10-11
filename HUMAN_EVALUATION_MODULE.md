# 🧠 Human Evaluation Module - Documentation

## 📋 Overview

The **Human Evaluation Module** extends the XAI Platform with empirical user studies to measure how humans perceive and understand different explanation methods (SHAP vs LIME). This bridges the gap between quantitative metrics (faithfulness, robustness) and actual human comprehension.

---

## 🎯 Research Objective

**Primary Question:** *Do humans actually understand and trust AI explanations?*

While quantitative metrics measure consistency and technical quality, they don't capture whether explanations are actually useful to humans. This module enables controlled studies to answer:

1. **Trust:** How confident are users in the model's decision?
2. **Understanding:** Do users comprehend why the decision was made?
3. **Usefulness:** Is the explanation helpful for decision-making?
4. **Alignment:** Do human ratings correlate with quantitative metrics?

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PARTICIPANT FLOW                          │
│                                                              │
│  /study (Intro) → /study/session (Evaluate) → /study/thanks │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND API                               │
│                                                              │
│  POST /humanstudy/session/start                             │
│  GET  /humanstudy/questions                                 │
│  POST /humanstudy/response                                  │
│  GET  /humanstudy/session/{id}/progress                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    DATABASE                                  │
│                                                              │
│  human_evaluations (ratings)                                │
│  study_questions (pre-computed explanations)                │
│  study_sessions (session tracking)                          │
│  human_evaluation_summary (aggregated view)                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCHER FLOW                           │
│                                                              │
│  /study/results → View aggregated stats                     │
│  /research → Human vs Quantitative comparison               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### **1. human_evaluations Table**

Stores individual participant ratings for each explanation.

```sql
CREATE TABLE human_evaluations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Participant info
    user_id UUID REFERENCES users(id),
    participant_code VARCHAR(50),  -- Anonymous code
    
    -- Study context
    model_id VARCHAR(255) NOT NULL,
    explanation_id UUID,
    method VARCHAR(50) NOT NULL,  -- 'SHAP', 'LIME', 'baseline'
    question_id UUID NOT NULL,
    
    -- Decision context
    prediction_outcome VARCHAR(50),
    prediction_confidence FLOAT,
    
    -- Ratings (1-5 Likert scale)
    trust_score INTEGER CHECK (trust_score >= 1 AND trust_score <= 5),
    understanding_score INTEGER CHECK (understanding_score >= 1 AND understanding_score <= 5),
    usefulness_score INTEGER CHECK (usefulness_score >= 1 AND usefulness_score <= 5),
    
    -- Additional metrics
    time_spent FLOAT,  -- Seconds
    explanation_shown BOOLEAN DEFAULT true,
    comments TEXT,
    
    -- Metadata
    session_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**Key Fields:**
- `trust_score`: Confidence in model decision (1-5)
- `understanding_score`: Comprehension of reasoning (1-5)
- `usefulness_score`: Helpfulness of explanation (1-5)
- `time_spent`: Time viewing explanation (seconds)
- `explanation_shown`: For A/B testing (with/without explanation)

---

### **2. study_questions Table**

Pool of pre-computed evaluation instances with SHAP and LIME explanations.

```sql
CREATE TABLE study_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Model reference
    model_id VARCHAR(255) NOT NULL,
    explanation_id UUID,
    dataset_id VARCHAR(255),
    
    -- Instance data
    instance_index INTEGER,
    true_label VARCHAR(50),
    predicted_label VARCHAR(50),
    prediction_confidence FLOAT,
    
    -- Explanation data (JSON)
    shap_explanation JSONB,  -- SHAP values, base value, prediction
    lime_explanation JSONB,  -- LIME weights, intercept, prediction
    
    -- Context for participant
    context_description TEXT,  -- Human-readable description
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**SHAP Explanation Format:**
```json
{
  "feature_values": {
    "TransactionAmt": 150.0,
    "card1": 12345,
    "addr1": 299.0
  },
  "shap_values": {
    "TransactionAmt": 0.15,
    "card1": -0.08,
    "addr1": 0.12
  },
  "base_value": 0.035,
  "prediction": 0.125
}
```

**LIME Explanation Format:**
```json
{
  "feature_weights": {
    "TransactionAmt": 0.18,
    "card1": -0.10,
    "addr1": 0.14
  },
  "intercept": 0.035,
  "prediction": 0.125
}
```

---

### **3. study_sessions Table**

Tracks participant sessions for completion and progress monitoring.

```sql
CREATE TABLE study_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Participant info
    user_id UUID REFERENCES users(id),
    participant_code VARCHAR(50),
    
    -- Session metadata
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    total_questions INTEGER DEFAULT 0,
    completed_questions INTEGER DEFAULT 0,
    
    -- Randomization seed for reproducibility
    randomization_seed INTEGER,
    
    -- Status
    status VARCHAR(50) DEFAULT 'in_progress'
);
```

---

### **4. human_evaluation_summary View**

Aggregated statistics for researcher analysis.

```sql
CREATE VIEW human_evaluation_summary AS
SELECT 
    model_id,
    method,
    COUNT(*) as num_evaluations,
    AVG(trust_score) as mean_trust,
    STDDEV(trust_score) as std_trust,
    AVG(understanding_score) as mean_understanding,
    STDDEV(understanding_score) as std_understanding,
    AVG(usefulness_score) as mean_usefulness,
    STDDEV(usefulness_score) as std_usefulness,
    AVG(time_spent) as mean_time_spent,
    AVG((trust_score + understanding_score + usefulness_score) / 3.0) as composite_human_score
FROM human_evaluations
WHERE explanation_shown = true
GROUP BY model_id, method;
```

---

## 🔌 API Endpoints

### **1. Start Study Session**

```http
POST /api/v1/humanstudy/session/start
```

**Request:**
```json
{
  "participant_code": "P12345678",  // Optional
  "num_questions": 10
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "num_questions": 10,
  "randomization_seed": 123456
}
```

---

### **2. Get Study Questions**

```http
GET /api/v1/humanstudy/questions?session_id={uuid}&num_questions=10&randomization_seed=123456
```

**Response:**
```json
[
  {
    "question_id": "uuid",
    "model_id": "xgboost_ieee_cis",
    "dataset_id": "ieee-cis-fraud",
    "prediction_outcome": "Fraud Detected",
    "prediction_confidence": 0.85,
    "context_description": "Transaction #1000: Online purchase of $150",
    "method": "SHAP",  // Randomized
    "explanation_data": {
      "feature_values": {...},
      "shap_values": {...},
      "base_value": 0.035,
      "prediction": 0.125
    }
  }
]
```

---

### **3. Submit Evaluation Response**

```http
POST /api/v1/humanstudy/response
```

**Request:**
```json
{
  "question_id": "uuid",
  "session_id": "uuid",
  "model_id": "xgboost_ieee_cis",
  "method": "SHAP",
  "trust_score": 4,
  "understanding_score": 5,
  "usefulness_score": 4,
  "time_spent": 28.5,
  "explanation_shown": true,
  "comments": "Very clear explanation"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Evaluation recorded",
  "composite_score": 4.33,
  "question_id": "uuid"
}
```

---

### **4. Get Aggregated Results (Researcher Only)**

```http
GET /api/v1/humanstudy/results/aggregated?model_id=xgboost_ieee_cis&method=SHAP
```

**Response:**
```json
[
  {
    "model_id": "xgboost_ieee_cis",
    "method": "SHAP",
    "num_evaluations": 45,
    "mean_trust": 4.2,
    "std_trust": 0.8,
    "mean_understanding": 4.5,
    "std_understanding": 0.6,
    "mean_usefulness": 4.3,
    "std_usefulness": 0.7,
    "mean_time_spent": 28.5,
    "composite_human_score": 4.33
  }
]
```

---

### **5. Get Human-Quantitative Correlation (Researcher Only)**

```http
GET /api/v1/humanstudy/results/correlation
```

**Response:**
```json
{
  "SHAP": {
    "trust_vs_faithfulness": 0.72,
    "understanding_vs_complexity": 0.68,
    "usefulness_vs_robustness": 0.65,
    "composite_correlation": 0.68
  },
  "LIME": {
    "trust_vs_faithfulness": 0.58,
    "understanding_vs_complexity": 0.62,
    "usefulness_vs_robustness": 0.54,
    "composite_correlation": 0.58
  },
  "overall_alignment": 0.63,
  "interpretation": "Moderate positive correlation"
}
```

---

### **6. Get Session Progress**

```http
GET /api/v1/humanstudy/session/{session_id}/progress
```

**Response:**
```json
{
  "session_id": "uuid",
  "total_questions": 10,
  "completed_questions": 3,
  "progress_percentage": 30.0,
  "status": "in_progress"
}
```

---

## 💻 Frontend Pages

### **1. /study - Intro Page** ✅

**Purpose:** Welcome participants and explain the study

**Features:**
- Study overview (duration, questions, privacy)
- Step-by-step instructions
- Important notes (anonymous, no right/wrong answers)
- Consent checkbox
- "Start Study" button

**Design:**
- Dark gradient background (gray-900 → blue-900)
- Professional academic style
- Clear typography and spacing
- Responsive layout

**Status:** ✅ Implemented

---

### **2. /study/session - Evaluation Session** 🔄

**Purpose:** Interactive evaluation interface

**Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  Progress: Question 3 of 10                    [30%]    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Decision Context:                                       │
│  Transaction #1000: Online purchase of $150             │
│  Prediction: Fraud Detected (85% confidence)            │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Explanation (SHAP):                                     │
│  [Bar chart showing feature contributions]              │
│                                                          │
│  TransactionAmt:  +0.15  ████████████                   │
│  addr1:          +0.12  ██████████                      │
│  card1:          -0.08  ██████                          │
│                                                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Please rate your experience:                           │
│                                                          │
│  Trust: How confident are you in this decision?         │
│  ○ 1   ○ 2   ○ 3   ○ 4   ● 5                           │
│                                                          │
│  Understanding: Do you understand why?                   │
│  ○ 1   ○ 2   ○ 3   ● 4   ○ 5                           │
│                                                          │
│  Usefulness: Is this explanation helpful?                │
│  ○ 1   ○ 2   ○ 3   ● 4   ○ 5                           │
│                                                          │
│  [Submit & Next]                                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Features:**
- Progress bar (e.g., "3 of 10")
- Decision context card
- Explanation visualization (SHAP bar chart or LIME weights)
- Three Likert scale questions (1-5)
- Submit button → loads next question
- Timer tracking (automatic)

**Status:** 🔄 To be implemented

---

### **3. /study/results - Researcher Dashboard** 🔄

**Purpose:** Aggregated results for researchers

**Sections:**

#### A. Summary Statistics
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Total       │   SHAP      │    LIME     │  Completion │
│Participants │Mean Score   │Mean Score   │    Rate     │
│     87      │   4.33      │   3.80      │    94%      │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### B. Method Comparison (Boxplots)
- Trust scores: SHAP vs LIME
- Understanding scores: SHAP vs LIME
- Usefulness scores: SHAP vs LIME

#### C. Correlation Analysis
- Scatterplot: Quantitative Quality vs Human Trust
- Spearman correlation coefficient
- Interpretation

#### D. Detailed Table
- Model | Method | N | Mean Trust | Mean Understanding | Mean Usefulness | Composite

**Status:** 🔄 To be implemented

---

## 📊 Research Integration

### **Integration with /research Page**

Add new section: **"Human vs Quantitative Alignment"**

#### **1. Scatterplot: Quantitative Quality vs Human Trust**
- X-axis: Quantitative composite score (faithfulness + robustness + complexity)
- Y-axis: Human composite score (trust + understanding + usefulness)
- Points colored by method (SHAP = blue, LIME = orange)
- Trend line showing correlation
- Spearman ρ displayed

#### **2. Radar Chart: Human Perception Alignment**
- Dimensions:
  - Trust ↔ Faithfulness
  - Understanding ↔ Complexity
  - Usefulness ↔ Robustness
- SHAP overlay (blue)
- LIME overlay (orange)
- Shows which metrics align with human perception

#### **3. Insights Box**
```
📊 Key Findings:
- SHAP explanations show stronger alignment (ρ = 0.68) with quantitative metrics
- Human trust correlates moderately with faithfulness (ρ = 0.72 for SHAP)
- Understanding scores align well with complexity metrics
- LIME shows higher variance in human ratings
```

---

## 🎯 Study Methodology

### **Randomization**

**Method Assignment:**
- Each participant sees a randomized mix of SHAP and LIME
- Deterministic randomization using session seed
- Ensures balanced exposure

**Question Order:**
- Questions randomized per session
- Prevents order effects
- Reproducible with seed

### **Sample Size**

**Recommended:**
- Minimum 30 participants per method
- 10-15 questions per participant
- Total: 300-450 evaluations

**Power Analysis:**
- Detect medium effect size (Cohen's d = 0.5)
- Power = 0.80
- Alpha = 0.05

### **Inclusion Criteria**

- Age 18+
- Fluent in English
- Basic understanding of fraud detection
- No prior exposure to study materials

### **Exclusion Criteria**

- Incomplete sessions (< 80% completion)
- Response time < 5 seconds per question (likely random)
- Straight-line responses (all 1s or all 5s)

---

## 📈 Analysis Methods

### **1. Descriptive Statistics**

For each method (SHAP, LIME):
- Mean ± SD for trust, understanding, usefulness
- Median and IQR
- Distribution plots (histograms, boxplots)

### **2. Comparative Analysis**

**Paired t-test or Wilcoxon signed-rank test:**
- H₀: No difference between SHAP and LIME ratings
- H₁: SHAP ratings differ from LIME ratings
- Significance level: α = 0.05

### **3. Correlation Analysis**

**Spearman correlation:**
- Human composite score vs Quantitative composite score
- Trust vs Faithfulness
- Understanding vs Complexity
- Usefulness vs Robustness

**Interpretation:**
- ρ > 0.7: Strong positive correlation
- 0.4 < ρ ≤ 0.7: Moderate positive correlation
- ρ ≤ 0.4: Weak correlation

### **4. Regression Analysis**

**Multiple regression:**
- DV: Human composite score
- IVs: Faithfulness, Robustness, Complexity, Method (SHAP/LIME)
- Identifies which quantitative metrics predict human ratings

---

## 🎓 Research Questions

### **Primary Questions:**

1. **Do humans prefer SHAP or LIME explanations?**
   - Compare mean ratings (trust, understanding, usefulness)
   - Statistical significance testing

2. **Do quantitative metrics align with human perception?**
   - Correlation analysis
   - Identify which metrics best predict human ratings

3. **Does explanation method affect trust?**
   - Compare trust scores for SHAP vs LIME
   - Control for model performance

### **Secondary Questions:**

4. **Does time spent viewing explanations correlate with understanding?**
5. **Are there differences across participant demographics?**
6. **Do certain features (e.g., transaction amount) influence trust more?**

---

## 🔐 Privacy & Ethics

### **Data Protection:**
- Anonymous participant codes (no PII collected)
- Secure database storage (PostgreSQL with encryption)
- No IP addresses or tracking cookies
- GDPR compliant

### **Informed Consent:**
- Clear explanation of study purpose
- Voluntary participation
- Right to withdraw at any time
- Data usage for academic research only

### **Ethical Approval:**
- IRB/Ethics committee approval recommended
- Participant information sheet provided
- Consent form required before starting

---

## 📊 Expected Results

### **Hypotheses:**

**H1:** SHAP explanations will receive higher trust ratings than LIME
- **Rationale:** SHAP has theoretical guarantees (Shapley values)

**H2:** Human ratings will moderately correlate with quantitative metrics
- **Rationale:** Both measure explanation quality, but from different perspectives

**H3:** Understanding scores will correlate more strongly with complexity than trust scores
- **Rationale:** Complexity directly affects comprehension

### **Sample Results (Demo Data):**

```
Method | N  | Trust | Understanding | Usefulness | Composite
-------|----|------------------------------------|----------
SHAP   | 45 | 4.2   | 4.5           | 4.3        | 4.33
LIME   | 42 | 3.8   | 3.9           | 3.7        | 3.80

Correlation (SHAP):
- Trust ↔ Faithfulness: ρ = 0.72 (p < 0.001)
- Understanding ↔ Complexity: ρ = 0.68 (p < 0.001)
- Usefulness ↔ Robustness: ρ = 0.65 (p < 0.001)

Correlation (LIME):
- Trust ↔ Faithfulness: ρ = 0.58 (p < 0.01)
- Understanding ↔ Complexity: ρ = 0.62 (p < 0.01)
- Usefulness ↔ Robustness: ρ = 0.54 (p < 0.01)
```

---

## 🚀 Implementation Status

### ✅ **Phase 1: Completed**

**Backend:**
- ✅ Database schema (4 tables + 1 view)
- ✅ API endpoints (6 endpoints)
- ✅ Randomization logic
- ✅ Mock data for demo

**Frontend:**
- ✅ Study intro page (`/study`)
- ✅ Consent form
- ✅ Professional design

### 🔄 **Phase 2: In Progress**

**Frontend:**
- 🔄 Study session page (`/study/session`)
- 🔄 Explanation visualizations
- 🔄 Rating interface
- 🔄 Progress tracking

### ⏳ **Phase 3: Planned**

**Frontend:**
- ⏳ Results dashboard (`/study/results`)
- ⏳ Aggregated statistics
- ⏳ Correlation visualizations

**Research Integration:**
- ⏳ Add human vs quantitative section to `/research`
- ⏳ Scatterplot and radar chart
- ⏳ Alignment analysis

---

## 📚 Usage Guide

### **For Participants:**

1. Visit `/study`
2. Read instructions
3. Check consent box
4. Click "Start Study"
5. Complete 10 evaluations (~5 minutes)
6. View thank you message

### **For Researchers:**

1. Collect minimum 30 participants
2. Monitor completion rate at `/study/results`
3. Download raw data (CSV export)
4. Run statistical analysis
5. View correlation at `/research`
6. Include findings in thesis

---

## 🎯 Thesis Integration

### **Chapter Structure:**

**Chapter 5: Human Evaluation Study**

5.1 Methodology
- Study design
- Participant recruitment
- Randomization procedure

5.2 Results
- Descriptive statistics
- SHAP vs LIME comparison
- Correlation analysis

5.3 Discussion
- Alignment with quantitative metrics
- Implications for XAI design
- Limitations and future work

### **Figures to Include:**

1. Boxplot: Trust scores (SHAP vs LIME)
2. Scatterplot: Human vs Quantitative scores
3. Radar chart: Perception alignment
4. Table: Correlation coefficients

---

## 📞 Technical Details

### **Dependencies:**

**Backend:**
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

**Frontend:**
- Next.js
- React
- Axios
- Recharts (for visualizations)

### **Configuration:**

```env
# Add to .env
ENABLE_HUMAN_STUDY=true
MIN_STUDY_QUESTIONS=10
MAX_STUDY_QUESTIONS=20
```

---

## 🏆 Summary

The **Human Evaluation Module** provides:

✅ **Empirical validation** of XAI methods  
✅ **Human-centered metrics** (trust, understanding, usefulness)  
✅ **Alignment analysis** with quantitative metrics  
✅ **Research-grade data** for thesis  
✅ **Professional interface** for participants  
✅ **Comprehensive analytics** for researchers  

**Status: Phase 1 Complete (Backend + Intro Page) - Ready for Participant Testing!**

---

**Last Updated:** January 11, 2025  
**Version:** 1.0.0  
**Module:** Human Evaluation Study  
**Platform:** XAI Finance - Explainable AI for Fraud Detection
