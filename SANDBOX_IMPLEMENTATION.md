# 🎯 Explainability Sandbox - Implementation Guide

## 📋 Overview

The **Explainability Sandbox** is a human-centered interpretation tool that transforms XAI from raw metrics into actionable insights. It replaces the old "Research Lab" with a focus on **understanding, interpreting, and communicating** AI explanations.

---

## 🎨 Frontend Implementation

### ✅ **COMPLETED**

1. **New Page Created:** `/sandbox`
   - File: `frontend/src/app/sandbox/page.tsx`
   - Route: `https://your-app.com/sandbox`

2. **Navigation Updated:**
   - "Research" → "Sandbox" in navbar
   - Protected route added to middleware

3. **Key Features Implemented:**
   - ✅ Model Context Panel (select model, view dataset)
   - ✅ SHAP vs LIME Comparison (side-by-side)
   - ✅ Human-Readable Interpretation Layer
   - ✅ Feature Contribution Visualization
   - ✅ Disagreement Detection
   - ✅ Human Interpretability Rating (Clarity, Trust, Actionability)
   - ✅ Global vs Local Toggle (UI ready)
   - ✅ What-If Analysis (UI ready)

4. **API Methods Added:**
   - `explanationsAPI.getSampleInstance(modelId)`
   - `explanationsAPI.getLocalExplanation(modelId, instanceId, method)`
   - `explanationsAPI.whatIfAnalysis(modelId, instanceId, feature, newValue)`
   - `explanationsAPI.submitInterpretabilityRating(data)`

---

## 🔧 Backend Implementation Needed

### **Priority 1: Core Endpoints** (Required for basic functionality)

#### **1. GET `/api/v1/explanations/sample/{model_id}`**
**Purpose:** Return a random test sample with model prediction

**Response:**
```json
{
  "instance_id": "sample_123",
  "features": {
    "TransactionAmt": 850.50,
    "card_type": "credit",
    "merchant_category": "retail",
    "transaction_time": "14:30",
    "user_history_days": 45
  },
  "prediction": 0.91,
  "model_output": "Fraud",
  "true_label": "Fraud"
}
```

**Implementation:**
```python
@router.get("/sample/{model_id}")
async def get_sample_instance(
    model_id: str,
    db: Session = Depends(get_db)
):
    # 1. Load model
    model = db.query(Model).filter(Model.model_id == model_id).first()
    
    # 2. Get random test sample
    X_test, y_test = load_test_data(model.dataset_id)
    random_idx = random.randint(0, len(X_test) - 1)
    sample = X_test.iloc[random_idx]
    
    # 3. Get prediction
    loaded_model = joblib.load(f"models/{model_id}.pkl")
    prediction = loaded_model.predict_proba([sample.values])[0][1]
    
    return {
        "instance_id": f"sample_{random_idx}",
        "features": sample.to_dict(),
        "prediction": float(prediction),
        "model_output": "Fraud" if prediction > 0.5 else "Not Fraud",
        "true_label": "Fraud" if y_test.iloc[random_idx] == 1 else "Not Fraud"
    }
```

---

#### **2. GET `/api/v1/explanations/local/{model_id}/{instance_id}?method=shap`**
**Purpose:** Get SHAP or LIME explanation for a specific instance

**Response:**
```json
{
  "method": "shap",
  "prediction_proba": 0.91,
  "base_value": 0.15,
  "features": [
    {
      "feature": "TransactionAmt",
      "value": 850.50,
      "contribution": 0.23,
      "importance": 0.45
    },
    {
      "feature": "user_history_days",
      "value": 45,
      "contribution": 0.18,
      "importance": 0.35
    },
    {
      "feature": "card_type",
      "value": "credit",
      "contribution": -0.11,
      "importance": 0.20
    }
  ]
}
```

