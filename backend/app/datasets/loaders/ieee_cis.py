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
        """Preprocess IEEE-CIS dataset.
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        logger.info("Preprocessing IEEE-CIS dataset", 
                   rows=len(df), 
                   cols=len(df.columns))
        
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
        
        # Remove low variance features
        logger.debug("Removing low variance features")
        from sklearn.feature_selection import VarianceThreshold
        
        feature_cols = self.get_feature_columns(df)
        selector = VarianceThreshold(threshold=0.01)
        
        # Fit on features only
        X = df[feature_cols]
        selector.fit(X)
        
        # Get selected feature names
        selected_features = [feature_cols[i] for i in range(len(feature_cols)) 
                           if selector.get_support()[i]]
        
        # Keep selected features + target
        df = df[selected_features + [target_col]]
        
        logger.info("Preprocessing complete",
                   original_features=len(feature_cols),
                   selected_features=len(selected_features))
        
        return df
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw IEEE-CIS data from CSV files.
        
        Returns:
            Combined dataframe
        """
        transaction_file = self.data_dir / 'train_transaction.csv'
        identity_file = self.data_dir / 'train_identity.csv'
        
        if not transaction_file.exists():
            raise FileNotFoundError(f"Transaction file not found: {transaction_file}")
        
        logger.info("Loading transaction data")
        transaction_df = pd.read_csv(transaction_file)
        
        # Identity file is optional
        if identity_file.exists():
            logger.info("Loading identity data")
            identity_df = pd.read_csv(identity_file)
            
            # Merge on TransactionID
            logger.info("Merging transaction and identity data")
            df = transaction_df.merge(identity_df, on='TransactionID', how='left')
        else:
            logger.warning("Identity file not found, using transaction data only")
            df = transaction_df
        
        logger.info("Raw data loaded", rows=len(df), cols=len(df.columns))
        return df
