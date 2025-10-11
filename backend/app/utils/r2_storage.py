"""
Cloudflare R2 storage client (S3-compatible).
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import structlog

try:
    import boto3
    from botocore.client import Config
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    boto3 = None
    Config = None
    ClientError = Exception

from app.core.config import settings

logger = structlog.get_logger()


class R2StorageClient:
    """
    Cloudflare R2 storage client using S3-compatible API.
    
    R2 is Cloudflare's object storage with zero egress fees,
    perfect for storing large datasets and model files.
    """
    
    def __init__(self):
        """Initialize R2 storage client."""
        if not BOTO3_AVAILABLE:
            logger.warning("boto3 not available, R2 storage disabled")
            self.client = None
            return
        
        if not settings.R2_ACCESS_KEY_ID or not settings.R2_SECRET_ACCESS_KEY:
            logger.warning("R2 credentials not configured, R2 storage disabled")
            self.client = None
            return
        
        try:
            self.client = boto3.client(
                's3',
                endpoint_url=settings.R2_ENDPOINT_URL,
                aws_access_key_id=settings.R2_ACCESS_KEY_ID,
                aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
                config=Config(signature_version='s3v4'),
                region_name='auto'  # R2 uses 'auto' for region
            )
            self.bucket = settings.R2_BUCKET_NAME
            logger.info("R2 storage client initialized", 
                       bucket=self.bucket,
                       endpoint=settings.R2_ENDPOINT_URL)
        except Exception as e:
            logger.error("Failed to initialize R2 client", exc_info=e)
            self.client = None
    
    def is_available(self) -> bool:
        """Check if R2 storage is available."""
        return self.client is not None
    
    def upload_file(
        self,
        local_path: str,
        remote_path: str,
        content_type: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload file to R2.
        
        Args:
            local_path: Local file path
            remote_path: Remote path in R2 bucket
            content_type: MIME type (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("R2 not available, skipping upload", local_path=local_path)
            return False
        
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            if metadata:
                extra_args['Metadata'] = metadata
            
            self.client.upload_file(
                local_path,
                self.bucket,
                remote_path,
                ExtraArgs=extra_args if extra_args else None
            )
            
            logger.info("File uploaded to R2",
                       local_path=local_path,
                       remote_path=remote_path,
                       bucket=self.bucket)
            return True
        
        except ClientError as e:
            logger.error("Failed to upload file to R2",
                        local_path=local_path,
                        remote_path=remote_path,
                        error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error uploading to R2",
                        local_path=local_path,
                        exc_info=e)
            return False
    
    def download_file(
        self,
        remote_path: str,
        local_path: str
    ) -> bool:
        """
        Download file from R2.
        
        Args:
            remote_path: Remote path in R2 bucket
            local_path: Local destination path
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("R2 not available, cannot download", remote_path=remote_path)
            return False
        
        try:
            # Create parent directories
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            self.client.download_file(
                self.bucket,
                remote_path,
                local_path
            )
            
            logger.info("File downloaded from R2",
                       remote_path=remote_path,
                       local_path=local_path,
                       bucket=self.bucket)
            return True
        
        except ClientError as e:
            logger.error("Failed to download file from R2",
                        remote_path=remote_path,
                        local_path=local_path,
                        error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error downloading from R2",
                        remote_path=remote_path,
                        exc_info=e)
            return False
    
    def delete_file(self, remote_path: str) -> bool:
        """
        Delete file from R2.
        
        Args:
            remote_path: Remote path in R2 bucket
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_available():
            logger.warning("R2 not available, cannot delete", remote_path=remote_path)
            return False
        
        try:
            self.client.delete_object(
                Bucket=self.bucket,
                Key=remote_path
            )
            
            logger.info("File deleted from R2",
                       remote_path=remote_path,
                       bucket=self.bucket)
            return True
        
        except ClientError as e:
            logger.error("Failed to delete file from R2",
                        remote_path=remote_path,
                        error=str(e))
            return False
        except Exception as e:
            logger.error("Unexpected error deleting from R2",
                        remote_path=remote_path,
                        exc_info=e)
            return False
    
    def list_files(
        self,
        prefix: str = "",
        max_keys: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        List files in R2 bucket.
        
        Args:
            prefix: Path prefix to filter
            max_keys: Maximum number of keys to return
            
        Returns:
            List of file objects with metadata
        """
        if not self.is_available():
            logger.warning("R2 not available, cannot list files")
            return []
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = response.get('Contents', [])
            
            logger.info("Files listed from R2",
                       prefix=prefix,
                       count=len(files),
                       bucket=self.bucket)
            
            return files
        
        except ClientError as e:
            logger.error("Failed to list files from R2",
                        prefix=prefix,
                        error=str(e))
            return []
        except Exception as e:
            logger.error("Unexpected error listing files from R2",
                        prefix=prefix,
                        exc_info=e)
            return []
    
    def file_exists(self, remote_path: str) -> bool:
        """
        Check if file exists in R2.
        
        Args:
            remote_path: Remote path in R2 bucket
            
        Returns:
            True if file exists, False otherwise
        """
        if not self.is_available():
            return False
        
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=remote_path
            )
            return True
        except ClientError:
            return False
        except Exception as e:
            logger.error("Error checking file existence in R2",
                        remote_path=remote_path,
                        exc_info=e)
            return False
    
    def get_file_size(self, remote_path: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            remote_path: Remote path in R2 bucket
            
        Returns:
            File size in bytes, or None if not found
        """
        if not self.is_available():
            return None
        
        try:
            response = self.client.head_object(
                Bucket=self.bucket,
                Key=remote_path
            )
            return response['ContentLength']
        except ClientError:
            return None
        except Exception as e:
            logger.error("Error getting file size from R2",
                        remote_path=remote_path,
                        exc_info=e)
            return None
    
    def generate_presigned_url(
        self,
        remote_path: str,
        expiration: int = 3600
    ) -> Optional[str]:
        """
        Generate presigned URL for temporary access.
        
        Args:
            remote_path: Remote path in R2 bucket
            expiration: URL expiration time in seconds (default: 1 hour)
            
        Returns:
            Presigned URL or None if failed
        """
        if not self.is_available():
            return None
        
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket,
                    'Key': remote_path
                },
                ExpiresIn=expiration
            )
            
            logger.info("Presigned URL generated",
                       remote_path=remote_path,
                       expiration=expiration)
            
            return url
        
        except ClientError as e:
            logger.error("Failed to generate presigned URL",
                        remote_path=remote_path,
                        error=str(e))
            return None
        except Exception as e:
            logger.error("Unexpected error generating presigned URL",
                        remote_path=remote_path,
                        exc_info=e)
            return None


# Global R2 storage client instance
r2_storage_client = R2StorageClient()
