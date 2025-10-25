# 🎯 Quick Reference: 4 Explanation Layers

## Layer Comparison Table

| Layer | Style | LLM? | Key Feature | Expected Outcome |
|-------|-------|------|-------------|------------------|
| **Layer 1** | Analytical Transparency | ❌ No | Raw SHAP values (4 decimals) | High trust (experts), Low comprehension (laypeople) |
| **Layer 2** | Conversational Summary | ✅ Yes (gpt-4o-mini) | Friendly AI talk, ≤80 words | High comprehension, Moderate trust |
| **Layer 3** | Causal + Counterfactual | ❌ No | "Because X... If Y..." | High fairness, High actionability |
| **Layer 4** | Visual Dashboard + Metaphor | ✅ Yes (gpt-4o-mini) | Emoji + Numbers + Metaphor | Best memory recall, Emotional resonance |

---

## Visual Preview

### Layer 1: Analytical Transparency
```
┌─────────────────────────────────────┐
│ Key Drivers                         │
│ Machine View - Raw SHAP Values      │
├─────────────────────────────────────┤
│ ↑ duration_months    +0.1523        │
│ ↑ credit_amount      +0.0842        │
│ ↓ checking_account   -0.0654        │
│ ↑ age                +0.0432        │
│ ↓ savings_account    -0.0321        │
└─────────────────────────────────────┘
```

### Layer 2: Conversational Summary
```
┌─────────────────────────────────────┐
│ Decision Summary                    │
│ AI Assistant Explanation            │
├─────────────────────────────────────┤
│ Unfortunately, your loan application│
│ was not approved at this time. The  │
│ decision was mainly influenced by   │
│ your loan duration and amount. Your │
│ current financial situation suggests│
│ a higher risk level.                │
└─────────────────────────────────────┘
```

### Layer 3: Causal + Counterfactual
```
┌─────────────────────────────────────┐
│ Why This Decision?                  │
│ Causal Story with What-If Scenario  │
├─────────────────────────────────────┤
│ ℹ️ Why This Decision?               │
│ Because your duration months (24)   │
│ indicates higher risk compared to   │
│ typical applicants, the system rated│
│ your application as risky.          │
│                                     │
│ 💡 What Could Change This?          │
│ If the loan duration were shortened │
│ by 6-12 months, approval would be   │
│ significantly more likely.          │
└─────────────────────────────────────┘
```

### Layer 4: Visual Dashboard + Metaphor
```
┌─────────────────────────────────────┐
│ Decision Dashboard                  │
│ Visual + Emotional Insight          │
├─────────────────────────────────────┤
│ ❌ REJECTED    High Risk    72%     │
│ 🔴 High Risk - 28% approval chance  │
├─────────────────────────────────────┤
│ 💭 "The numbers told a cautious     │
│    story about this credit path."   │
├─────────────────────────────────────┤
│ Key Factors:                        │
│ 1. 📅 Duration strongly reduced     │
│       approval (+0.152)             │
│ 2. 💰 Credit Amount moderately      │
│       reduced approval (+0.084)     │
│ 3. 🏦 Checking Account slightly     │
│       helped approval (-0.065)      │
├─────────────────────────────────────┤
│ 💡 Guidance: Choosing a shorter     │
│    loan duration would reduce risk. │
└─────────────────────────────────────┘
```

---

## Implementation Checklist

### Backend (Python)
- [x] OpenAI client initialized in `__init__`
- [x] Layer 1: Pure SHAP formatting
- [x] Layer 2: `_generate_conversational_summary()` with OpenAI
- [x] Layer 3: `_generate_counterfactual()` template-based
- [x] Layer 4: `_generate_metaphor()` with OpenAI
- [x] Layer 4: `_get_feature_emoji()` emoji mapping
- [x] Layer 4: `_generate_guidance()` actionable advice
- [x] Fallback templates for all LLM calls

### Frontend (React/TypeScript)
- [x] Layer 1: Slate header, SHAP values with arrows
- [x] Layer 2: Blue header, large text paragraph
- [x] Layer 3: Purple header, two-section layout
- [x] Layer 4: Gradient header, metaphor box, emoji drivers

### Configuration
- [x] OpenAI API key in `.env`
- [x] Model: `gpt-4o-mini` (cost-efficient)
- [x] Temperature: 0.7 (Layer 2), 0.8 (Layer 4)
- [x] Max tokens: 150 (Layer 2), 30 (Layer 4)

---

## Testing Commands

