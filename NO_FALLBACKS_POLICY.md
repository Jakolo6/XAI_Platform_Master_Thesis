# 🚨 NO FALLBACKS POLICY - OpenAI Required for Layers 2 & 4

## Policy

**NO MADE-UP DATA ALLOWED.** If OpenAI API fails, the study will show an error instead of fallback templates.

---

## What Changed

### Before (with fallbacks)
- Layer 2: If OpenAI failed → showed template text
- Layer 4: If OpenAI failed → showed template metaphor
- **Problem:** Participants might see made-up template data instead of real LLM output

### After (NO fallbacks)
- Layer 2: If OpenAI fails → **raises ValueError with error message**
- Layer 4: If OpenAI fails → **raises ValueError with error message**
- **Result:** Study stops, admin is notified, no made-up data shown

---

## Implementation

### Layer 2: Conversational Summary
```python
def _generate_conversational_summary(...) -> str:
    if not self.openai_client:
        logger.error("OpenAI API key not configured - Layer 2 requires OpenAI")
        raise ValueError("Layer 2 requires OpenAI API key. Please configure OPENAI_API_KEY in environment.")
    
    try:
        # Call OpenAI API
        response = self.openai_client.chat.completions.create(...)
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API call failed for Layer 2: {e}")
        raise ValueError(f"Failed to generate Layer 2 explanation via OpenAI: {str(e)}")
```

### Layer 4: Metaphor Generation
```python
def _generate_metaphor(...) -> str:
    if not self.openai_client:
        logger.error("OpenAI API key not configured - Layer 4 requires OpenAI")
        raise ValueError("Layer 4 requires OpenAI API key. Please configure OPENAI_API_KEY in environment.")
    
    try:
        # Call OpenAI API
        response = self.openai_client.chat.completions.create(...)
        metaphor = response.choices[0].message.content.strip()
        return metaphor
    except Exception as e:
        logger.error(f"OpenAI API call failed for Layer 4 metaphor: {e}")
        raise ValueError(f"Failed to generate Layer 4 metaphor via OpenAI: {str(e)}")
```

---

## Error Handling

### Startup Check
When the backend starts:
```
✅ OpenAI API key found → "OpenAI client initialized for study service"
❌ No API key → "OpenAI API key not configured - Layers 2 & 4 will FAIL without it"
                "Please set OPENAI_API_KEY in your .env file to use Layers 2 and 4"
```

### Runtime Errors
If a participant encounters Layer 2 or Layer 4 without OpenAI:
1. Backend raises `ValueError` with clear message
2. Frontend receives 500 error
3. Error displayed to participant
4. Study cannot continue until fixed

---

## What This Means

### ✅ Guaranteed Data Integrity
- **Layer 1:** Pure SHAP values (no LLM, no templates)
- **Layer 2:** 100% OpenAI-generated text OR error
- **Layer 3:** Template-based counterfactuals (deterministic, no LLM)
- **Layer 4:** 100% OpenAI-generated metaphor OR error

### ✅ No Mixed Data
- Participants will NEVER see a mix of LLM and template data
- Either all Layer 2 cases use OpenAI, or study fails
- Either all Layer 4 cases use OpenAI, or study fails

### ✅ Clear Error Messages
- Admin knows immediately if OpenAI is not configured
- Logs show exactly which API call failed
- No silent fallbacks that hide problems

---

## Setup Requirements

### CRITICAL: Set OpenAI API Key
```bash
# In backend/.env
OPENAI_API_KEY=sk-...your-key-here...
```

### Verify Setup
```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Check logs for:
✅ "OpenAI client initialized for study service"

# If you see:
❌ "OpenAI API key not configured - Layers 2 & 4 will FAIL without it"
   → Set OPENAI_API_KEY in .env immediately!
```

---

## Testing

### Test OpenAI Integration
1. **Set API key** in `.env`
2. **Start backend** and check logs
3. **Start study** and complete cases
4. **Verify Layer 2** shows LLM-generated text (not template)
5. **Verify Layer 4** shows LLM-generated metaphor (not template)

### Test Error Handling (Optional)
1. **Remove API key** from `.env`
2. **Restart backend** → should see error logs
3. **Try Layer 2 or Layer 4** → should fail with clear error
4. **Restore API key** and restart

---

## Layers That Don't Need OpenAI

### Layer 1: Analytical Transparency
- ✅ Pure SHAP values
- ✅ No LLM required
- ✅ Always works

### Layer 3: Causal + Counterfactual
- ✅ Template-based
- ✅ No LLM required
- ✅ Always works
- ✅ Deterministic and reproducible

---

## Benefits of This Approach

### 1. Data Integrity
- **No contamination** between LLM and template data
- **Clear distinction** between layers
- **Reproducible results** for research

### 2. Transparency
- **Participants know** if something went wrong
- **Researchers know** exactly what was shown
- **No hidden fallbacks** that mask issues

### 3. Quality Control
- **Forces proper setup** before study launch
- **Prevents pilot studies** with broken configuration
- **Ensures consistent experience** across all participants

---

## Cost Implications

### With This Policy
- **Must have OpenAI credits** to run study
- **Cost per participant:** ~$0.0005 (6 cases)
- **Cost for 100 participants:** ~$0.05
- **No free fallback option**

### Why It's Worth It
- **Research validity:** No mixed data
- **Data quality:** All LLM-generated text is real
- **Reproducibility:** Clear what was shown
- **Low cost:** <$0.05 per 100 participants

---

## Troubleshooting

### Error: "Layer 2 requires OpenAI API key"
**Solution:** Set `OPENAI_API_KEY` in `backend/.env`

### Error: "Failed to generate Layer 2 explanation via OpenAI"
**Possible causes:**
- API key invalid
- No credits remaining
- Network issue
- Rate limit exceeded

**Solution:** Check OpenAI dashboard, verify credits, check logs

### Error: "Layer 4 requires OpenAI API key"
**Solution:** Same as Layer 2 - set API key

---

## Summary

✅ **NO FALLBACKS** = **NO MADE-UP DATA**

- Layer 2 & 4 **require OpenAI API**
- If API fails → **study fails with clear error**
- No silent fallbacks to templates
- Guarantees data integrity for research

**Set your OpenAI API key before running the study!** 🔑
