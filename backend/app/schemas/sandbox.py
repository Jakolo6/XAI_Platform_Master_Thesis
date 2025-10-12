"""
Pydantic schemas for Explainability Sandbox
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime

class SampleInstance(BaseModel):
    """A test sample with model prediction"""
    instance_id: str
    features: Dict[str, Any]
    prediction: float
    model_output: str
    true_label: Optional[str] = None

class FeatureContribution(BaseModel):
    """Feature contribution from SHAP or LIME"""
    feature: str
    value: Any
    contribution: float
    importance: float

class ExplanationData(BaseModel):
    """Explanation data from SHAP or LIME"""
    method: str  # 'shap' or 'lime'
    prediction_proba: float
    base_value: Optional[float] = None
    features: List[FeatureContribution]

class WhatIfRequest(BaseModel):
    """Request for what-if analysis"""
    model_id: str
    instance_id: str
    feature: str
    new_value: float

class WhatIfResponse(BaseModel):
    """Response from what-if analysis"""
    original_prediction: float
    new_prediction: float
    prediction_change: float
    shap: ExplanationData
    lime: ExplanationData

class InterpretabilityRating(BaseModel):
    """Human interpretability rating"""
    model_id: str
    instance_id: str
    clarity: int = Field(..., ge=1, le=5, description="How clear and understandable (1-5)")
    trustworthiness: int = Field(..., ge=1, le=5, description="How much you trust it (1-5)")
    actionability: int = Field(..., ge=1, le=5, description="Can you act on it (1-5)")
    shap_method: str = 'shap'
    lime_method: str = 'lime'

class RatingResponse(BaseModel):
    """Response after submitting rating"""
    rating_id: str
    message: str
