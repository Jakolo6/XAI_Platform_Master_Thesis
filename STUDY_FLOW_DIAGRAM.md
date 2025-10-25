# Study Flow Architecture Diagram

## 📊 Complete System Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         PARTICIPANT JOURNEY                          │
└─────────────────────────────────────────────────────────────────────┘

1. INTRO PAGE (/study)
   │
   ├─ Read study description
   ├─ Agree to terms
   └─ Click "Start Study"
      │
      ▼
   POST /api/v1/study/session/start
      │
      ├─ Generate session_id
      ├─ Generate participant_code (e.g., "P12345678")
      ├─ Create randomization_seed
      ├─ Assign layers to 6 cases: [layer_1, layer_3, layer_2, layer_4, layer_1, layer_3]
      └─ Save to study_sessions table
      │
      ▼
   Redirect to /study/session?session_id=xxx&assignments=layer_1,layer_3,...


2. SESSION PAGE (/study/session) - CASE 1 of 6
   │
   ▼
   POST /api/v1/study/case
   {
     session_id: "xxx",
     case_index: 0,
     layer_assignment: "layer_1"
   }
      │
      ├─ Load sample from german_credit_xgb model
      ├─ Get test data from R2: datasets/uci_german_credit/processed/test.parquet
      ├─ Generate SHAP explanation
      ├─ Format loan data (applicant info, loan details, financial status)
      ├─ Format explanation for layer_1
      └─ Return case data
      │
      ▼
   DISPLAY TO USER:
   ┌──────────────────────────────────────────┐
   │  Loan Application Details                │
   │  ├─ Applicant: Age, Employment, etc.     │
   │  ├─ Loan: Amount, Duration, etc.         │
   │  └─ Financial: Checking, Savings, etc.   │
   ├──────────────────────────────────────────┤
   │  Model Decision                          │
   │  ├─ ✓ Approved / ✗ Denied               │
   │  ├─ Confidence: 75%                      │
   │  └─ Risk Score: ████░░░░░░               │
   ├──────────────────────────────────────────┤
   │  Explanation (Layer 1 Style)             │
   │  └─ [Your custom visualization]          │
   ├──────────────────────────────────────────┤
   │  Rate This Explanation                   │
   │  ├─ Trust:          ★★★★☆               │
   │  ├─ Understanding:  ★★★★★               │
   │  ├─ Usefulness:     ★★★★☆               │
   │  ├─ Mental Effort:  ★★☆☆☆               │
   │  └─ Comments: [optional text]            │
   └──────────────────────────────────────────┘
      │
      ▼
   Click "Next Case"
      │
      ▼
   POST /api/v1/study/response
   {
     session_id: "xxx",
     case_index: 0,
     instance_id: "sample_42",
     explanation_layer: "layer_1",
     trust: 4,
     understanding: 5,
     usefulness: 4,
     mental_effort: 2,
     time_spent: 45.3,
     comments: "Very clear"
   }
      │
      ├─ Save to human_evaluations table
      ├─ Update study_sessions.completed_questions = 1
      └─ Return success
      │
      ▼
   Load CASE 2 (layer_3) → Same flow
      │
      ▼
   Load CASE 3 (layer_2) → Same flow
      │
      ▼
   ... Continue for all 6 cases ...
      │
      ▼
   After CASE 6 → Redirect to /study/final?session_id=xxx


