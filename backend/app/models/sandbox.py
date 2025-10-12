"""
Database models for Explainability Sandbox
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.db.base_class import Base

class SandboxInstance(Base):
    """Stores test samples used in sandbox for reproducibility"""
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
    """Stores human interpretability ratings for research"""
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
