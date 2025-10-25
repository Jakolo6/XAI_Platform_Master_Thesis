# Study Flow - Quick Start Guide

## 🚀 What Was Implemented

A complete user study infrastructure for evaluating 4 different explanation styles using the **UCI German Credit dataset**.

### Study Flow
1. Participant sees 6 loan application cases
2. Each case shows: applicant data → model decision → explanation (1 of 4 styles)
3. Participant rates: trust, understanding, usefulness, mental effort
4. After 6 cases: rank the 4 explanation styles from best to worst
5. Data saved to Supabase for analysis

---

## 📂 File Structure

```
backend/
├── app/
│   ├── services/
│   │   └── study_service.py          ✨ NEW - Core study logic
│   └── api/v1/endpoints/
│       └── study.py                   ✅ UPDATED - API endpoints

frontend/
├── src/
│   ├── app/study/
│   │   ├── page.tsx                   ✅ UPDATED - Intro page
│   │   ├── session/page.tsx           ✨ REPLACED - Main study UI
│   │   └── final/page.tsx             ✨ NEW - Final ranking
│   └── components/study/
│       └── ExplanationLayers.tsx      ✨ NEW - Layer components
```

---

## 🎯 Next Step: Implement Your 4 Explanation Layers

### Where to Edit

**1. Backend Data Formatting**
File: `backend/app/services/study_service.py`
Function: `_format_explanation_for_layer()` (lines ~180-250)

```python
if layer == "layer_1":
    # TODO: Format data for your first explanation style
    base_explanation["rendered_content"] = {
        "type": "your_type",
        "data": { ... }
    }
```

**2. Frontend Rendering**
File: `frontend/src/components/study/ExplanationLayers.tsx`
Components: `Layer1Explanation`, `Layer2Explanation`, `Layer3Explanation`, `Layer4Explanation`

```tsx
export const Layer1Explanation: React.FC<ExplanationLayerProps> = ({
  features, prediction_proba, rendered_content
}) => {
  // TODO: Implement your visualization
  return <div>Your Layer 1 UI</div>;
};
```

---

## 🧪 Testing Locally

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

### 3. Test the Flow
1. Visit: http://localhost:3000/study
2. Click "Start Study"
3. Complete a case with ratings
4. Check console for API calls
5. Verify data in Supabase

---

## 🗄️ Database Schema

### Tables Used (Already Exist)

**study_sessions**
- Tracks each participant session
- Stores: session_id, participant_code, randomization_seed, status

**human_evaluations**
- Stores ratings for each case
- Stores: trust_score, understanding_score, usefulness_score, time_spent, comments
- `method` field = explanation layer type (layer_1, layer_2, layer_3, layer_4)

---

## 📊 Data You'll Collect

### Per Case (6 cases × N participants)
- Which explanation layer was shown
- Trust rating (1-5)
- Understanding rating (1-5)
- Usefulness rating (1-5)
- Mental effort rating (1-5)
- Time spent viewing
- Optional comments

### Per Session (N participants)
- Final ranking of all 4 layers (1=best, 4=worst)
- Which layers were shown in which order

---

## 🎨 Explanation Layer Ideas

Here are some research-backed explanation styles you could implement:

### Layer 1: Feature Importance List
- Simple ranked list of features
- Show +/- contribution
- Minimal cognitive load

### Layer 2: Natural Language Narrative
- LLM-generated explanation
- Reads like a human analyst
- High interpretability

### Layer 3: Visual Bar Chart
- Color-coded horizontal bars
- Immediate visual understanding
- Good for comparisons

### Layer 4: Counterfactual Scenarios
- "What if X was Y, then Z would happen"
- Actionable insights
- Helps understand decision boundaries

---

## 🔧 Configuration

### Study Parameters
Edit in `backend/app/services/study_service.py`:

```python
STUDY_MODEL_ID = "german_credit_xgb"      # Your trained model
STUDY_DATASET_ID = "uci_german_credit"    # Your dataset
NUM_CASES_PER_SESSION = 6                 # Cases per participant
EXPLANATION_LAYERS = ["layer_1", "layer_2", "layer_3", "layer_4"]
```

---

## ✅ Implementation Checklist

- [x] Backend service created
- [x] API endpoints implemented
- [x] Frontend session page created
- [x] Final comparison page created
- [x] Rating collection implemented
- [x] Database integration complete
- [x] Layer component structure ready
- [ ] **Layer 1 visualization implemented** ← YOU ARE HERE
- [ ] **Layer 2 visualization implemented**
- [ ] **Layer 3 visualization implemented**
- [ ] **Layer 4 visualization implemented**
- [ ] Test with real participants
- [ ] Export data for analysis

---

## 🐛 Troubleshooting

### "Model not found"
- Ensure `german_credit_xgb` model exists in Supabase
- Check R2 storage has the model file

### "Dataset not found"
- Verify `datasets/uci_german_credit/processed/test.parquet` exists in R2
- Check dataset is processed and uploaded

### "Supabase not available"
- Check `.env` file has correct Supabase credentials
- Verify database tables exist (run migration SQL)

### Frontend build errors
- Run `npm install` in frontend directory
- Check TypeScript types match API responses

---

## 📚 Additional Resources

### Key Files to Reference
- **Existing SHAP logic**: `backend/app/services/sandbox_service.py`
- **Existing UI patterns**: `frontend/src/app/sandbox/page.tsx`
- **Database schema**: `backend/migrations/FINAL_supabase_schema.sql`

### API Endpoints
- `POST /api/v1/study/session/start` - Create session
- `POST /api/v1/study/case` - Get case with explanation
- `POST /api/v1/study/response` - Submit ratings
- `GET /api/v1/study/session/{id}/final` - Get comparison data
- `POST /api/v1/study/session/{id}/ranking` - Submit final ranking

---

## 🎓 Research Tips

### Balancing Layer Assignments
The system ensures each participant sees all 4 layers at least once across 6 cases. The remaining 2 cases are randomly assigned.

### Randomization
Each session gets a unique `randomization_seed` to ensure reproducibility while maintaining randomness.

### Data Analysis
Export data from Supabase:
```sql
-- Get all ratings
SELECT * FROM human_evaluations 
WHERE session_id IN (
  SELECT id FROM study_sessions WHERE status = 'completed'
);

-- Get average ratings by layer
SELECT 
  method as layer,
  AVG(trust_score) as avg_trust,
  AVG(understanding_score) as avg_understanding,
  AVG(usefulness_score) as avg_usefulness,
  COUNT(*) as n
FROM human_evaluations
GROUP BY method;
```

---

## 🚀 Ready to Implement!

The infrastructure is complete. Focus on implementing your 4 explanation layer visualizations in:
1. `backend/app/services/study_service.py` - Data formatting
2. `frontend/src/components/study/ExplanationLayers.tsx` - UI rendering

Good luck with your master thesis! 🎓
