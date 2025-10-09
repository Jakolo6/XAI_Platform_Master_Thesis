"""Human study models."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class StudySession(Base):
    """Human study session tracking."""
    
    __tablename__ = "study_sessions"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, unique=True, nullable=False, index=True)  # Pseudonymous ID
    
    # Session configuration
    has_explanations = Column(Boolean, nullable=False)  # 50% yes, 50% no
    model_id = Column(String, ForeignKey("models.id"), nullable=False)
    
    # Session metadata
    user_agent = Column(String)
    ip_hash = Column(String)  # Hashed for privacy
    
    # Completion tracking
    total_interactions = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True))


class StudyInteraction(Base):
    """Individual study interaction."""
    
    __tablename__ = "study_interactions"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("study_sessions.id"), nullable=False, index=True)
    
    # Transaction data
    transaction_id = Column(String, nullable=False)
    transaction_data = Column(JSON)
    
    # Model prediction
    predicted_fraud = Column(Boolean, nullable=False)
    prediction_probability = Column(Float, nullable=False)
    
    # Explanation (if applicable)
    explanation_id = Column(String, ForeignKey("explanations.id"))
    explanation_shown = Column(Boolean, default=False)
    
    # User response
    user_decision = Column(Boolean)  # User's fraud decision
    confidence_level = Column(Integer)  # 1-7 scale
    trust_level = Column(Integer)  # 1-7 scale
    response_time_seconds = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
