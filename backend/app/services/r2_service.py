"""
Cloudflare R2 storage service for persistent dataset storage.
"""

import boto3
from botocore.client import Config
from pathlib import Path
import structlog
from typing import Optional, List
import os

logger = structlog.get_logger()


class R2Service:
    """Service for Cloudflare R2 object storage operations"""
    
    def __init__(self):
        """Initialize R2 client with credentials from environment"""
        self.account_id = os.getenv('R2_ACCOUNT_ID')
        self.access_key = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET_NAME', 'xai-platform-datasets')
        
        if not all([self.account_id, self.access_key, self.secret_key]):
            logger.warning("R2 credentials not configured, storage will be ephemeral")
            self.client = None
            return
        
        # Initialize S3 client for R2
        self.client = boto3.client(
            's3',
            endpoint_url=f'https://{self.account_id}.r2.cloudflarestorage.com',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(signature_version='s3v4'),
            region_name='auto'
        )
        
        logger.info("R2 client initialized", bucket=self.bucket_name)
    
    def is_configured(self) -> bool:
        """Check if R2 is properly configured"""
        return self.client is not None
    
    def file_exists(self, key: str) -> bool:
        """Check if a file exists in R2"""
        if not self.is_configured():
            return False
        
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False
    
    def upload_file(self, local_path: Path, r2_key: str) -> bool:
        """Upload a file to R2"""
        if not self.is_configured():
            logger.warning("R2 not configured, skipping upload")
            return False
        
        try:
            logger.info("Uploading to R2", local_path=str(local_path), r2_key=r2_key)
            
            with open(local_path, 'rb') as f:
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=r2_key,
                    Body=f
                )
            
            logger.info("Upload successful", r2_key=r2_key)
            return True
            
        except Exception as e:
            logger.error("Upload failed", error=str(e), r2_key=r2_key)
            return False
    
    def download_file(self, r2_key: str, local_path: Path) -> bool:
        """Download a file from R2"""
        if not self.is_configured():
            logger.warning("R2 not configured, skipping download")
            print(f"❌ R2 NOT CONFIGURED - Cannot download {r2_key}", flush=True)
            return False
        
        try:
            logger.info("Downloading from R2", r2_key=r2_key, local_path=str(local_path))
            print(f"📥 Downloading from R2: {r2_key} -> {local_path}", flush=True)
            
            # Create parent directory if needed
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Check if file exists first
            try:
                self.client.head_object(Bucket=self.bucket_name, Key=r2_key)
            except Exception as e:
                logger.error("File not found in R2", r2_key=r2_key, error=str(e))
                print(f"❌ FILE NOT FOUND IN R2: {r2_key}", flush=True)
                print(f"   Bucket: {self.bucket_name}", flush=True)
                print(f"   Error: {str(e)}", flush=True)
                return False
            
            self.client.download_file(
                Bucket=self.bucket_name,
                Key=r2_key,
                Filename=str(local_path)
            )
            
            logger.info("Download successful", r2_key=r2_key)
            print(f"✅ Downloaded successfully: {r2_key}", flush=True)
            return True
            
        except Exception as e:
            logger.error("Download failed", error=str(e), r2_key=r2_key)
            print(f"❌ R2 DOWNLOAD FAILED: {r2_key}", flush=True)
            print(f"   Error: {str(e)}", flush=True)
            return False
    
    def upload_directory(self, local_dir: Path, r2_prefix: str) -> bool:
        """Upload all files in a directory to R2"""
        if not self.is_configured():
            logger.warning("R2 not configured, skipping directory upload")
            return False
        
        try:
            logger.info("Uploading directory to R2", local_dir=str(local_dir), r2_prefix=r2_prefix)
            
            uploaded_count = 0
            # Upload both CSV and Parquet files
            for file_path in local_dir.glob("*"):
                if file_path.is_file() and file_path.suffix in ['.csv', '.parquet']:
                    r2_key = f"{r2_prefix}/{file_path.name}"
                    if self.upload_file(file_path, r2_key):
                        uploaded_count += 1
            
            logger.info("Directory upload complete", uploaded_count=uploaded_count)
            return uploaded_count > 0
            
        except Exception as e:
            logger.error("Directory upload failed", error=str(e))
            return False
    
    def download_directory(self, r2_prefix: str, local_dir: Path) -> bool:
        """Download all files with a prefix from R2"""
        if not self.is_configured():
            logger.warning("R2 not configured, skipping directory download")
            return False
        
        try:
            logger.info("Downloading directory from R2", r2_prefix=r2_prefix, local_dir=str(local_dir))
            
            # List all objects with prefix
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=r2_prefix
            )
            
            if 'Contents' not in response:
                logger.warning("No files found in R2", r2_prefix=r2_prefix)
                return False
            
            downloaded_count = 0
            for obj in response['Contents']:
                r2_key = obj['Key']
                file_name = Path(r2_key).name
                local_path = local_dir / file_name
                
                if self.download_file(r2_key, local_path):
                    downloaded_count += 1
            
            logger.info("Directory download complete", downloaded_count=downloaded_count)
            return downloaded_count > 0
            
        except Exception as e:
            logger.error("Directory download failed", error=str(e))
            return False
    
    def list_files(self, prefix: str = "") -> List[str]:
        """List all files in R2 with optional prefix"""
        if not self.is_configured():
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return []
            
            return [obj['Key'] for obj in response['Contents']]
            
        except Exception as e:
            logger.error("List files failed", error=str(e))
            return []
    
    def delete_file(self, r2_key: str) -> bool:
        """Delete a file from R2"""
        if not self.is_configured():
            return False
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=r2_key)
            logger.info("File deleted from R2", r2_key=r2_key)
            return True
        except Exception as e:
            logger.error("Delete failed", error=str(e), r2_key=r2_key)
            return False


# Singleton instance
r2_service = R2Service()
