"""German Credit Risk dataset loader."""

from pathlib import Path
import pandas as pd
from .base import BaseDatasetLoader
import structlog

logger = structlog.get_logger()


class GermanCreditLoader(BaseDatasetLoader):
    """Loader for German Credit Risk dataset."""
    
    async def download(self) -> Path:
        """Download German Credit dataset from Kaggle.
        
        Returns:
            Path to downloaded data directory
        """
        logger.info("Downloading German Credit dataset", dataset_id=self.dataset_id)
        
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            # Download dataset
            dataset_name = self.config.get('kaggle_dataset', 'uciml/german-credit')
            
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
        """Preprocess German Credit dataset.
        
        Args:
            df: Raw dataframe
            
        Returns:
            Preprocessed dataframe
        """
        logger.info("Preprocessing German Credit dataset",
                   rows=len(df),
                   cols=len(df.columns))
        
        target_col = self.get_target_column()
        positive_class = self.config.get('positive_class', 'bad')
        
        # Encode target variable (convert 'good'/'bad' to 0/1)
        if df[target_col].dtype == 'object':
            logger.debug("Encoding target variable")
            df[target_col] = (df[target_col] == positive_class).astype(int)
        
        # Encode categorical variables
        logger.debug("Encoding categorical variables")
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        
        for col in categorical_cols:
            if col != target_col:
                df[col] = df[col].astype('category').cat.codes
        
        # Scale numerical features
        logger.debug("Scaling numerical features")
        from sklearn.preprocessing import StandardScaler
        
        feature_cols = self.get_feature_columns(df)
        numerical_cols = df[feature_cols].select_dtypes(include=['float64', 'int64']).columns
        
        if len(numerical_cols) > 0:
            scaler = StandardScaler()
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
        
        logger.info("Preprocessing complete", rows=len(df), cols=len(df.columns))
        return df
    
    def load_raw_data(self) -> pd.DataFrame:
        """Load raw German Credit data from CSV.
        
        Returns:
            Raw dataframe
        """
        # Try different possible filenames
        possible_files = [
            'german_credit_data.csv',
            'german.csv',
            'credit.csv',
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