**Implementation:**
```python
@router.get("/local/{model_id}/{instance_id}")
async def get_local_explanation(
    model_id: str,
    instance_id: str,
    method: str = "shap",
    db: Session = Depends(get_db)
):
    # 1. Load model and sample
    model = db.query(Model).filter(Model.model_id == model_id).first()
    sample_idx = int(instance_id.split("_")[1])
    X_test, _ = load_test_data(model.dataset_id)
    sample = X_test.iloc[sample_idx]
    
    # 2. Load model
    loaded_model = joblib.load(f"models/{model_id}.pkl")
    prediction = loaded_model.predict_proba([sample.values])[0][1]
    
    # 3. Generate explanation
    if method == "shap":
        explainer = shap.TreeExplainer(loaded_model)
        shap_values = explainer.shap_values(sample.values.reshape(1, -1))
        base_value = explainer.expected_value[1]
        
        features = []
        for i, (feature_name, feature_value) in enumerate(sample.items()):
            features.append({
                "feature": feature_name,
                "value": feature_value,
                "contribution": float(shap_values[1][0][i]),
                "importance": abs(float(shap_values[1][0][i]))
            })
        
        # Sort by importance
        features.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "method": "shap",
            "prediction_proba": float(prediction),
            "base_value": float(base_value),
            "features": features
        }
    
    elif method == "lime":
        explainer = lime.lime_tabular.LimeTabularExplainer(
            X_test.values,
            feature_names=X_test.columns.tolist(),
            class_names=['Not Fraud', 'Fraud'],
            mode='classification'
        )
        
        exp = explainer.explain_instance(
            sample.values,
            loaded_model.predict_proba,
            num_features=len(sample)
        )
        
        features = []
        for feature_idx, contribution in exp.as_list():
            feature_name = X_test.columns[feature_idx]
            features.append({
                "feature": feature_name,
                "value": sample[feature_name],
                "contribution": float(contribution),
                "importance": abs(float(contribution))
            })
        
        features.sort(key=lambda x: x["importance"], reverse=True)
        
        return {
            "method": "lime",
            "prediction_proba": float(prediction),
            "features": features
        }
```

---

### **Priority 2: Advanced Features** (Optional but valuable)

#### **3. POST `/api/v1/explanations/what-if`**
**Purpose:** Simulate changing a feature value and see impact

**Request:**
```json
{
  "model_id": "xgboost_123",
  "instance_id": "sample_45",
  "feature": "TransactionAmt",
  "new_value": 200.0
}
```

**Response:**
```json
{
  "original_prediction": 0.91,
  "new_prediction": 0.56,
  "prediction_change": -0.35,
  "shap": { /* updated SHAP explanation */ },
  "lime": { /* updated LIME explanation */ }
}
```

**Implementation:**
```python
@router.post("/what-if")
async def what_if_analysis(
    data: WhatIfRequest,
    db: Session = Depends(get_db)
):
    # 1. Load original sample
    sample_idx = int(data.instance_id.split("_")[1])
    X_test, _ = load_test_data(model.dataset_id)
    original_sample = X_test.iloc[sample_idx].copy()
    
    # 2. Create modified sample
    modified_sample = original_sample.copy()
    modified_sample[data.feature] = data.new_value
    
    # 3. Get new prediction
    loaded_model = joblib.load(f"models/{data.model_id}.pkl")
    original_pred = loaded_model.predict_proba([original_sample.values])[0][1]
    new_pred = loaded_model.predict_proba([modified_sample.values])[0][1]
    
    # 4. Generate new explanations
    shap_exp = generate_shap_explanation(loaded_model, modified_sample)
    lime_exp = generate_lime_explanation(loaded_model, modified_sample, X_test)
    
    return {
        "original_prediction": float(original_pred),
        "new_prediction": float(new_pred),
        "prediction_change": float(new_pred - original_pred),
        "shap": shap_exp,
        "lime": lime_exp
    }
```

---

#### **4. POST `/api/v1/explanations/rating`**
**Purpose:** Save human interpretability ratings for research

**Request:**
```json
{
  "model_id": "xgboost_123",
  "instance_id": "sample_45",
  "clarity": 4,
  "trustworthiness": 5,
  "actionability": 3,
  "shap_method": "shap",
  "lime_method": "lime"
}
```

**Response:**
```json
{
  "rating_id": "rating_789",
  "message": "Rating saved successfully"
}
```

**Implementation:**
```python
@router.post("/rating")
async def submit_interpretability_rating(
    data: InterpretabilityRating,
    db: Session = Depends(get_db)
):
    # Save to database for thesis research
    rating = ExplanationRating(
        model_id=data.model_id,
        instance_id=data.instance_id,
        clarity=data.clarity,
        trustworthiness=data.trustworthiness,
        actionability=data.actionability,
        shap_method=data.shap_method,
        lime_method=data.lime_method,
        timestamp=datetime.utcnow()
    )
    
    db.add(rating)
    db.commit()
    
    return {
        "rating_id": f"rating_{rating.id}",
        "message": "Rating saved successfully"
    }
```

