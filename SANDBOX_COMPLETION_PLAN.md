# 🎯 EXPLAINABILITY SANDBOX - COMPLETE IMPLEMENTATION PLAN

## 📋 OVERVIEW

This is a **step-by-step plan** to fully implement the Explainability Sandbox with:
- ✅ NO mock data
- ✅ Full backend integration
- ✅ Real SHAP/LIME explanations
- ✅ Database persistence
- ✅ Production-ready code

---

## 🗂️ PHASE 1: BACKEND FOUNDATION (Priority: CRITICAL)

### **Step 1.1: Create Database Schema**
**File:** `backend/migrations/3_sandbox_schema.sql`

```sql
-- Table for storing sample instances used in sandbox
CREATE TABLE IF NOT EXISTS sandbox_instances (
    id SERIAL PRIMARY KEY,
    instance_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    sample_index INTEGER NOT NULL,
    features JSONB NOT NULL,
    prediction FLOAT NOT NULL,
    true_label VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

-- Table for storing explanation ratings (human study data)
CREATE TABLE IF NOT EXISTS explanation_ratings (
    id SERIAL PRIMARY KEY,
    rating_id VARCHAR(255) UNIQUE NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    instance_id VARCHAR(255) NOT NULL,
    clarity INTEGER CHECK (clarity BETWEEN 1 AND 5),
    trustworthiness INTEGER CHECK (trustworthiness BETWEEN 1 AND 5),
    actionability INTEGER CHECK (actionability BETWEEN 1 AND 5),
    shap_method VARCHAR(50) DEFAULT 'shap',
    lime_method VARCHAR(50) DEFAULT 'lime',
    user_email VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(model_id) ON DELETE CASCADE
);

-- Index for faster queries
CREATE INDEX idx_sandbox_instances_model ON sandbox_instances(model_id);
CREATE INDEX idx_ratings_model ON explanation_ratings(model_id);
CREATE INDEX idx_ratings_created ON explanation_ratings(created_at);
```

**Action:** Run this migration
```bash
cd backend
psql -U postgres -d xai_platform -f migrations/3_sandbox_schema.sql
```

---

### **Step 1.2: Create Pydantic Models**
**File:** `backend/app/schemas/sandbox.py`

```python
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class SampleInstance(BaseModel):
    instance_id: str
    features: Dict[str, Any]
    prediction: float
    model_output: str
    true_label: Optional[str] = None

class FeatureContribution(BaseModel):
    feature: str
    value: Any
    contribution: float
    importance: float

class ExplanationData(BaseModel):
    method: str  # 'shap' or 'lime'
    prediction_proba: float
    base_value: Optional[float] = None
    features: List[FeatureContribution]

class WhatIfRequest(BaseModel):
    model_id: str
    instance_id: str
    feature: str
    new_value: float

class WhatIfResponse(BaseModel):
    original_prediction: float
    new_prediction: float
    prediction_change: float
    shap: ExplanationData
    lime: ExplanationData

class InterpretabilityRating(BaseModel):
    model_id: str
    instance_id: str
    clarity: int = Field(..., ge=1, le=5)
    trustworthiness: int = Field(..., ge=1, le=5)
    actionability: int = Field(..., ge=1, le=5)
    shap_method: str = 'shap'
    lime_method: str = 'lime'

class RatingResponse(BaseModel):
    rating_id: str
    message: str
```

---

### **Step 1.3: Create Sandbox Service**
**File:** `backend/app/services/sandbox_service.py`

