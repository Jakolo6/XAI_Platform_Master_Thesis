"""Base dataset loader."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Tuple, Optional
import pandas as pd
import structlog

logger = structlog.get_logger()


class BaseDatasetLoader(ABC):
    """Base class for dataset loaders.
    
    All dataset loaders should inherit from this class and implement
    the abstract methods for downloading and preprocessing.
    """
    
    def __init__(self, dataset_id: str, config: Dict, data_dir: Optional[Path] = None):
        """Initialize dataset loader.
        
        Args:
            dataset_id: Dataset identifier
            config: Dataset configuration from registry
            data_dir: Optional data directory path (defaults to data/{dataset_id})
        """
        self.dataset_id = dataset_id
        self.config = config
        
        # Use provided data directory or default
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path("data") / dataset_id
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Dataset loader initialized", 
                   dataset_id=dataset_id,
                   data_dir=str(self.data_dir))
    
    @abstractmethod
    async def download(self) -> Path:
        """Download dataset from source.
        
        Returns:
            Path to downloaded data file
        """
        pass
    
    @abstractmethod
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess dataset.
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        pass
    
    def split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split dataset into train/val/test.
        
        Args:
            df: Preprocessed dataframe
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        ratios = self.config.get('split_ratios', {
            'train': 0.7,
            'val': 0.15,
            'test': 0.15
        })
        
        # Shuffle
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        # Calculate split points
        n = len(df)
        train_end = int(n * ratios['train'])
        val_end = train_end + int(n * ratios['val'])
        
        train_df = df[:train_end]
        val_df = df[train_end:val_end]
        test_df = df[val_end:]
        
        logger.info(
            "Dataset split",
            dataset_id=self.dataset_id,
            train=len(train_df),
            val=len(val_df),
            test=len(test_df)
        )
        
        return train_df, val_df, test_df
    
    def save_splits(
        self,
        train_df: pd.DataFrame,
        val_df: pd.DataFrame,
        test_df: pd.DataFrame
    ):
        """Save splits to parquet files.
        
        Args:
            train_df: Training dataframe
            val_df: Validation dataframe
            test_df: Test dataframe
        """
        train_df.to_parquet(self.data_dir / "train.parquet", index=False)
        val_df.to_parquet(self.data_dir / "validation.parquet", index=False)
        test_df.to_parquet(self.data_dir / "test.parquet", index=False)
        
        logger.info("Dataset splits saved", 
                   dataset_id=self.dataset_id,
                   directory=str(self.data_dir))
    
    def load_splits(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Load splits from parquet files.
        
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        train_df = pd.read_parquet(self.data_dir / "train.parquet")
        val_df = pd.read_parquet(self.data_dir / "validation.parquet")
        test_df = pd.read_parquet(self.data_dir / "test.parquet")
        
        logger.info("Dataset splits loaded",
                   dataset_id=self.dataset_id,
                   train=len(train_df),
                   val=len(val_df),
                   test=len(test_df))
        
        return train_df, val_df, test_df
    
    def splits_exist(self) -> bool:
        """Check if splits already exist.
        
        Returns:
            True if all split files exist
        """
        return (
            (self.data_dir / "train.parquet").exists() and
            (self.data_dir / "validation.parquet").exists() and
            (self.data_dir / "test.parquet").exists()
        )
    
    def get_target_column(self) -> str:
        """Get target column name.
        
        Returns:
            Target column name
        """
        return self.config['target_column']
    
    def get_feature_columns(self, df: pd.DataFrame) -> list:
        """Get feature column names (all except target).
        
        Args:
            df: Dataframe
            
        Returns:
            List of feature column names
        """
        target = self.get_target_column()
        return [col for col in df.columns if col != target]
    
    def get_statistics(self, df: pd.DataFrame) -> Dict:
        """Calculate dataset statistics.
        
        Args:
            df: Dataframe
            
        Returns:
            Dictionary of statistics
        """
        target_col = self.get_target_column()
        
        stats = {
            'total_samples': len(df),
            'num_features': len(df.columns) - 1,  # Exclude target
            'missing_values': df.isnull().sum().sum(),
            'class_distribution': df[target_col].value_counts().to_dict(),
        }
        
        # Calculate class balance
        if target_col in df.columns:
            value_counts = df[target_col].value_counts()
            total = len(df)
            stats['class_balance'] = {
                str(k): float(v / total) for k, v in value_counts.items()
            }
        
        return stats
