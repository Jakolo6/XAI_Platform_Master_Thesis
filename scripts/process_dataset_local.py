#!/usr/bin/env python3
"""
Local Dataset Processing Script

Process datasets locally (using your computer's RAM) and upload to cloud storage.
This bypasses Railway's memory limits and allows processing of large datasets.

Usage:
    python scripts/process_dataset_local.py <dataset_id>
    
Examples:
    python scripts/process_dataset_local.py ieee-cis-fraud
    python scripts/process_dataset_local.py givemesomecredit
    python scripts/process_dataset_local.py german-credit
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil
import argparse

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from app.datasets.registry import get_dataset_registry
from app.datasets.loaders import get_loader
from app.utils.kaggle_client import KaggleClient
from app.utils.r2_storage import r2_storage_client
from app.utils.supabase_client import supabase_db
import structlog

logger = structlog.get_logger()


def process_dataset_locally(dataset_id: str, use_full_dataset: bool = True):
    """
    Process a dataset locally and upload to cloud storage.
    
    Args:
        dataset_id: Dataset identifier (e.g., 'ieee-cis-fraud')
        use_full_dataset: If True, process full dataset. If False, use sampling.
    """
    print(f"\n{'='*60}")
    print(f"🚀 LOCAL DATASET PROCESSING")
    print(f"{'='*60}")
    print(f"Dataset: {dataset_id}")
    print(f"Mode: {'FULL DATASET' if use_full_dataset else 'SAMPLED'}")
    print(f"{'='*60}\n")
    
    # 1. Get dataset configuration
    print("📋 Step 1: Loading dataset configuration...")
    registry = get_dataset_registry()
    
    if dataset_id not in registry.datasets:
        print(f"❌ Error: Dataset '{dataset_id}' not found in registry")
        print(f"Available datasets: {list(registry.datasets.keys())}")
        return False
    
    config = registry.datasets[dataset_id]
    print(f"✅ Configuration loaded for: {config.get('display_name', dataset_id)}")
    
    # 2. Update status to processing
    print("\n📝 Step 2: Updating status to 'processing'...")
    try:
        if supabase_db.is_available():
            supabase_db.update_dataset(dataset_id, {'status': 'processing'})
            print("✅ Status updated in Supabase")
        else:
            print("⚠️  Supabase not available, skipping status update")
    except Exception as e:
        print(f"⚠️  Warning: Could not update status: {e}")
    
    # 3. Create temporary directory
    print("\n📁 Step 3: Creating temporary directory...")
    temp_dir = Path(tempfile.mkdtemp(prefix=f"{dataset_id}_"))
    print(f"✅ Temp directory: {temp_dir}")
    
    try:
        # 4. Download from Kaggle
        print("\n⬇️  Step 4: Downloading from Kaggle...")
        kaggle_client = KaggleClient()
        
        source = config.get('source', 'kaggle')
        if source != 'kaggle':
            print(f"❌ Error: Unsupported source: {source}")
            return False
        
        # Download based on type
        if 'kaggle_competition' in config:
            competition = config['kaggle_competition']
            print(f"   Competition: {competition}")
            result = kaggle_client.download_competition(
                competition_name=competition,
                output_dir=str(temp_dir)
            )
        elif 'kaggle_dataset' in config:
            dataset = config['kaggle_dataset']
            print(f"   Dataset: {dataset}")
            result = kaggle_client.download_dataset(
                dataset_name=dataset,
                output_dir=str(temp_dir)
            )
        else:
            print("❌ Error: No kaggle_competition or kaggle_dataset in config")
            return False
        
        if result['status'] != 'success':
            print(f"❌ Download failed: {result.get('error')}")
            return False
        
        print("✅ Download complete!")
        
        # 5. Load and preprocess
        print("\n🔄 Step 5: Loading and preprocessing data...")
        print("   This may take several minutes for large datasets...")
        
        # Create loader with temp directory
        loader = get_loader(dataset_id, config, data_dir=temp_dir)
        
        # If using full dataset, temporarily modify the loader
        if use_full_dataset and dataset_id == 'ieee-cis-fraud':
            print("   📊 Processing FULL dataset (no sampling)")
            # Override the load_raw_data method to not sample
            import pandas as pd
            
            transaction_file = temp_dir / 'train_transaction.csv'
            identity_file = temp_dir / 'train_identity.csv'
            
            print("   Loading transaction data...")
            transaction_df = pd.read_csv(transaction_file, low_memory=True)
            print(f"   ✅ Loaded {len(transaction_df):,} transaction rows")
            
            if identity_file.exists():
                print("   Loading identity data...")
                identity_df = pd.read_csv(identity_file, low_memory=True)
                print(f"   ✅ Loaded {len(identity_df):,} identity rows")
                
                print("   Merging datasets...")
                raw_df = transaction_df.merge(identity_df, on='TransactionID', how='left')
                del transaction_df, identity_df
            else:
                raw_df = transaction_df
            
            print(f"   ✅ Raw data loaded: {len(raw_df):,} rows, {len(raw_df.columns)} columns")
        else:
            raw_df = loader.load_raw_data()
        
        print("   Preprocessing...")
        processed_df = loader.preprocess(raw_df)
        print(f"   ✅ Preprocessing complete: {len(processed_df.columns)} features")
        
        del raw_df  # Free memory
        
        # 6. Split into train/val/test
        print("\n✂️  Step 6: Splitting into train/val/test...")
        train_df, val_df, test_df = loader.split(processed_df)
        print(f"   ✅ Train: {len(train_df):,} samples")
        print(f"   ✅ Val:   {len(val_df):,} samples")
        print(f"   ✅ Test:  {len(test_df):,} samples")
        
        del processed_df  # Free memory
        
        # 7. Save to parquet files
        print("\n💾 Step 7: Saving to parquet files...")
        train_path = temp_dir / "train.parquet"
        val_path = temp_dir / "val.parquet"
        test_path = temp_dir / "test.parquet"
        
        train_df.to_parquet(train_path, index=False)
        val_df.to_parquet(val_path, index=False)
        test_df.to_parquet(test_path, index=False)
        print("✅ Files saved locally")
        
        # 8. Upload to R2
        print("\n☁️  Step 8: Uploading to R2 storage...")
        r2_base_path = f"datasets/{dataset_id}/processed"
        
        print(f"   Uploading train.parquet...")
        r2_storage_client.upload_file(
            str(train_path),
            f"{r2_base_path}/train.parquet"
        )
        
        print(f"   Uploading val.parquet...")
        r2_storage_client.upload_file(
            str(val_path),
            f"{r2_base_path}/val.parquet"
        )
        
        print(f"   Uploading test.parquet...")
        r2_storage_client.upload_file(
            str(test_path),
            f"{r2_base_path}/test.parquet"
        )
        print("✅ All files uploaded to R2!")
        
        # 9. Calculate statistics
        print("\n📊 Step 9: Calculating statistics...")
        target_col = config.get('target_column', 'target')
        
        stats = {
            'total_samples': len(train_df) + len(val_df) + len(test_df),
            'num_features': len(train_df.columns) - 1,
            'train_samples': len(train_df),
            'val_samples': len(val_df),
            'test_samples': len(test_df),
        }
        
        # Class balance
        if target_col in train_df.columns:
            class_counts = train_df[target_col].value_counts().to_dict()
            stats['class_balance'] = {str(k): int(v) for k, v in class_counts.items()}
        
        print(f"   Total samples: {stats['total_samples']:,}")
        print(f"   Features: {stats['num_features']}")
        print(f"   Class balance: {stats.get('class_balance', 'N/A')}")
        
        # 10. Update Supabase
        print("\n💾 Step 10: Updating Supabase metadata...")
        try:
            if supabase_db.is_available():
                update_data = {
                    'status': 'completed',
                    'total_samples': stats['total_samples'],
                    'num_features': stats['num_features'],
                    'train_samples': stats['train_samples'],
                    'val_samples': stats['val_samples'],
                    'test_samples': stats['test_samples'],
                    'class_balance': stats.get('class_balance', {}),
                    'r2_path': r2_base_path,
                }
                
                supabase_db.update_dataset(dataset_id, update_data)
                print("✅ Supabase updated successfully!")
            else:
                print("⚠️  Supabase not available, skipping metadata update")
        except Exception as e:
            print(f"⚠️  Warning: Could not update Supabase: {e}")
        
        print(f"\n{'='*60}")
        print("🎉 SUCCESS! Dataset processing complete!")
        print(f"{'='*60}")
        print(f"\n✅ Dataset '{dataset_id}' is now ready for:")
        print("   - Model training")
        print("   - XAI analysis (SHAP, LIME)")
        print("   - Benchmarking")
        print(f"\nView it at: https://xai-working-project.netlify.app/datasets\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        
        # Update status to failed
        try:
            if supabase_db.is_available():
                supabase_db.update_dataset(dataset_id, {
                    'status': 'failed',
                    'error_message': str(e)
                })
        except:
            pass
        
        return False
        
    finally:
        # Cleanup
        print("\n🧹 Cleaning up temporary files...")
        try:
            shutil.rmtree(temp_dir)
            print("✅ Cleanup complete")
        except Exception as e:
            print(f"⚠️  Warning: Could not cleanup temp directory: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Process datasets locally and upload to cloud storage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/process_dataset_local.py ieee-cis-fraud
  python scripts/process_dataset_local.py givemesomecredit
  python scripts/process_dataset_local.py german-credit --sample
        """
    )
    
    parser.add_argument(
        'dataset_id',
        help='Dataset identifier (e.g., ieee-cis-fraud)'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Use sampling instead of full dataset (faster, less memory)'
    )
    
    args = parser.parse_args()
    
    # Check environment variables
    # Note: SUPABASE_SERVICE_KEY and SUPABASE_SERVICE_ROLE_KEY are the same
    if not os.getenv('SUPABASE_SERVICE_ROLE_KEY') and os.getenv('SUPABASE_SERVICE_KEY'):
        os.environ['SUPABASE_SERVICE_ROLE_KEY'] = os.getenv('SUPABASE_SERVICE_KEY')
    
    required_vars = [
        'KAGGLE_USERNAME',
        'KAGGLE_KEY',
        'R2_ACCOUNT_ID',
        'R2_ACCESS_KEY_ID',
        'R2_SECRET_ACCESS_KEY',
        'R2_BUCKET_NAME',
        'SUPABASE_URL',
        'SUPABASE_SERVICE_ROLE_KEY'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or export them.")
        sys.exit(1)
    
    # Process dataset
    success = process_dataset_locally(
        args.dataset_id,
        use_full_dataset=not args.sample
    )
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