```python
import numpy as np
import pandas as pd
import shap
import lime
import lime.lime_tabular
import joblib
import random
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.model import Model
from app.schemas.sandbox import (
    SampleInstance, ExplanationData, FeatureContribution
)

class SandboxService:
    """Service for Explainability Sandbox operations"""
    
    @staticmethod
    def load_test_data(dataset_id: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load test data for a dataset"""
        # Load preprocessed test data
        test_path = f"data/processed/{dataset_id}_test.csv"
        df = pd.read_csv(test_path)
        
        # Separate features and target
        target_col = 'isFraud' if 'isFraud' in df.columns else 'target'
        X_test = df.drop(columns=[target_col])
        y_test = df[target_col]
        
        return X_test, y_test
    
    @staticmethod
    def get_sample_instance(
        model_id: str, 
        db: Session
    ) -> SampleInstance:
        """Get a random test sample with prediction"""
        
        # Load model from database
        model = db.query(Model).filter(Model.model_id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Load test data
        X_test, y_test = SandboxService.load_test_data(model.dataset_id)
        
        # Select random sample
        random_idx = random.randint(0, len(X_test) - 1)
        sample = X_test.iloc[random_idx]
        true_label = y_test.iloc[random_idx]
        
        # Load trained model
        model_path = f"models/{model_id}.pkl"
        loaded_model = joblib.load(model_path)
        
        # Get prediction
        prediction_proba = loaded_model.predict_proba([sample.values])[0][1]
        prediction_class = 1 if prediction_proba > 0.5 else 0
        
        # Determine output label
        if model.dataset_id == 'ieee-cis-fraud':
            model_output = "Fraud" if prediction_class == 1 else "Not Fraud"
            true_output = "Fraud" if true_label == 1 else "Not Fraud"
        else:
            model_output = f"Class {prediction_class}"
            true_output = f"Class {true_label}"
        
        return SampleInstance(
            instance_id=f"sample_{random_idx}",
            features=sample.to_dict(),
            prediction=float(prediction_proba),
            model_output=model_output,
            true_label=true_output
        )
    
    @staticmethod
    def generate_shap_explanation(
        model_id: str,
        instance_id: str,
        db: Session
    ) -> ExplanationData:
        """Generate SHAP explanation for a specific instance"""
        
        # Load model
        model = db.query(Model).filter(Model.model_id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Load test data
        X_test, y_test = SandboxService.load_test_data(model.dataset_id)
        
        # Get sample
        sample_idx = int(instance_id.split("_")[1])
        sample = X_test.iloc[sample_idx]
        
        # Load trained model
        model_path = f"models/{model_id}.pkl"
        loaded_model = joblib.load(model_path)
        
        # Get prediction
        prediction_proba = loaded_model.predict_proba([sample.values])[0][1]
        
        # Generate SHAP explanation
        explainer = shap.TreeExplainer(loaded_model)
        shap_values = explainer.shap_values(sample.values.reshape(1, -1))
        
        # Handle different SHAP output formats
        if isinstance(shap_values, list):
            shap_values_class = shap_values[1][0]  # For binary classification
            base_value = explainer.expected_value[1]
        else:
            shap_values_class = shap_values[0]
            base_value = explainer.expected_value
        
        # Create feature contributions
        features = []
        for i, (feature_name, feature_value) in enumerate(sample.items()):
            contribution = float(shap_values_class[i])
            features.append(FeatureContribution(
                feature=feature_name,
                value=feature_value,
                contribution=contribution,
                importance=abs(contribution)
            ))
        
        # Sort by importance
        features.sort(key=lambda x: x.importance, reverse=True)
        
        return ExplanationData(
            method='shap',
            prediction_proba=float(prediction_proba),
            base_value=float(base_value),
            features=features
        )
    
    @staticmethod
    def generate_lime_explanation(
        model_id: str,
        instance_id: str,
        db: Session
    ) -> ExplanationData:
        """Generate LIME explanation for a specific instance"""
        
        # Load model
        model = db.query(Model).filter(Model.model_id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Load test data
        X_test, y_test = SandboxService.load_test_data(model.dataset_id)
        
        # Get sample
        sample_idx = int(instance_id.split("_")[1])
        sample = X_test.iloc[sample_idx]
        
        # Load trained model
        model_path = f"models/{model_id}.pkl"
        loaded_model = joblib.load(model_path)
        
        # Get prediction
        prediction_proba = loaded_model.predict_proba([sample.values])[0][1]
        
        # Generate LIME explanation
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
        
        # Create feature contributions
        features = []
        lime_dict = dict(exp.as_list())
        
        for i, (feature_name, feature_value) in enumerate(sample.items()):
            # Find contribution in LIME output
            contribution = 0.0
            for lime_feature, lime_contrib in lime_dict.items():
                if feature_name in lime_feature:
                    contribution = lime_contrib
                    break
            
            features.append(FeatureContribution(
                feature=feature_name,
                value=feature_value,
                contribution=float(contribution),
                importance=abs(float(contribution))
            ))
        
        # Sort by importance
        features.sort(key=lambda x: x.importance, reverse=True)
        
        return ExplanationData(
            method='lime',
            prediction_proba=float(prediction_proba),
            features=features
        )
    
    @staticmethod
    def what_if_analysis(
        model_id: str,
        instance_id: str,
        feature: str,
        new_value: float,
        db: Session
    ) -> Dict[str, Any]:
        """Perform what-if analysis by changing a feature value"""
        
        # Load model
        model = db.query(Model).filter(Model.model_id == model_id).first()
        if not model:
            raise ValueError(f"Model {model_id} not found")
        
        # Load test data
        X_test, y_test = SandboxService.load_test_data(model.dataset_id)
        
        # Get original sample
        sample_idx = int(instance_id.split("_")[1])
        original_sample = X_test.iloc[sample_idx].copy()
        
        # Load trained model
        model_path = f"models/{model_id}.pkl"
        loaded_model = joblib.load(model_path)
        
        # Get original prediction
        original_pred = loaded_model.predict_proba([original_sample.values])[0][1]
        
        # Create modified sample
        modified_sample = original_sample.copy()
        modified_sample[feature] = new_value
        
        # Get new prediction
        new_pred = loaded_model.predict_proba([modified_sample.values])[0][1]
        
        # Generate new SHAP explanation
        explainer = shap.TreeExplainer(loaded_model)
        shap_values = explainer.shap_values(modified_sample.values.reshape(1, -1))
        
        if isinstance(shap_values, list):
            shap_values_class = shap_values[1][0]
            base_value = explainer.expected_value[1]
        else:
            shap_values_class = shap_values[0]
            base_value = explainer.expected_value
        
        shap_features = []
        for i, (feat_name, feat_value) in enumerate(modified_sample.items()):
            contribution = float(shap_values_class[i])
            shap_features.append(FeatureContribution(
                feature=feat_name,
                value=feat_value,
                contribution=contribution,
                importance=abs(contribution)
            ))
        shap_features.sort(key=lambda x: x.importance, reverse=True)
        
        # Generate new LIME explanation
        lime_explainer = lime.lime_tabular.LimeTabularExplainer(
            X_test.values,
            feature_names=X_test.columns.tolist(),
            class_names=['Not Fraud', 'Fraud'],
            mode='classification'
        )
        
        lime_exp = lime_explainer.explain_instance(
            modified_sample.values,
            loaded_model.predict_proba,
            num_features=len(modified_sample)
        )
        
        lime_features = []
        lime_dict = dict(lime_exp.as_list())
        
        for i, (feat_name, feat_value) in enumerate(modified_sample.items()):
            contribution = 0.0
            for lime_feature, lime_contrib in lime_dict.items():
                if feat_name in lime_feature:
                    contribution = lime_contrib
                    break
            
            lime_features.append(FeatureContribution(
                feature=feat_name,
                value=feat_value,
                contribution=float(contribution),
                importance=abs(float(contribution))
            ))
        lime_features.sort(key=lambda x: x.importance, reverse=True)
        
        return {
            'original_prediction': float(original_pred),
            'new_prediction': float(new_pred),
            'prediction_change': float(new_pred - original_pred),
            'shap': ExplanationData(
                method='shap',
                prediction_proba=float(new_pred),
                base_value=float(base_value),
                features=shap_features
            ),
            'lime': ExplanationData(
                method='lime',
                prediction_proba=float(new_pred),
                features=lime_features
            )
        }
```

