"""
Kaggle API client for downloading IEEE-CIS fraud detection dataset.
"""

import os
import zipfile
from pathlib import Path
from typing import Optional, Dict, Any
import structlog

logger = structlog.get_logger()


class KaggleClient:
    """
    Client for interacting with Kaggle API to download datasets.
    """
    
    def __init__(self, username: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize Kaggle client.
        
        Args:
            username: Kaggle username (uses env var if None)
            api_key: Kaggle API key (uses env var if None)
        """
        self.username = username or os.getenv('KAGGLE_USERNAME')
        self.api_key = api_key or os.getenv('KAGGLE_KEY')
        
        if not self.username or not self.api_key:
            logger.warning("Kaggle credentials not found in environment variables")
        
        # Set up Kaggle credentials
        self._setup_credentials()
    
    def _setup_credentials(self) -> None:
        """Set up Kaggle API credentials."""
        if self.username and self.api_key:
            # Create kaggle directory if it doesn't exist
            kaggle_dir = Path.home() / '.kaggle'
            kaggle_dir.mkdir(exist_ok=True)
            
            # Write credentials file
            kaggle_json = kaggle_dir / 'kaggle.json'
            kaggle_json.write_text(
                f'{{"username":"{self.username}","key":"{self.api_key}"}}'
            )
            kaggle_json.chmod(0o600)
            
            logger.info("Kaggle credentials configured")
    
    def download_ieee_cis_dataset(
        self,
        output_dir: str,
        competition_name: str = 'ieee-fraud-detection'
    ) -> Dict[str, Any]:
        """
        Download IEEE-CIS fraud detection dataset from Kaggle.
        
        Args:
            output_dir: Directory to save downloaded files
            competition_name: Kaggle competition name
            
        Returns:
            Dictionary with download status and file paths
        """
        try:
            # Import kaggle API
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            logger.info("Downloading IEEE-CIS dataset from Kaggle",
                       competition=competition_name,
                       output_dir=output_dir)
            
            # Initialize API
            api = KaggleApi()
            api.authenticate()
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Download competition files
            api.competition_download_files(
                competition_name,
                path=output_dir,
                quiet=False
            )
            
            # Extract zip files
            zip_file = Path(output_dir) / f'{competition_name}.zip'
            if zip_file.exists():
                logger.info("Extracting downloaded files")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                
                # Remove zip file
                zip_file.unlink()
            
            # Verify required files exist
            transaction_file = Path(output_dir) / 'train_transaction.csv'
            identity_file = Path(output_dir) / 'train_identity.csv'
            
            if not transaction_file.exists() or not identity_file.exists():
                raise FileNotFoundError("Required dataset files not found after download")
            
            logger.info("Dataset download complete",
                       transaction_file=str(transaction_file),
                       identity_file=str(identity_file))
            
            return {
                'status': 'success',
                'transaction_file': str(transaction_file),
                'identity_file': str(identity_file),
                'output_dir': output_dir,
            }
            
        except ImportError:
            logger.error("Kaggle package not installed. Install with: pip install kaggle")
            return {
                'status': 'error',
                'error': 'Kaggle package not installed',
                'message': 'Install kaggle package: pip install kaggle'
            }
        
        except Exception as e:
            logger.error("Failed to download dataset", exc_info=e)
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to download IEEE-CIS dataset from Kaggle'
            }
    
    def list_competition_files(self, competition_name: str = 'ieee-fraud-detection') -> Dict[str, Any]:
        """
        List files available in a Kaggle competition.
        
        Args:
            competition_name: Kaggle competition name
            
        Returns:
            Dictionary with file information
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            files = api.competition_list_files(competition_name)
            
            file_info = [
                {
                    'name': f.name,
                    'size': f.size,
                    'creation_date': str(f.creationDate) if hasattr(f, 'creationDate') else None
                }
                for f in files
            ]
            
            logger.info("Listed competition files",
                       competition=competition_name,
                       file_count=len(file_info))
            
            return {
                'status': 'success',
                'competition': competition_name,
                'files': file_info
            }
            
        except Exception as e:
            logger.error("Failed to list competition files", exc_info=e)
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def download_competition(
        self,
        competition_name: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Download a Kaggle competition dataset.
        
        Args:
            competition_name: Name of the competition
            output_dir: Directory to save downloaded files
            
        Returns:
            Dictionary with download status and file paths
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            logger.info("Downloading Kaggle competition",
                       competition=competition_name,
                       output_dir=output_dir)
            
            # Initialize API
            api = KaggleApi()
            api.authenticate()
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Download competition files
            api.competition_download_files(
                competition_name,
                path=output_dir,
                quiet=False
            )
            
            # Extract zip files
            zip_file = Path(output_dir) / f'{competition_name}.zip'
            if zip_file.exists():
                logger.info("Extracting downloaded files")
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(output_dir)
                zip_file.unlink()
            
            # Find all CSV files
            csv_files = list(Path(output_dir).glob('*.csv'))
            
            logger.info("Competition download complete",
                       file_count=len(csv_files))
            
            return {
                'status': 'success',
                'files': [str(f) for f in csv_files],
                'output_dir': output_dir,
            }
            
        except Exception as e:
            logger.error("Failed to download competition", exc_info=e)
            return {
                'status': 'error',
                'error': str(e),
                'message': f'Failed to download competition: {competition_name}'
            }
    
    def download_dataset(
        self,
        dataset_name: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Download a Kaggle dataset.
        
        Args:
            dataset_name: Name of the dataset (format: owner/dataset-name)
            output_dir: Directory to save downloaded files
            
        Returns:
            Dictionary with download status and file paths
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            logger.info("Downloading Kaggle dataset",
                       dataset=dataset_name,
                       output_dir=output_dir)
            
            # Initialize API
            api = KaggleApi()
            api.authenticate()
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            
            # Download dataset files
            api.dataset_download_files(
                dataset_name,
                path=output_dir,
                unzip=True,
                quiet=False
            )
            
            # Find all CSV files
            csv_files = list(Path(output_dir).glob('*.csv'))
            
            logger.info("Dataset download complete",
                       file_count=len(csv_files))
            
            return {
                'status': 'success',
                'files': [str(f) for f in csv_files],
                'output_dir': output_dir,
            }
            
        except Exception as e:
            logger.error("Failed to download dataset", exc_info=e)
            return {
                'status': 'error',
                'error': str(e),
                'message': f'Failed to download dataset: {dataset_name}'
            }
    
    def verify_credentials(self) -> bool:
        """
        Verify Kaggle API credentials are valid.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            from kaggle.api.kaggle_api_extended import KaggleApi
            
            api = KaggleApi()
            api.authenticate()
            
            # Try to list competitions to verify authentication
            api.competitions_list(page=1)
            
            logger.info("Kaggle credentials verified successfully")
            return True
            
        except Exception as e:
            logger.error("Kaggle credentials verification failed", exc_info=e)
            return False
