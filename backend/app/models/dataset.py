"""Dataset model."""

from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DatasetStatus(str, enum.Enum):
    """Dataset processing status."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Dataset(Base):
    """Dataset model for tracking datasets."""
    
    __tablename__ = "datasets"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    source = Column(String, nullable=False)  # e.g., "kaggle", "upload"
    source_identifier = Column(String)  # e.g., Kaggle dataset ID
    
    status = Column(SQLEnum(DatasetStatus), default=DatasetStatus.PENDING, nullable=False)
    
    # File information
    file_path = Column(String)
    file_size_mb = Column(Float)
    
    # Dataset statistics
    total_rows = Column(Integer)
    total_columns = Column(Integer)
    train_rows = Column(Integer)
    val_rows = Column(Integer)
    test_rows = Column(Integer)
    
    # Class distribution
    fraud_count = Column(Integer)
    non_fraud_count = Column(Integer)
    fraud_percentage = Column(Float)
    
    # Preprocessing info
    preprocessing_config = Column(JSON)
    feature_names = Column(JSON)
    statistics = Column(JSON)
    
    # Error tracking
    error_message = Column(String)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