---

### **Step 1.4: Create Sandbox API Endpoints**
**File:** `backend/app/api/v1/endpoints/sandbox.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid
from datetime import datetime

from app.api.deps import get_db
from app.services.sandbox_service import SandboxService
from app.schemas.sandbox import (
    SampleInstance,
    ExplanationData,
    WhatIfRequest,
    WhatIfResponse,
    InterpretabilityRating,
    RatingResponse
)
from app.models.model import Model

router = APIRouter()

@router.get("/sample/{model_id}", response_model=SampleInstance)
async def get_sample_instance(
    model_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a random test sample with prediction for sandbox exploration
    """
    try:
        return SandboxService.get_sample_instance(model_id, db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Test data not found for model {model_id}. Please ensure dataset is processed."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load sample: {str(e)}")

@router.get("/local/{model_id}/{instance_id}", response_model=ExplanationData)
async def get_local_explanation(
    model_id: str,
    instance_id: str,
    method: str = 'shap',
    db: Session = Depends(get_db)
):
    """
    Get SHAP or LIME explanation for a specific instance
    """
    try:
        if method.lower() == 'shap':
            return SandboxService.generate_shap_explanation(model_id, instance_id, db)
        elif method.lower() == 'lime':
            return SandboxService.generate_lime_explanation(model_id, instance_id, db)
        else:
            raise HTTPException(status_code=400, detail=f"Invalid method: {method}. Use 'shap' or 'lime'")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

@router.post("/what-if", response_model=WhatIfResponse)
async def what_if_analysis(
    request: WhatIfRequest,
    db: Session = Depends(get_db)
):
    """
    Perform what-if analysis by changing a feature value
    """
    try:
        result = SandboxService.what_if_analysis(
            request.model_id,
            request.instance_id,
            request.feature,
            request.new_value,
            db
        )
        return WhatIfResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"What-if analysis failed: {str(e)}")

@router.post("/rating", response_model=RatingResponse)
async def submit_interpretability_rating(
    rating: InterpretabilityRating,
    db: Session = Depends(get_db)
):
    """
    Submit human interpretability rating for research purposes
    """
    try:
        # Generate unique rating ID
        rating_id = f"rating_{uuid.uuid4().hex[:12]}"
        
        # Save to database
        from app.models.sandbox import ExplanationRating
        
        db_rating = ExplanationRating(
            rating_id=rating_id,
            model_id=rating.model_id,
            instance_id=rating.instance_id,
            clarity=rating.clarity,
            trustworthiness=rating.trustworthiness,
            actionability=rating.actionability,
            shap_method=rating.shap_method,
            lime_method=rating.lime_method,
            created_at=datetime.utcnow()
        )
        
        db.add(db_rating)
        db.commit()
        db.refresh(db_rating)
        
        return RatingResponse(
            rating_id=rating_id,
            message="Rating saved successfully. Thank you for your feedback!"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save rating: {str(e)}")
```

