# Study Flow Implementation Summary

## ✅ Implementation Complete

The study flow infrastructure has been successfully implemented for the UCI German Credit dataset user study.

---

## 📁 Files Created/Modified

### Backend

1. **`backend/app/services/study_service.py`** ✨ NEW
   - Core business logic for study session management
   - Functions:
     - `create_study_session()` - Initialize session with random layer assignments
     - `get_study_case()` - Load case data with SHAP explanation
     - `save_case_response()` - Store ratings in database
     - `get_final_comparison_data()` - Aggregate results for comparison
     - `save_final_ranking()` - Store final layer rankings
   - **TODO**: Implement 4 explanation layer renderers in `_format_explanation_for_layer()`

2. **`backend/app/api/v1/endpoints/study.py`** ✅ UPDATED
   - RESTful API endpoints:
     - `POST /study/session/start` - Create session
     - `POST /study/case` - Get case with explanation
     - `POST /study/response` - Submit ratings
     - `GET /study/session/{id}/final` - Get comparison data
     - `POST /study/session/{id}/ranking` - Submit final ranking
     - `GET /study/session/{id}/progress` - Get progress
     - `GET /study/health` - Health check

### Frontend

3. **`frontend/src/app/study/page.tsx`** ✅ UPDATED
   - Study intro page
   - Updated to call new `/study/session/start` endpoint
   - Passes layer assignments to session page

4. **`frontend/src/app/study/session/page.tsx`** ✨ REPLACED
   - Main study session interface
   - Shows 6 cases sequentially
   - Components:
     - `LoanDataDisplay` - Shows applicant info, loan details, financial status
     - `DecisionDisplay` - Shows approve/deny decision with confidence
     - `ExplanationDisplay` - **TODO**: Render based on layer type
     - `RatingStars` - 5-point Likert scale input
   - Collects: trust, understanding, usefulness, mental effort, comments
   - Tracks time spent per case

5. **`frontend/src/app/study/final/page.tsx`** ✨ NEW
   - Final comparison screen
   - Shows summary of all layers experienced
   - Collects ranking (1-4) for each layer
   - Thank you page on completion

---

## 🗄️ Database Tables Used

### Existing Tables (No Changes Needed)

- **`study_sessions`** - Tracks session metadata
  - Columns: `id`, `participant_code`, `started_at`, `completed_at`, `total_questions`, `completed_questions`, `randomization_seed`, `status`

- **`human_evaluations`** - Stores case ratings
  - Columns: `id`, `session_id`, `participant_code`, `model_id`, `question_id`, `method` (stores layer type), `trust_score`, `understanding_score`, `usefulness_score`, `time_spent`, `comments`, `created_at`
  - Note: `method` field is repurposed to store explanation layer type

### Optional Enhancement

If you want to add `mental_effort` as a separate column:

```sql
ALTER TABLE human_evaluations 
ADD COLUMN mental_effort INTEGER CHECK (mental_effort >= 1 AND mental_effort <= 5);
```

Currently, mental effort is stored in the `comments` field or can be added to a JSONB column.

---

## 🔄 Study Flow

```
1. Participant visits /study
   ↓
2. Clicks "Start Study" → POST /study/session/start
   ↓
3. Backend creates session, assigns 4 layers randomly to 6 cases
   ↓
4. Redirects to /study/session?session_id=xxx&assignments=layer_1,layer_2,...
   ↓
5. For each case (1-6):
   a. POST /study/case → Get loan data + decision + explanation
   b. User views and rates
   c. POST /study/response → Save ratings
   d. Load next case
   ↓
6. After 6 cases → Redirect to /study/final?session_id=xxx
   ↓
7. GET /study/session/{id}/final → Show layer summaries
   ↓
8. User ranks layers 1-4
   ↓
9. POST /study/session/{id}/ranking → Save rankings
   ↓
10. Thank you page
```

---

## 🎯 Next Steps: Implement 4 Explanation Layers

### Where to Add Layer Renderers

**Backend:** `backend/app/services/study_service.py`
- Function: `_format_explanation_for_layer()`
- Lines: ~180-250
- Currently returns placeholder `rendered_content` for each layer

