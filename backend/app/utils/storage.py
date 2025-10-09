"""
Supabase storage utilities.
"""

from typing import Optional, BinaryIO
from pathlib import Path
import structlog

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from app.core.config import settings

logger = structlog.get_logger()


class StorageClient:
    """
    Supabase storage client wrapper.
    """
    
    def __init__(self):
        """Initialize storage client."""
        if not SUPABASE_AVAILABLE:
            logger.warning("Supabase client not available, using local storage fallback")
            self.client = None
            return
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
            logger.warning("Supabase credentials not configured, using local storage fallback")
            self.client = None
            return
        
        try:
            self.client: Optional[Client] = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_ROLE_KEY
            )
            logger.info("Supabase storage client initialized")
        except Exception as e:
            logger.error("Failed to initialize Supabase client", exc_info=e)
            self.client = None
    
    def upload_file(
        self,
        bucket: str,
        file_path: str,
        destination_path: str,
        content_type: Optional[str] = None,
    ) -> Optional[str]:
        """
        Upload file to Supabase storage.
        
        Args:
            bucket: Storage bucket name
            file_path: Local file path
            destination_path: Destination path in bucket
            content_type: File content type
            
        Returns:
            Public URL or None if using local storage
        """
        if self.client is None:
            logger.info("Using local storage, skipping Supabase upload",
                       file_path=file_path)
            return None
        
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            
            # Upload to Supabase
            self.client.storage.from_(bucket).upload(
                destination_path,
                file_data,
                file_options={"content-type": content_type} if content_type else None
            )
            
            # Get public URL
            public_url = self.client.storage.from_(bucket).get_public_url(destination_path)
            
            logger.info("File uploaded to Supabase",
                       bucket=bucket,
                       destination_path=destination_path)
            
            return public_url
        
        except Exception as e:
            logger.error("Failed to upload file to Supabase",
                        bucket=bucket,
                        destination_path=destination_path,
                        exc_info=e)
            return None
    
    def download_file(
        self,
        bucket: str,
        source_path: str,
        destination_path: str,
    ) -> bool:
        """
        Download file from Supabase storage.
        
        Args:
            bucket: Storage bucket name
            source_path: Source path in bucket
            destination_path: Local destination path
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Supabase client not available, cannot download")
            return False
        
        try:
            # Download from Supabase
            file_data = self.client.storage.from_(bucket).download(source_path)
            
            # Save to local file
            Path(destination_path).parent.mkdir(parents=True, exist_ok=True)
            with open(destination_path, 'wb') as f:
                f.write(file_data)
            
            logger.info("File downloaded from Supabase",
                       bucket=bucket,
                       source_path=source_path,
                       destination_path=destination_path)
            
            return True
        
        except Exception as e:
            logger.error("Failed to download file from Supabase",
                        bucket=bucket,
                        source_path=source_path,
                        exc_info=e)
            return False
    
    def delete_file(
        self,
        bucket: str,
        file_path: str,
    ) -> bool:
        """
        Delete file from Supabase storage.
        
        Args:
            bucket: Storage bucket name
            file_path: File path in bucket
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Supabase client not available, cannot delete")
            return False
        
        try:
            self.client.storage.from_(bucket).remove([file_path])
            
            logger.info("File deleted from Supabase",
                       bucket=bucket,
                       file_path=file_path)
            
            return True
        
        except Exception as e:
            logger.error("Failed to delete file from Supabase",
                        bucket=bucket,
                        file_path=file_path,
                        exc_info=e)
            return False
    
    def list_files(
        self,
        bucket: str,
        path: str = "",
    ) -> list:
        """
        List files in Supabase storage bucket.
        
        Args:
            bucket: Storage bucket name
            path: Path prefix to filter
            
        Returns:
            List of file objects
        """
        if self.client is None:
            logger.warning("Supabase client not available, cannot list files")
            return []
        
        try:
            files = self.client.storage.from_(bucket).list(path)
            
            logger.info("Files listed from Supabase",
                       bucket=bucket,
                       path=path,
                       count=len(files))
            
            return files
        
        except Exception as e:
            logger.error("Failed to list files from Supabase",
                        bucket=bucket,
                        path=path,
                        exc_info=e)
            return []
    
    def create_bucket(self, bucket: str, public: bool = False) -> bool:
        """
        Create a storage bucket.
        
        Args:
            bucket: Bucket name
            public: Whether bucket should be public
            
        Returns:
            True if successful, False otherwise
        """
        if self.client is None:
            logger.warning("Supabase client not available, cannot create bucket")
            return False
        
        try:
            self.client.storage.create_bucket(bucket, options={"public": public})
            
            logger.info("Bucket created in Supabase",
                       bucket=bucket,
                       public=public)
            
            return True
        
        except Exception as e:
            logger.error("Failed to create bucket in Supabase",
                        bucket=bucket,
                        exc_info=e)
            return False


# Global storage client instance
storage_client = StorageClient()
