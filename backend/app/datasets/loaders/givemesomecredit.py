"""Give Me Some Credit dataset loader."""

from pathlib import Path
import pandas as pd
from .base import BaseDatasetLoader
import structlog

logger = structlog.get_logger()


class GiveMeSomeCreditLoader(BaseDatasetLoader):
    """Loader for Give Me Some Credit dataset."""
    
    async def download(self) -> Path:
        """Download Give Me Some Credit dataset from Kaggle.
        
        Returns:
            Path to downloaded data directory
        """
        logger.info("Downloading Give Me Some Credit dataset", dataset_id=self.dataset_id)
        
        # Initialize Kaggle client
        from app.utils.kaggle_client import KaggleClient
        kaggle_client = KaggleClient()
        
        # For datasets (not competitions), we need to use the dataset API
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            # Download dataset
            dataset_name = self.config.get('kaggle_dataset', 'brycecf/give-me-some-credit-dataset')
            
            logger.info("Downloading from Kaggle", dataset=dataset_name)
            api.dataset_download_files(
                dataset_name,
                path=str(self.data_dir),
                unzip=True
            )
            
            logger.info("Dataset downloaded successfully", output_dir=str(self.data_dir))
            return self.data_dir
            
        except Exception as e:
            logger.error("Failed to download dataset", error=str(e))
            raise RuntimeError(f"Failed to download dataset: {e}")
    
    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        """Preprocess Give Me Some Credit dataset.
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        logger.info("Preprocessing Give Me Some Credit dataset",
                   rows=len(df),
                   cols=len(df.columns))
        
        # Remove unnamed index column if present
        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)
        
        # Handle missing values
        logger.debug("Handling missing values")
        # Fill numerical columns with median
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
        target_col = self.get_target_column()
        
        for col in numerical_cols:
            if col != target_col and df[col].isnull().any():
                df[col] = df[col].fillna(df[col].median())
        
        # Remove outliers (values beyond 3 standard deviations)
        logger.debug("Removing outliers")
        for col in numerical_cols:
            if col != target_col:
                mean = df[col].mean()
                std = df[col].std()
                df[col] = df[col].clip(lower=mean - 3*std, upper=mean + 3*std)
        
        # Scale numerical features
        logger.debug("Scaling numerical features")
        from sklearn.preprocessing import StandardScaler
        
        feature_cols = self.get_feature_columns(df)
        scaler = StandardScaler()
        df[feature_cols] = scaler.fit_transform(df[feature_cols])
        
        logger.info("Preprocessing complete", rows=len(df), cols=len(df.columns))
        return df
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw Give Me Some Credit data from CSV.
        
        Returns:
            Raw dataframe
        """
        # Try different possible filenames
        possible_files = [
            'cs-training.csv',
            'train.csv',
            'givemesomecredit.csv',
        ]
        
        for filename in possible_files:
            file_path = self.data_dir / filename
            if file_path.exists():
                logger.info("Loading data from file", file=filename)
                df = pd.read_csv(file_path)
                logger.info("Raw data loaded", rows=len(df), cols=len(df.columns))
                return df
        
        # If no file found, list what's in the directory
        files = list(self.data_dir.glob('*.csv'))
        if files:
            logger.info("Using first CSV file found", file=files[0].name)
            df = pd.read_csv(files[0])
            return df
        
        raise FileNotFoundError(f"No CSV file found in {self.data_dir}")
