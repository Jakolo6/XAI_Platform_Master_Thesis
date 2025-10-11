"""IEEE-CIS Fraud Detection dataset loader."""

from pathlib import Path
import pandas as pd
from .base import BaseDatasetLoader
from app.utils.kaggle_client import KaggleClient
import structlog

logger = structlog.get_logger()


class IEEECISLoader(BaseDatasetLoader):
    """Loader for IEEE-CIS Fraud Detection dataset."""
    
    async def download(self) -> Path:
        """Download IEEE-CIS dataset from Kaggle.
        
        Returns:
            Path to downloaded data directory
        """
        logger.info("Downloading IEEE-CIS dataset", dataset_id=self.dataset_id)
        
        # Initialize Kaggle client
        kaggle_client = KaggleClient()
        
        # Download dataset
        competition = self.config.get('kaggle_competition', 'ieee-fraud-detection')
        result = kaggle_client.download_ieee_cis_dataset(
            output_dir=str(self.data_dir),
            competition_name=competition
        )
        
        if result['status'] != 'success':
            raise RuntimeError(f"Failed to download dataset: {result.get('error')}")
        
        logger.info("IEEE-CIS dataset downloaded successfully", 
                   output_dir=str(self.data_dir))
        
        return self.data_dir
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess IEEE-CIS dataset with memory optimization.
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        logger.info("Preprocessing IEEE-CIS dataset", 
                   rows=len(df), 
                   cols=len(df.columns))
        
        # Drop columns with >50% missing values to save memory
        logger.debug("Dropping high-missing columns")
        missing_pct = df.isnull().sum() / len(df)
        cols_to_keep = missing_pct[missing_pct < 0.5].index.tolist()
        df = df[cols_to_keep]
        logger.info(f"Kept {len(cols_to_keep)} columns with <50% missing values")
        
        # Handle missing values
        logger.debug("Handling missing values")
        # For numerical columns, fill with median
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        for col in numerical_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        
        # For categorical columns, fill with mode or 'unknown'
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            if df[col].isnull().any():
                df[col] = df[col].fillna('unknown')
        
        # Encode categorical variables
        logger.debug("Encoding categorical variables")
        target_col = self.get_target_column()
        for col in categorical_cols:
            if col != target_col:
                df[col] = df[col].astype('category').cat.codes
        
        # Limit features to top 50 by variance to save memory
        logger.debug("Selecting top features by variance")
        feature_cols = self.get_feature_columns(df)
        
        if len(feature_cols) > 50:
            # Calculate variance for each feature
            variances = df[feature_cols].var()
            top_features = variances.nlargest(50).index.tolist()
            df = df[top_features + [target_col]]
            logger.info(f"Selected top 50 features from {len(feature_cols)}")
        else:
            df = df[feature_cols + [target_col]]
        
        logger.info("Preprocessing complete", features=len(df.columns) - 1)
        
        return df
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw IEEE-CIS data from CSV files with memory optimization.
        
        Returns:
            Combined dataframe (sampled for memory efficiency)
        """
        transaction_file = self.data_dir / 'train_transaction.csv'
        identity_file = self.data_dir / 'train_identity.csv'
        
        if not transaction_file.exists():
            raise FileNotFoundError(f"Transaction file not found: {transaction_file}")
        
        logger.info("Loading transaction data with sampling for memory efficiency")
        
        # Sample 100k rows instead of all 590k to fit in memory
        # This is sufficient for XAI research and model training
        sample_size = 100000
        
        # Read with sampling to reduce memory usage
        transaction_df = pd.read_csv(
            transaction_file,
            nrows=sample_size,
            low_memory=True
        )
        
        logger.info(f"Loaded {len(transaction_df)} transaction rows (sampled for memory efficiency)")
        
        # Identity file is optional
        if identity_file.exists():
            logger.info("Loading identity data")
            identity_df = pd.read_csv(
                identity_file,
                nrows=sample_size,
                low_memory=True
            )
            
            # Merge on TransactionID
            logger.info("Merging transaction and identity data")
            df = transaction_df.merge(identity_df, on='TransactionID', how='left')
            
            # Clean up to free memory
            del transaction_df, identity_df
        else:
            logger.warning("Identity file not found, using transaction data only")
            df = transaction_df
        
        logger.info("Raw data loaded", rows=len(df), cols=len(df.columns))
        return df