3. FINAL PAGE (/study/final)
   │
   ▼
   GET /api/v1/study/session/{session_id}/final
      │
      ├─ Query all evaluations for this session
      ├─ Group by explanation_layer
      ├─ Calculate averages per layer
      └─ Return summary
      │
      ▼
   DISPLAY TO USER:
   ┌──────────────────────────────────────────┐
   │  Rank the Explanation Styles             │
   ├──────────────────────────────────────────┤
   │  Layer 1 (2 cases)                       │
   │  ├─ Avg Trust: 4.5                       │
   │  ├─ Avg Understanding: 4.0               │
   │  ├─ Avg Usefulness: 4.5                  │
   │  └─ Your Rank: [Select 1-4] ▼            │
   ├──────────────────────────────────────────┤
   │  Layer 2 (1 case)                        │
   │  ├─ Avg Trust: 3.0                       │
   │  ├─ Avg Understanding: 3.0               │
   │  ├─ Avg Usefulness: 3.0                  │
   │  └─ Your Rank: [Select 1-4] ▼            │
   ├──────────────────────────────────────────┤
   │  Layer 3 (2 cases)                       │
   │  └─ Your Rank: [Select 1-4] ▼            │
   ├──────────────────────────────────────────┤
   │  Layer 4 (1 case)                        │
   │  └─ Your Rank: [Select 1-4] ▼            │
   └──────────────────────────────────────────┘
      │
      ▼
   Click "Submit Rankings"
      │
      ▼
   POST /api/v1/study/session/{session_id}/ranking
   {
     session_id: "xxx",
     rankings: {
       "layer_1": 1,  // Best
       "layer_3": 2,
       "layer_2": 4,  // Worst
       "layer_4": 3
     }
   }
      │
      ├─ Validate rankings (must be 1,2,3,4)
      ├─ Update study_sessions.status = 'completed'
      └─ Return success
      │
      ▼
   THANK YOU PAGE
   ┌──────────────────────────────────────────┐
   │  ✓ Study Complete!                       │
   │                                          │
   │  Thank you for participating.            │
   │  Your responses have been saved.         │
   │                                          │
   │  Session ID: xxx                         │
   └──────────────────────────────────────────┘
```

---

## 🗄️ Database Schema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SUPABASE TABLES                              │
└─────────────────────────────────────────────────────────────────────┘

study_sessions
├─ id (UUID, PK)
├─ participant_code (VARCHAR)
├─ started_at (TIMESTAMP)
├─ completed_at (TIMESTAMP)
├─ total_questions (INT) = 6
├─ completed_questions (INT) = 0→6
├─ randomization_seed (INT)
└─ status (VARCHAR) = 'in_progress' | 'completed'

human_evaluations
├─ id (UUID, PK)
├─ session_id (UUID, FK → study_sessions)
├─ participant_code (VARCHAR)
├─ model_id (VARCHAR) = 'german_credit_xgb'
├─ question_id (UUID)
├─ method (VARCHAR) = 'layer_1' | 'layer_2' | 'layer_3' | 'layer_4'
├─ trust_score (INT 1-5)
├─ understanding_score (INT 1-5)
├─ usefulness_score (INT 1-5)
├─ time_spent (FLOAT)
├─ comments (TEXT)
└─ created_at (TIMESTAMP)
```

---

## 🔄 Backend Service Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICE LAYER                             │
└─────────────────────────────────────────────────────────────────────┘

study_service.py
│
├─ create_study_session()
│  ├─ Generate session_id, participant_code, seed
│  ├─ Randomize layer assignments (ensure all 4 layers appear)
│  └─ Save to study_sessions table
│
├─ get_study_case(session_id, case_index, layer_assignment)
│  ├─ Call sandbox_service.get_sample_instance(model_id)
│  │  ├─ Load model from R2
│  │  ├─ Load test data from R2
│  │  ├─ Get random sample
│  │  └─ Return features + prediction
│  │
│  ├─ Call sandbox_service.generate_shap_explanation(model_id, instance_id)
│  │  ├─ Create SHAP TreeExplainer
│  │  ├─ Calculate SHAP values
│  │  └─ Return feature contributions
│  │
│  ├─ _format_loan_data(features)
│  │  └─ Categorize into applicant_info, loan_details, financial_status
│  │
│  └─ _format_explanation_for_layer(shap_data, layer_type)
│     ├─ if layer == "layer_1": [TODO: Your implementation]
│     ├─ if layer == "layer_2": [TODO: Your implementation]
│     ├─ if layer == "layer_3": [TODO: Your implementation]
│     └─ if layer == "layer_4": [TODO: Your implementation]
│
├─ save_case_response(session_id, case_index, ratings)
│  ├─ Create evaluation record
│  ├─ Save to human_evaluations table
│  └─ Update study_sessions.completed_questions
│
├─ get_final_comparison_data(session_id)
│  ├─ Query all evaluations for session
│  ├─ Group by layer
│  └─ Calculate averages
│
└─ save_final_ranking(session_id, rankings)
   ├─ Validate rankings (1,2,3,4)
   └─ Update study_sessions.status = 'completed'