### Start Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Start Frontend
```bash
cd frontend
npm run dev
```

### Test URL
```
http://localhost:3000/study
```

### Test Each Layer
1. Start study session
2. Complete Case 1 → Check Layer X renders
3. Submit ratings
4. Repeat for all 6 cases
5. Final ranking screen

---

## OpenAI API Usage

### Layer 2 Prompt Template
```
Summarize this credit decision in ≤80 words. 
Be conversational and friendly, avoiding jargon and numbers.

Decision: Loan {approved/rejected}
Key factors:
- {feature1}: {helped/raised concerns}
- {feature2}: {helped/raised concerns}

Write 2-3 sentences explaining this decision in a friendly, 
accessible way.
```

### Layer 4 Metaphor Prompt Template
```
Write ONE short metaphor (≤12 words) that explains this 
credit decision emotionally but responsibly.

Decision: Loan {approved/rejected}
Risk level: {low/high}
Key factors: {feature1, feature2, feature3}

Example metaphors:
- "Your financial engine was strong, but the loan weight slowed it."
- "The numbers told a cautious story about your credit journey."

Write one metaphor (≤12 words):
```

---

## Cost Estimation

| Item | Value |
|------|-------|
| Model | gpt-4o-mini |
| Input cost | $0.15 / 1M tokens |
| Output cost | $0.60 / 1M tokens |
| Per case | ~$0.00009 |
| Per participant (6 cases) | ~$0.0005 |
| 100 participants | ~$0.05 |

---

## Emoji Reference (Layer 4)

| Feature Type | Emoji |
|--------------|-------|
| Amount/Credit | 💰 |
| Income/Salary | 💵 |
| Duration/Months | 📅 |
| Age | 👤 |
| Employment/Job | 💼 |
| Savings/Account | 🏦 |
| Property/Housing | 🏠 |
| Purpose | 🎯 |
| Default | 📊 |

**Risk Meter:**
- 🟢 Low Risk
- 🟡 Medium Risk
- 🔴 High Risk

---

## Data Collection

### Per Case (human_evaluations table)
- `method` = layer_id (layer_1, layer_2, layer_3, layer_4)
- `trust_score` (1-5)
- `understanding_score` (1-5)
- `usefulness_score` (1-5)
- `time_spent` (seconds)
- `comments` = JSON with:
  - `user_comments` (free text)
  - `mental_effort` (1-5)
  - `explanation_shown` (full explanation object)

### Per Session (study_sessions table)
- `session_id`
- `participant_code`
- `layer_assignments` (e.g., [layer_1, layer_3, layer_2, layer_4, layer_1, layer_3])
- `completed_questions` (0-6)
- `final_rankings` (JSON)

---

## Research Questions

1. **Does LLM-generated text increase trust?**
   - Compare Layer 2 (LLM) vs Layer 1 (template)

2. **Do metaphors improve memory recall?**
   - Test Layer 4 (metaphor) after 1 week

3. **Do counterfactuals increase perceived fairness?**
   - Compare Layer 3 (what-if) vs Layer 1 (descriptive)

4. **What's the optimal balance of detail vs simplicity?**
   - Compare all 4 layers on mental effort vs understanding

5. **Do hybrid approaches win?**
   - Check final rankings: Layer 3/4 vs Layer 1/2

---

## Troubleshooting

### OpenAI API not working
- Check `.env` file has `OPENAI_API_KEY=sk-...`
- Check backend logs for "OpenAI client initialized"
- If missing, fallback templates will be used (check logs)

### Layer 2 shows template instead of LLM text
- API call failed → check logs
- Fallback is working correctly
- Verify API key has credits

### Layer 4 missing metaphor
- API call failed → check logs
- Fallback metaphor will be used
- Verify API key has credits

### Emojis not displaying
- Check browser supports Unicode emojis
- Check font rendering
- Should work on all modern browsers

---

## Quick Stats

- **Total Lines of Code:** ~700 (backend) + ~250 (frontend)
- **API Calls per Case:** 2 (Layer 2 + Layer 4 metaphor)
- **Fallback Coverage:** 100% (all LLM calls have templates)
- **Cost per 100 participants:** ~$0.05
- **Implementation Time:** ~4 hours

---

## 🎉 Ready to Launch!

All 4 layers implemented with:
- ✅ Real SHAP values
- ✅ OpenAI integration
- ✅ Fallback templates
- ✅ Complete logging
- ✅ Professional UI

**Start your pilot study now!** 🚀
