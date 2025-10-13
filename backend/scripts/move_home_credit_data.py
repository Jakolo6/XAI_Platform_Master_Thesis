"""
Script to move home-credit data from home-credit/ to datasets/home-credit-default-risk/
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.utils.r2_storage import r2_storage_client
import structlog

logger = structlog.get_logger()


def move_home_credit_data():
    """Move files from home-credit/ to datasets/home-credit-default-risk/"""
    
    # List all files in home-credit/
    old_prefix = "home-credit/"
    new_prefix = "datasets/home-credit-default-risk/"
    
    logger.info("Starting to move home-credit data")
    
    try:
        # List all objects with old prefix
        response = r2_storage_client.client.list_objects_v2(
            Bucket=r2_storage_client.bucket_name,
            Prefix=old_prefix
        )
        
        if 'Contents' not in response:
            logger.info("No files found in home-credit/")
            return
        
        files_to_move = response['Contents']
        logger.info(f"Found {len(files_to_move)} files to move")
        
        for obj in files_to_move:
            old_key = obj['Key']
            # Skip if it's just the directory marker
            if old_key == old_prefix:
                continue
                
            # Create new key by replacing prefix
            relative_path = old_key[len(old_prefix):]
            new_key = new_prefix + relative_path
            
            logger.info(f"Copying {old_key} -> {new_key}")
            
            # Copy object to new location
            r2_storage_client.client.copy_object(
                Bucket=r2_storage_client.bucket_name,
                CopySource={'Bucket': r2_storage_client.bucket_name, 'Key': old_key},
                Key=new_key
            )
            
            logger.info(f"Copied successfully, now deleting {old_key}")
            
            # Delete old object
            r2_storage_client.client.delete_object(
                Bucket=r2_storage_client.bucket_name,
                Key=old_key
            )
            
            logger.info(f"Moved {old_key} to {new_key}")
        
        logger.info("Successfully moved all home-credit data")
        
    except Exception as e:
        logger.error("Failed to move home-credit data", error=str(e))
        raise


if __name__ == "__main__":
    move_home_credit_data()