```

---

## 🎨 Frontend Component Tree

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FRONTEND COMPONENTS                               │
└─────────────────────────────────────────────────────────────────────┘

/study/page.tsx (Intro)
└─ StudyIntroPage
   ├─ Header
   ├─ Welcome Card
   ├─ Instructions
   ├─ Consent Checkbox
   └─ Start Button → POST /study/session/start

/study/session/page.tsx (Main Study)
└─ StudySessionContent
   ├─ Progress Bar (Case X of 6)
   ├─ LoanDataDisplay
   │  ├─ Applicant Info Section
   │  ├─ Loan Details Section
   │  ├─ Financial Status Section
   │  └─ Other Info Section
   │
   ├─ DecisionDisplay
   │  ├─ Approve/Deny Badge
   │  ├─ Confidence Percentage
   │  └─ Risk Score Bar
   │
   ├─ ExplanationDisplay
   │  └─ ExplanationRouter
   │     ├─ if layer_1 → Layer1Explanation [TODO]
   │     ├─ if layer_2 → Layer2Explanation [TODO]
   │     ├─ if layer_3 → Layer3Explanation [TODO]
   │     └─ if layer_4 → Layer4Explanation [TODO]
   │
   └─ RatingForm
      ├─ RatingStars (Trust)
      ├─ RatingStars (Understanding)
      ├─ RatingStars (Usefulness)
      ├─ RatingStars (Mental Effort)
      ├─ Comments TextArea
      └─ Submit Button → POST /study/response

/study/final/page.tsx (Comparison)
└─ FinalComparisonContent
   ├─ Layer Summary Cards
   │  ├─ Layer 1 Card (avg ratings + rank selector)
   │  ├─ Layer 2 Card (avg ratings + rank selector)
   │  ├─ Layer 3 Card (avg ratings + rank selector)
   │  └─ Layer 4 Card (avg ratings + rank selector)
   │
   └─ Submit Rankings Button → POST /study/session/{id}/ranking

/components/study/ExplanationLayers.tsx
├─ Layer1Explanation [TODO: Implement]
├─ Layer2Explanation [TODO: Implement]
├─ Layer3Explanation [TODO: Implement]
├─ Layer4Explanation [TODO: Implement]
└─ ExplanationRouter (selects which layer to render)
```

---

## 📊 Data Flow Example

```
EXAMPLE: Participant completes Case 1

1. Frontend requests case
   POST /study/case
   { session_id: "abc123", case_index: 0, layer_assignment: "layer_1" }

2. Backend processes
   ├─ Load model: german_credit_xgb
   ├─ Load sample: datasets/uci_german_credit/processed/test.parquet[42]
   ├─ Features: { duration_months: 24, credit_amount: 5000, age: 35, ... }
   ├─ Prediction: 0.25 (low risk → approved)
   ├─ SHAP values: { duration_months: +0.15, credit_amount: -0.08, ... }
   └─ Format for layer_1

3. Frontend displays
   ├─ Loan Data: Age 35, Amount 5000, Duration 24 months
   ├─ Decision: ✓ Approved (75% confidence)
   └─ Explanation: [Layer 1 visualization]

4. User rates
   ├─ Trust: 4/5
   ├─ Understanding: 5/5
   ├─ Usefulness: 4/5
   ├─ Mental Effort: 2/5
   └─ Time: 45.3 seconds

5. Frontend submits
   POST /study/response
   { session_id: "abc123", case_index: 0, trust: 4, ... }

6. Backend saves
   INSERT INTO human_evaluations
   (session_id, method, trust_score, understanding_score, ...)
   VALUES ('abc123', 'layer_1', 4, 5, ...)

7. Repeat for cases 2-6 with different layers
```

---

## 🎯 Implementation Checklist

### ✅ Complete
- [x] Session management
- [x] Case loading
- [x] SHAP generation
- [x] Loan data formatting
- [x] Decision visualization
- [x] Rating collection
- [x] Database persistence
- [x] Progress tracking
- [x] Final comparison
- [x] Ranking collection

### 🚧 Your Task
- [ ] Implement Layer 1 visualization
- [ ] Implement Layer 2 visualization
- [ ] Implement Layer 3 visualization
- [ ] Implement Layer 4 visualization

### 📍 Exact Locations
1. Backend: `backend/app/services/study_service.py` line ~180
2. Frontend: `frontend/src/components/study/ExplanationLayers.tsx` lines ~40, ~80, ~120, ~160

---

## 🚀 You're Ready!

The complete infrastructure is in place. Focus on implementing your 4 unique explanation styles to make your research contribution!