---

### **Priority 3: Global View** (Future enhancement)

#### **5. GET `/api/v1/explanations/global/{model_id}`**
**Purpose:** Get averaged SHAP importances across entire dataset

**Response:**
```json
{
  "global_importances": [
    {
      "feature": "TransactionAmt",
      "mean_importance": 0.45,
      "std_importance": 0.12
    },
    {
      "feature": "user_history_days",
      "mean_importance": 0.35,
      "std_importance": 0.08
    }
  ]
}
```

---

## 📊 Database Schema Updates

### **New Table: `explanation_ratings`**
```sql
CREATE TABLE explanation_ratings (
    id SERIAL PRIMARY KEY,
    model_id VARCHAR(255) NOT NULL,
    instance_id VARCHAR(255) NOT NULL,
    clarity INTEGER CHECK (clarity BETWEEN 1 AND 5),
    trustworthiness INTEGER CHECK (trustworthiness BETWEEN 1 AND 5),
    actionability INTEGER CHECK (actionability BETWEEN 1 AND 5),
    shap_method VARCHAR(50),
    lime_method VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id)
);
```

---

## 🎯 User Flow

1. **User logs in** → Navigates to "Sandbox"
2. **Selects a trained model** from dropdown
3. **Clicks "Load Sample Prediction"** → Backend returns random test instance
4. **Views SHAP vs LIME** side-by-side with:
   - Feature contributions (bars)
   - Human-readable tooltips
   - Prediction probability
5. **Reads interpretation** → AI-generated summary explains key drivers
6. **Rates explanation** → Submits clarity/trust/actionability scores
7. **(Optional) What-If Analysis** → Tweaks feature, sees impact

---

## 🚀 Deployment Steps

### **Frontend (Already Done)**
```bash
cd frontend
npm run build
# Deploy to Netlify (auto-deploys from GitHub)
```

### **Backend (TODO)**
1. Add new endpoints to `backend/app/api/v1/endpoints/explanations.py`
2. Create database migration for `explanation_ratings` table
3. Test endpoints locally
4. Deploy backend

---

## 🧪 Testing Checklist

- [ ] Load sample instance works
- [ ] SHAP explanation displays correctly
- [ ] LIME explanation displays correctly
- [ ] Interpretation text generates
- [ ] Disagreement detection works
- [ ] Rating submission saves to database
- [ ] What-if analysis updates predictions
- [ ] Global view shows averaged importances

---

## 📈 Benefits for Thesis

### **1. Human-Centered XAI**
- Moves beyond metrics to **understanding**
- Demonstrates **interpretability** in practice
- Shows **communication** of AI decisions

### **2. Research Data Collection**
- Collect human ratings (clarity, trust, actionability)
- Compare SHAP vs LIME from user perspective
- Identify disagreements between methods

### **3. Interactive Demonstration**
- What-if analysis shows **causal reasoning**
- Side-by-side comparison highlights **method differences**
- Natural language interpretation bridges **AI ↔ Human gap**

---

## 🎓 Thesis Integration

### **Chapter Alignment:**
- **Chapter 3 (Methodology):** Sandbox as evaluation tool
- **Chapter 4 (Implementation):** Technical architecture
- **Chapter 5 (Evaluation):** Human study results from ratings
- **Chapter 6 (Discussion):** SHAP vs LIME insights

### **Key Contributions:**
1. ✅ **Interactive XAI exploration** (not just static reports)
2. ✅ **Human interpretability metrics** (clarity, trust, actionability)
3. ✅ **Method comparison** (SHAP vs LIME disagreements)
4. ✅ **Causal reasoning** (what-if analysis)

---

## 📝 Next Steps

1. **Implement backend endpoints** (Priority 1 first)
2. **Test with real models** (use trained XGBoost/RF)
3. **Collect pilot data** (5-10 users rating explanations)
4. **Refine interpretation** (improve AI-generated summaries)
5. **Add LLM summarizer** (optional: GPT-4 for better text)

---

## 🎉 Summary

The **Explainability Sandbox** transforms your platform from a "model training tool" into a **human-centered XAI research platform**. It directly supports your thesis by:

- ✅ Demonstrating **interpretability** (not just accuracy)
- ✅ Collecting **human evaluation data**
- ✅ Comparing **explanation methods**
- ✅ Enabling **interactive exploration**

**This is the core differentiator for your thesis!** 🚀