---

### **Step 1.5: Create Database Models**
**File:** `backend/app/models/sandbox.py`

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class SandboxInstance(Base):
    __tablename__ = "sandbox_instances"
    
    id = Column(Integer, primary_key=True, index=True)
    instance_id = Column(String(255), unique=True, nullable=False, index=True)
    model_id = Column(String(255), ForeignKey("models.model_id", ondelete="CASCADE"), nullable=False)
    sample_index = Column(Integer, nullable=False)
    features = Column(JSON, nullable=False)
    prediction = Column(Float, nullable=False)
    true_label = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExplanationRating(Base):
    __tablename__ = "explanation_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    rating_id = Column(String(255), unique=True, nullable=False, index=True)
    model_id = Column(String(255), ForeignKey("models.model_id", ondelete="CASCADE"), nullable=False)
    instance_id = Column(String(255), nullable=False)
    clarity = Column(Integer, nullable=False)
    trustworthiness = Column(Integer, nullable=False)
    actionability = Column(Integer, nullable=False)
    shap_method = Column(String(50), default='shap')
    lime_method = Column(String(50), default='lime')
    user_email = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

---

### **Step 1.6: Register Sandbox Routes**
**File:** `backend/app/api/v1/api.py`

Add this line:
```python
from app.api.v1.endpoints import sandbox

api_router.include_router(sandbox.router, prefix="/explanations", tags=["sandbox"])
```

---

## 🗂️ PHASE 2: FRONTEND FIXES (Priority: HIGH)

### **Step 2.1: Fix API Endpoint Paths**
**File:** `frontend/src/lib/api.ts`

Update the sandbox endpoints to match backend:
```typescript
// Sandbox-specific endpoints
getSampleInstance: (modelId: string) => 
  api.get(`/explanations/sample/${modelId}`),

getLocalExplanation: (modelId: string, instanceId: string, method: string) =>
  api.get(`/explanations/local/${modelId}/${instanceId}`, { params: { method } }),

whatIfAnalysis: (modelId: string, instanceId: string, feature: string, newValue: number) =>
  api.post(`/explanations/what-if`, { 
    model_id: modelId, 
    instance_id: instanceId, 
    feature, 
    new_value: newValue 
  }),

submitInterpretabilityRating: (data: {
  model_id: string;
  instance_id: string;
  clarity: number;
  trustworthiness: number;
  actionability: number;
  shap_method: string;
  lime_method: string;
}) => api.post('/explanations/rating', data),
```

---

### **Step 2.2: Add Error Boundaries**
**File:** `frontend/src/app/sandbox/page.tsx`

