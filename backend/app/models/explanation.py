"""Explanation and metrics models."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ExplanationMethod(str, enum.Enum):
    """XAI explanation methods."""
    SHAP_TREE = "shap_tree"
    SHAP_KERNEL = "shap_kernel"
    LIME = "lime"


class Explanation(Base):
    """XAI explanation tracking."""
    
    __tablename__ = "explanations"
    
    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, ForeignKey("models.id"), nullable=False, index=True)
    method = Column(SQLEnum(ExplanationMethod), nullable=False, index=True)
    
    # Explanation type
    is_global = Column(Boolean, default=False, nullable=False)
    instance_id = Column(String)  # For local explanations
    
    # Explanation data
    explanation_data = Column(JSON)  # SHAP values, LIME weights, etc.
    feature_importance = Column(JSON)
    
    # Storage
    file_path = Column(String)  # Supabase path for large explanations
    file_size_mb = Column(Float)
    
    # Caching
    cache_key = Column(String, unique=True, index=True)
    cached_until = Column(DateTime(timezone=True))
    
    # Computation info
    computation_time_seconds = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class ExplanationMetrics(Base):
    """Explanation quality metrics."""
    
    __tablename__ = "explanation_metrics"
    
    id = Column(String, primary_key=True, index=True)
    explanation_id = Column(String, ForeignKey("explanations.id"), nullable=False, index=True)
    
    # Faithfulness metrics
    faithfulness_correlation = Column(Float)
    faithfulness_estimate = Column(Float)
    
    # Stability metrics
    max_sensitivity = Column(Float)
    avg_sensitivity = Column(Float)
    
    # Sparsity metrics
    sparseness = Column(Float)
    complexity = Column(Float)
    
    # Additional Quantus metrics
    additional_metrics = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
