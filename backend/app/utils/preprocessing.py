"""
Data preprocessing utilities for IEEE-CIS fraud detection dataset.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any, Optional, List
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
import structlog

logger = structlog.get_logger()


class DataPreprocessor:
    """
    Preprocessor for IEEE-CIS fraud detection dataset.
    Handles merging, cleaning, feature engineering, and sampling.
    """
    
    def __init__(self, max_size_mb: int = 200, sample_size: int = 500000):
        """
        Initialize preprocessor.
        
        Args:
            max_size_mb: Maximum dataset size in MB before sampling
            sample_size: Target sample size for large datasets
        """
        self.max_size_mb = max_size_mb
        self.sample_size = sample_size
        self.scalers = {}
        self.encoders = {}
        self.feature_names = []
        
    def load_and_merge_ieee_cis(
        self,
        transaction_path: str,
        identity_path: str
    ) -> pd.DataFrame:
        """
        Load and merge IEEE-CIS transaction and identity datasets.
        
        Args:
            transaction_path: Path to train_transaction.csv
            identity_path: Path to train_identity.csv
            
        Returns:
            Merged DataFrame
        """
        logger.info("Loading IEEE-CIS datasets", 
                   transaction_path=transaction_path,
                   identity_path=identity_path)
        
        # Load datasets
        df_transaction = pd.read_csv(transaction_path)
        df_identity = pd.read_csv(identity_path)
        
        logger.info("Datasets loaded",
                   transaction_rows=len(df_transaction),
                   identity_rows=len(df_identity))
        
        # Merge on TransactionID
        df = df_transaction.merge(df_identity, on='TransactionID', how='left')
        
        logger.info("Datasets merged", total_rows=len(df), total_columns=len(df.columns))
        
        return df
    
    def engineer_financial_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer financial domain features.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering financial features")
        
        df = df.copy()
        
        # Ratio features
        if 'TransactionAmt' in df.columns:
            # Transaction amount to card mean ratio
            card_mean = df.groupby('card1')['TransactionAmt'].transform('mean')
            df['amt_to_card_mean_ratio'] = df['TransactionAmt'] / (card_mean + 1e-6)
            
            # Transaction amount statistics
            df['amt_log'] = np.log1p(df['TransactionAmt'])
            df['amt_decimal'] = df['TransactionAmt'] - df['TransactionAmt'].astype(int)
        
        # Time-of-day features
        if 'TransactionDT' in df.columns:
            # Convert to hours (assuming TransactionDT is in seconds)
            df['transaction_hour'] = (df['TransactionDT'] / 3600) % 24
            df['transaction_day'] = (df['TransactionDT'] / 86400).astype(int)
            df['transaction_weekday'] = (df['transaction_day'] % 7)
            
            # Time-based cyclical features
            df['hour_sin'] = np.sin(2 * np.pi * df['transaction_hour'] / 24)
            df['hour_cos'] = np.cos(2 * np.pi * df['transaction_hour'] / 24)
        
        # Device/Browser frequency encoding
        for col in ['id_30', 'id_31', 'DeviceType', 'DeviceInfo']:
            if col in df.columns:
                freq = df[col].value_counts(normalize=True)
                df[f'{col}_freq'] = df[col].map(freq)
        
        # Card features
        for col in ['card1', 'card2', 'card3', 'card4', 'card5', 'card6']:
            if col in df.columns:
                # Frequency encoding
                freq = df[col].value_counts(normalize=True)
                df[f'{col}_freq'] = df[col].map(freq)
        
        logger.info("Feature engineering complete", new_columns=len(df.columns))
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with handled missing values
        """
        logger.info("Handling missing values")
        
        df = df.copy()
        
        # Separate numerical and categorical columns
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        # Remove target column from processing
        if 'isFraud' in numerical_cols:
            numerical_cols.remove('isFraud')
        
        # Fill numerical columns with median
        for col in numerical_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical columns with mode or 'missing'
        for col in categorical_cols:
            if df[col].isnull().any():
                mode_val = df[col].mode()
                if len(mode_val) > 0:
                    df[col].fillna(mode_val[0], inplace=True)
                else:
                    df[col].fillna('missing', inplace=True)
        
        logger.info("Missing values handled")
        
        return df
    
    def encode_categorical_features(
        self,
        df: pd.DataFrame,
        fit: bool = True
    ) -> pd.DataFrame:
        """
        Encode categorical features.
        
        Args:
            df: Input DataFrame
            fit: Whether to fit encoders or use existing ones
            
        Returns:
            DataFrame with encoded features
        """
        logger.info("Encoding categorical features", fit=fit)
        
        df = df.copy()
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        
        for col in categorical_cols:
            if fit:
                # Create new encoder
                encoder = LabelEncoder()
                df[col] = encoder.fit_transform(df[col].astype(str))
                self.encoders[col] = encoder
            else:
                # Use existing encoder
                if col in self.encoders:
                    # Handle unseen categories
                    known_categories = set(self.encoders[col].classes_)
                    df[col] = df[col].apply(
                        lambda x: x if x in known_categories else 'unknown'
                    )
                    df[col] = self.encoders[col].transform(df[col].astype(str))
        
        logger.info("Categorical encoding complete")
        
        return df
    
    def remove_ip_like_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove IP-like hash features for privacy.
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with IP-like features removed
        """
        logger.info("Removing IP-like features")
        
        # Remove columns that might contain IP hashes
        ip_like_cols = [col for col in df.columns if 'ip' in col.lower()]
        
        if ip_like_cols:
            df = df.drop(columns=ip_like_cols)
            logger.info("Removed IP-like columns", columns=ip_like_cols)
        
        return df
    
    def balanced_sample(
        self,
        df: pd.DataFrame,
        target_col: str = 'isFraud',
        sample_size: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Create a balanced sample of the dataset.
        
        Args:
            df: Input DataFrame
            target_col: Target column name
            sample_size: Desired sample size (uses self.sample_size if None)
            
        Returns:
            Balanced sampled DataFrame
        """
        if sample_size is None:
            sample_size = self.sample_size
        
        logger.info("Creating balanced sample", 
                   original_size=len(df),
                   target_size=sample_size)
        
        # Calculate samples per class
        fraud_count = df[target_col].sum()
        non_fraud_count = len(df) - fraud_count
        
        # Determine sampling strategy
        if len(df) <= sample_size:
            logger.info("Dataset smaller than target, no sampling needed")
            return df
        
        # Sample equal amounts from each class
        samples_per_class = sample_size // 2
        
        fraud_df = df[df[target_col] == 1].sample(
            n=min(samples_per_class, fraud_count),
            random_state=42
        )
        non_fraud_df = df[df[target_col] == 0].sample(
            n=min(samples_per_class, non_fraud_count),
            random_state=42
        )
        
        # Combine and shuffle
        sampled_df = pd.concat([fraud_df, non_fraud_df]).sample(frac=1, random_state=42)
        
        logger.info("Balanced sampling complete",
                   final_size=len(sampled_df),
                   fraud_ratio=sampled_df[target_col].mean())
        
        return sampled_df
    
    def scale_features(
        self,
        df: pd.DataFrame,
        target_col: str = 'isFraud',
        fit: bool = True
    ) -> pd.DataFrame:
        """
        Scale numerical features.
        
        Args:
            df: Input DataFrame
            target_col: Target column to exclude from scaling
            fit: Whether to fit scalers or use existing ones
            
        Returns:
            DataFrame with scaled features
        """
        logger.info("Scaling features", fit=fit)
        
        df = df.copy()
        
        # Get numerical columns (exclude target and ID columns)
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        exclude_cols = [target_col, 'TransactionID']
        numerical_cols = [col for col in numerical_cols if col not in exclude_cols]
        
        if fit:
            scaler = StandardScaler()
            df[numerical_cols] = scaler.fit_transform(df[numerical_cols])
            self.scalers['standard'] = scaler
        else:
            if 'standard' in self.scalers:
                df[numerical_cols] = self.scalers['standard'].transform(df[numerical_cols])
        
        logger.info("Feature scaling complete")
        
        return df
    
    def split_data(
        self,
        df: pd.DataFrame,
        target_col: str = 'isFraud',
        test_size: float = 0.15,
        val_size: float = 0.15
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Split data into train, validation, and test sets.
        
        Args:
            df: Input DataFrame
            target_col: Target column name
            test_size: Test set proportion
            val_size: Validation set proportion
            
        Returns:
            Tuple of (train_df, val_df, test_df)
        """
        logger.info("Splitting data",
                   test_size=test_size,
                   val_size=val_size)
        
        # First split: train+val vs test
        train_val_df, test_df = train_test_split(
            df,
            test_size=test_size,
            stratify=df[target_col],
            random_state=42
        )
        
        # Second split: train vs val
        val_proportion = val_size / (1 - test_size)
        train_df, val_df = train_test_split(
            train_val_df,
            test_size=val_proportion,
            stratify=train_val_df[target_col],
            random_state=42
        )
        
        logger.info("Data split complete",
                   train_size=len(train_df),
                   val_size=len(val_df),
                   test_size=len(test_df))
        
        return train_df, val_df, test_df
    
    def get_dataset_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive dataset statistics.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Dictionary of statistics
        """
        logger.info("Calculating dataset statistics")
        
        stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
            'missing_values': df.isnull().sum().to_dict(),
            'missing_percentage': (df.isnull().sum() / len(df) * 100).to_dict(),
            'duplicate_rows': df.duplicated().sum(),
        }
        
        # Target distribution
        if 'isFraud' in df.columns:
            stats['class_distribution'] = df['isFraud'].value_counts().to_dict()
            stats['fraud_percentage'] = df['isFraud'].mean() * 100
        
        # Numerical features statistics
        numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        stats['numerical_features'] = {
            col: {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'median': float(df[col].median()),
            }
            for col in numerical_cols[:10]  # Limit to first 10 for brevity
        }
        
        # Categorical features
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        stats['categorical_features'] = {
            col: {
                'unique_values': int(df[col].nunique()),
                'top_value': str(df[col].mode()[0]) if len(df[col].mode()) > 0 else None,
            }
            for col in categorical_cols[:10]  # Limit to first 10
        }
        
        logger.info("Statistics calculation complete")
        
        return stats
    
    def preprocess_pipeline(
        self,
        transaction_path: str,
        identity_path: str,
        output_dir: str,
        apply_sampling: bool = True
    ) -> Dict[str, Any]:
        """
        Complete preprocessing pipeline.
        
        Args:
            transaction_path: Path to transaction CSV
            identity_path: Path to identity CSV
            output_dir: Directory to save processed data
            apply_sampling: Whether to apply balanced sampling
            
        Returns:
            Dictionary with processing results and statistics
        """
        logger.info("Starting preprocessing pipeline")
        
        # Load and merge
        df = self.load_and_merge_ieee_cis(transaction_path, identity_path)
        
        # Remove IP-like features
        df = self.remove_ip_like_features(df)
        
        # Engineer features
        df = self.engineer_financial_features(df)
        
        # Handle missing values
        df = self.handle_missing_values(df)
        
        # Encode categorical features
        df = self.encode_categorical_features(df, fit=True)
        
        # Apply sampling if needed
        if apply_sampling:
            df = self.balanced_sample(df)
        
        # Split data
        train_df, val_df, test_df = self.split_data(df)
        
        # Scale features
        train_df = self.scale_features(train_df, fit=True)
        val_df = self.scale_features(val_df, fit=False)
        test_df = self.scale_features(test_df, fit=False)
        
        # Save processed data
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        train_df.to_csv(f"{output_dir}/train.csv", index=False)
        val_df.to_csv(f"{output_dir}/validation.csv", index=False)
        test_df.to_csv(f"{output_dir}/test.csv", index=False)
        
        # Get statistics
        stats = self.get_dataset_statistics(df)
        
        logger.info("Preprocessing pipeline complete")
        
        return {
            'status': 'success',
            'statistics': stats,
            'train_size': len(train_df),
            'val_size': len(val_df),
            'test_size': len(test_df),
            'output_dir': output_dir,
        }