Already implemented! ✅

---

### **Step 2.3: Add Loading States**
**File:** `frontend/src/app/sandbox/page.tsx`

Already implemented! ✅

---

## 🗂️ PHASE 3: TESTING & VALIDATION (Priority: MEDIUM)

### **Step 3.1: Backend Unit Tests**
**File:** `backend/tests/test_sandbox.py`

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_sample_instance():
    # Assumes you have a trained model with ID 'test_model_123'
    response = client.get("/api/v1/explanations/sample/test_model_123")
    assert response.status_code == 200
    data = response.json()
    assert "instance_id" in data
    assert "features" in data
    assert "prediction" in data

def test_get_shap_explanation():
    response = client.get(
        "/api/v1/explanations/local/test_model_123/sample_0",
        params={"method": "shap"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["method"] == "shap"
    assert "features" in data

def test_submit_rating():
    rating_data = {
        "model_id": "test_model_123",
        "instance_id": "sample_0",
        "clarity": 5,
        "trustworthiness": 4,
        "actionability": 3,
        "shap_method": "shap",
        "lime_method": "lime"
    }
    response = client.post("/api/v1/explanations/rating", json=rating_data)
    assert response.status_code == 200
    data = response.json()
    assert "rating_id" in data
```

---

### **Step 3.2: Integration Test**
**Manual Test Flow:**

1. Train a model (XGBoost on ieee-cis-fraud)
2. Navigate to `/sandbox`
3. Select the trained model
4. Click "Load Sample Prediction"
5. Verify SHAP and LIME explanations load
6. Submit a rating
7. Check database for saved rating

---

## 🗂️ PHASE 4: DEPLOYMENT (Priority: LOW)

### **Step 4.1: Backend Deployment**
```bash
# Run migrations
cd backend
alembic upgrade head

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### **Step 4.2: Frontend Deployment**
```bash
# Build frontend
cd frontend
npm run build

# Deploy to Netlify (auto-deploys from GitHub)
git push origin main
```

---

## 📊 COMPLETION CHECKLIST

### **Backend:**
- [ ] Step 1.1: Database schema created
- [ ] Step 1.2: Pydantic models created
- [ ] Step 1.3: Sandbox service implemented
- [ ] Step 1.4: API endpoints created
- [ ] Step 1.5: Database models created
- [ ] Step 1.6: Routes registered
- [ ] Step 3.1: Unit tests written
- [ ] Step 3.2: Integration test passed

### **Frontend:**
- [x] Sandbox page created
- [x] API methods added
- [x] Navigation updated
- [x] Error handling implemented
- [x] Loading states implemented
- [ ] Step 2.1: API paths verified

### **Testing:**
- [ ] Sample instance loads
- [ ] SHAP explanation works
- [ ] LIME explanation works
- [ ] Interpretation generates
- [ ] Rating saves to database
- [ ] What-if analysis works

### **Deployment:**
- [ ] Backend deployed
- [ ] Frontend deployed
- [ ] Database migrations run
- [ ] Environment variables set

---

## 🚀 ESTIMATED TIME

| Phase | Time | Priority |
|-------|------|----------|
| Phase 1: Backend Foundation | 4-6 hours | CRITICAL |
| Phase 2: Frontend Fixes | 30 minutes | HIGH |
| Phase 3: Testing | 1-2 hours | MEDIUM |
| Phase 4: Deployment | 1 hour | LOW |
| **TOTAL** | **6-9 hours** | - |

---

## 🎯 SUCCESS CRITERIA

✅ **User can:**
1. Select a trained model
2. Load a real test sample
3. See SHAP explanation (real, not mock)
4. See LIME explanation (real, not mock)
5. Read AI-generated interpretation
6. Submit rating (saves to database)
7. Perform what-if analysis (optional)

✅ **NO MOCK DATA ANYWHERE**
✅ **ALL ERRORS HANDLED GRACEFULLY**
✅ **PRODUCTION-READY CODE**

---

## 📝 NEXT IMMEDIATE ACTIONS

1. **Create database migration** (Step 1.1)
2. **Create Pydantic models** (Step 1.2)
3. **Implement sandbox service** (Step 1.3)
4. **Create API endpoints** (Step 1.4)
5. **Test with Postman/curl**
6. **Verify frontend integration**

**START WITH STEP 1.1 NOW!** 🚀