**Frontend:** `frontend/src/app/study/session/page.tsx`
- Component: `ExplanationDisplay`
- Lines: ~340-380
- Currently shows placeholder + raw SHAP data

### Implementation Pattern

For each layer (layer_1, layer_2, layer_3, layer_4):

1. **Backend** - Format data structure:
   ```python
   if layer == "layer_1":
       base_explanation["rendered_content"] = {
           "type": "your_type",
           "data": {
               # Your formatted data here
           }
       }
   ```

2. **Frontend** - Render visualization:
   ```tsx
   if (explanation.layer_type === "layer_1") {
       return <YourLayer1Component data={rendered_content} />;
   }
   ```

### Example Layer Ideas

- **Layer 1**: Simple feature list with +/- indicators
- **Layer 2**: Natural language narrative (LLM-generated)
- **Layer 3**: Visual bar chart with color coding
- **Layer 4**: Counterfactual "what-if" scenarios

---

## 🧪 Testing the Implementation

### 1. Start Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Flow
1. Visit http://localhost:3000/study
2. Agree to terms and click "Start Study"
3. Complete 6 cases with ratings
4. Rank the explanation layers
5. Check database for stored data

### 4. Verify Database
```sql
-- Check sessions
SELECT * FROM study_sessions ORDER BY started_at DESC LIMIT 5;

-- Check evaluations
SELECT * FROM human_evaluations ORDER BY created_at DESC LIMIT 10;
```

---

## 📊 Data Collection

### Per Case (6 cases × N participants)
- Session ID
- Case index (0-5)
- Instance ID (sample from German Credit dataset)
- Explanation layer shown (layer_1, layer_2, layer_3, or layer_4)
- Trust rating (1-5)
- Understanding rating (1-5)
- Usefulness rating (1-5)
- Mental effort rating (1-5)
- Time spent (seconds)
- Optional comments

### Per Session (N participants)
- Participant code (anonymous)
- Layer assignments (which layer for each case)
- Final rankings (1-4 for each layer)
- Completion status

---

## 🔧 Configuration

### Dataset & Model
- **Dataset**: UCI German Credit (Statlog)
- **Dataset ID**: `uci_german_credit`
- **Model ID**: `german_credit_xgb`
- **Storage**: R2 at `datasets/uci_german_credit/processed/test.parquet`

### Study Parameters
- **Cases per session**: 6 (configurable in `study_service.py`)
- **Explanation layers**: 4 (layer_1, layer_2, layer_3, layer_4)
- **Rating scale**: 1-5 (Likert)
- **Randomization**: Each participant sees all 4 layers at least once

---

## ⚠️ Important Notes

1. **Model must exist**: Ensure `german_credit_xgb` model is trained and stored in R2
2. **Dataset must exist**: Ensure test.parquet is available at the expected path
3. **Supabase required**: Database must be accessible for session/response storage
4. **Layer renderers**: Currently placeholders - implement before running study
5. **Anonymous participants**: No authentication required, uses generated participant codes

---

## 🎨 UI/UX Features

- **Progress bar**: Shows case X of 6
- **Loan data display**: Categorized by applicant info, loan details, financial status
- **Decision display**: Visual approve/deny with confidence meter
- **Star ratings**: Interactive 5-star input for each dimension
- **Comments field**: Optional free-text feedback
- **Responsive design**: Works on desktop and tablet
- **Loading states**: Smooth transitions between cases
- **Error handling**: User-friendly error messages

---

## 📝 Code Quality

- ✅ TypeScript types defined
- ✅ Error handling implemented
- ✅ Logging with structlog
- ✅ Input validation (ratings 1-5, rankings 1-4)
- ✅ Responsive UI with TailwindCSS
- ✅ Modular component structure
- ✅ Clear TODO comments for layer implementation
- ✅ Suspense boundaries for loading states

---

## 🚀 Ready for Next Phase

The infrastructure is complete and ready for you to implement the 4 interpretational layers. The code is modular, well-documented, and follows the existing codebase patterns.

**Next task**: Define and implement your 4 explanation layer styles in the marked TODO sections.
