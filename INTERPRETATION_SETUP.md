# Interpretation Layer Setup Guide

## Overview
The Interpretation Layer translates SHAP values into human-readable explanations using two paradigms:
1. **LLM-driven** (OpenAI GPT-4 Turbo)
2. **Rule-based** (Deterministic SHAP reasoning)

This is for master's thesis research comparing interpretability approaches.

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Add OpenAI API Key to Railway

**CRITICAL: Do this first!**

1. Go to [Railway Dashboard](https://railway.app)
2. Select project: `xaiplatformmasterthesis-production`
3. Click **Variables** tab
4. Click **+ New Variable**
5. Add:
   ```
   OPENAI_API_KEY=sk-proj-...your-key-here...
   ```
6. Railway will auto-redeploy (takes 2-3 minutes)

**Get API Key:** https://platform.openai.com/api-keys

---

### Step 2: Create Database Table

**Option A: Using Supabase Dashboard (Recommended)**

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project
3. Go to **SQL Editor**
4. Copy contents of `backend/migrations/4_interpretation_feedback.sql`
5. Paste and click **Run**
6. Verify: Go to **Table Editor** → should see `interpretation_feedback` table

**Option B: Using Python Script**

```bash
cd backend
python3 scripts/apply_interpretation_migration.py
```

---

### Step 3: Test the Page

1. Wait for deployments:
   - ✅ Railway (backend) - 2-3 minutes
   - ✅ Netlify (frontend) - 3-5 minutes

2. Go to: https://xai-working-project.netlify.app/interpretation

3. Test flow:
   - Select a model (e.g., German Credit XGBoost)
   - Click "Load SHAP Data"
   - Select "Compare Both"
   - Click "Generate Interpretation"
   - View LLM vs Rule-based side-by-side
   - Rate the quality (1-5 stars)
   - Submit feedback

---

## 📊 Database Schema

### Table: `interpretation_feedback`

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `interpretation_id` | VARCHAR(255) | Unique interpretation identifier |
| `model_id` | VARCHAR(255) | Model that was explained |
| `mode` | VARCHAR(50) | 'llm' or 'rule-based' |
| `clarity` | INT (1-5) | How clear was the explanation? |
| `trustworthiness` | INT (1-5) | How trustworthy? |
| `fairness` | INT (1-5) | How fair/unbiased? |
| `comments` | TEXT | Optional user comments |
| `user_id` | VARCHAR(255) | User who submitted feedback |
| `created_at` | TIMESTAMPTZ | Timestamp |

### Views (for analysis):
- `interpretation_feedback_summary` - Average ratings by mode
- `interpretation_feedback_by_model` - Ratings per model
- `interpretation_feedback_recent` - Last 50 entries

---

## 🎯 How It Works

### Backend Flow:

```
1. User selects model
   ↓
2. Frontend loads SHAP data from /api/v1/interpretation/model/{id}/shap
   ↓
3. User clicks "Generate Interpretation"
   ↓
4. Backend receives SHAP values
   ↓
5a. LLM Mode:                    5b. Rule-Based Mode:
    - Formats prompt                 - Applies deterministic rules
    - Calls OpenAI GPT-4             - Maps SHAP → human phrases
    - Returns natural text           - Returns structured text
   ↓
6. Frontend displays both side-by-side
   ↓
7. User rates quality (clarity, trust, fairness)
   ↓
8. Feedback saved to database for thesis research
```

### API Endpoints:

```
POST /api/v1/interpretation/generate
  Body: { model_id, shap_data, mode: "llm" | "rule-based" }
  Returns: { interpretation, top_features, confidence, method }

POST /api/v1/interpretation/compare
  Body: { model_id, shap_data }
  Returns: { llm: {...}, rule_based: {...} }

POST /api/v1/interpretation/feedback
  Body: { interpretation_id, model_id, mode, clarity, trustworthiness, fairness }
  Returns: { status: "success" }

GET /api/v1/interpretation/model/{model_id}/shap
  Returns: SHAP explanation data for the model
```

---

## 🧪 Testing

### Test LLM Mode:
```bash
curl -X POST "https://xaiplatformmasterthesis-production.up.railway.app/api/v1/interpretation/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "german-credit_xgboost_8d10e541",
    "mode": "llm",
    "shap_data": {
      "features": [
        {"feature": "credit_amount", "contribution": 0.45, "value": 5000},
        {"feature": "age", "contribution": -0.23, "value": 35}
      ],
      "prediction": "High Risk",
      "prediction_proba": 0.75
    }
  }'
```

### Test Rule-Based Mode:
```bash
# Same as above but with "mode": "rule-based"
```

### Test Comparison:
```bash
curl -X POST "https://xaiplatformmasterthesis-production.up.railway.app/api/v1/interpretation/compare?model_id=german-credit_xgboost_8d10e541" \
  -H "Content-Type: application/json" \
  -d '{ "shap_data": {...} }'
```

---

## 📈 Analyzing Results (For Thesis)

### Query average ratings:
```sql
SELECT * FROM interpretation_feedback_summary;
```

### Compare LLM vs Rule-based:
```sql
SELECT 
  mode,
  AVG(clarity) as avg_clarity,
  AVG(trustworthiness) as avg_trust,
  AVG(fairness) as avg_fairness,
  COUNT(*) as n
FROM interpretation_feedback
GROUP BY mode;
```

### Export for analysis:
```sql
COPY (
  SELECT * FROM interpretation_feedback
) TO '/tmp/interpretation_feedback.csv' CSV HEADER;
```

---

## 🐛 Troubleshooting

### "OpenAI API key not configured"
- ✅ Add `OPENAI_API_KEY` to Railway variables
- ✅ Wait for Railway to redeploy
- ✅ Check Railway logs for "OpenAI client initialized"

### "Failed to load SHAP data"
- ✅ Model must have SHAP explanation generated
- ✅ Go to model detail page and check if SHAP exists
- ✅ Train a new model (SHAP auto-generated)

### "Table does not exist"
- ✅ Run migration script or SQL in Supabase
- ✅ Check Supabase Table Editor for `interpretation_feedback`

### LLM responses are slow
- ⏱️ GPT-4 Turbo takes 3-10 seconds (normal)
- ⚡ Rule-based is instant (<100ms)

---

## 💰 Cost Estimation

### OpenAI API Costs:
- **GPT-4 Turbo**: ~$0.01 per interpretation
- **Typical usage**: 100 interpretations = $1.00
- **Thesis research**: ~$10-20 total

### Tips to reduce costs:
1. Use "Compare Both" mode (generates both at once)
2. Cache interpretations (already implemented)
3. Use rule-based mode for testing

---

## 📚 Research Questions

This implementation helps answer:

1. **RQ1**: Which interpretation paradigm (LLM vs Rule-based) provides clearer explanations?
2. **RQ2**: Which approach is more trustworthy to users?
3. **RQ3**: Which method is perceived as more fair/unbiased?
4. **RQ4**: How do interpretations differ between methods?

Collect at least **30 ratings per mode** for statistical significance.

---

## 🎓 Citation

If you use this in your thesis:

```
Lindner, J. (2025). Interpretation Layer: Comparing LLM-driven and 
Rule-based Approaches for Translating SHAP Values into Human-Readable 
Explanations. Master's Thesis, [Your University].
```

---

## 📞 Support

- **Backend logs**: Railway Dashboard → Deployments → Logs
- **Frontend errors**: Browser Console (F12)
- **Database**: Supabase Dashboard → Table Editor

---

## ✅ Checklist

- [ ] OpenAI API key added to Railway
- [ ] Database table created in Supabase
- [ ] Railway deployed successfully
- [ ] Netlify deployed successfully
- [ ] Tested LLM mode
- [ ] Tested Rule-based mode
- [ ] Tested Compare mode
- [ ] Submitted test feedback
- [ ] Verified feedback in database

**Ready to collect thesis data! 🎉**
