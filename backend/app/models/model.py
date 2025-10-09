"""Model and metrics models."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey, Boolean
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class ModelStatus(str, enum.Enum):
    """Model training status."""
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"


class Model(Base):
    """ML model tracking."""
    
    __tablename__ = "models"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    model_type = Column(String, nullable=False, index=True)  # xgboost, random_forest, etc.
    version = Column(String, nullable=False)
    
    # Dataset reference
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False, index=True)
    
    # Training status
    status = Column(SQLEnum(ModelStatus), default=ModelStatus.PENDING, nullable=False)
    
    # Model configuration
    hyperparameters = Column(JSON)
    training_config = Column(JSON)
    
    # Model storage
    model_path = Column(String)  # Supabase path
    model_hash = Column(String, unique=True, index=True)  # SHA256 hash for versioning
    model_size_mb = Column(Float)
    
    # Training metrics
    training_time_seconds = Column(Float)
    
    # Error tracking
    error_message = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))


class ModelMetrics(Base):
    """Model performance metrics."""
    
    __tablename__ = "model_metrics"
    
    id = Column(String, primary_key=True, index=True)
    model_id = Column(String, ForeignKey("models.id"), nullable=False, index=True)
    
    # Classification metrics
    auc_roc = Column(Float)
    auc_pr = Column(Float)
    f1_score = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    accuracy = Column(Float)
    log_loss = Column(Float)
    brier_score = Column(Float)
    
    # Calibration metrics
    expected_calibration_error = Column(Float)
    maximum_calibration_error = Column(Float)
    
    # Confusion matrix
    confusion_matrix = Column(JSON)
    
    # Per-class metrics
    class_metrics = Column(JSON)
    
    # Additional metrics
    additional_metrics = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
