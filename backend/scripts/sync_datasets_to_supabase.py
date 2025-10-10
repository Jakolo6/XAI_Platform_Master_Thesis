"""Sync dataset registry to Supabase."""

import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.registry import get_dataset_registry
from app.supabase.client import get_supabase_client
import structlog

logger = structlog.get_logger()


def sync_datasets():
    """Sync datasets from YAML registry to Supabase."""
    print("=" * 60)
    print("SYNC DATASETS TO SUPABASE")
    print("=" * 60)
    
    try:
        # Load registry
        print("\n1. Loading dataset registry...")
        registry = get_dataset_registry()
        datasets = registry.list_datasets(active_only=False)
        print(f"   ✅ Found {len(datasets)} datasets in registry")
        
        # Connect to Supabase
        print("\n2. Connecting to Supabase...")
        supabase = get_supabase_client()
        print("   ✅ Connected to Supabase")
        
        # Get existing datasets from Supabase
        print("\n3. Checking existing datasets in Supabase...")
        existing_datasets = supabase.get_datasets(is_active=False)
        existing_ids = {d['name'] for d in existing_datasets}
        print(f"   ℹ️  Found {len(existing_datasets)} existing datasets")
        
        # Sync each dataset
        print("\n4. Syncing datasets...")
        synced = 0
        skipped = 0
        errors = 0
        
        for dataset in datasets:
            dataset_id = dataset['id']
            
            try:
                # Check if already exists
                if dataset_id in existing_ids:
                    print(f"   ⏭️  Skipping {dataset_id} (already exists)")
                    skipped += 1
                    continue
                
                # Prepare data for Supabase
                supabase_data = {
                    'name': dataset['id'],
                    'display_name': dataset.get('display_name'),
                    'description': dataset.get('description'),
                    'source': dataset.get('source'),
                    'source_identifier': dataset.get('kaggle_dataset') or dataset.get('kaggle_competition'),
                    'kaggle_dataset': dataset.get('kaggle_dataset'),
                    'kaggle_competition': dataset.get('kaggle_competition'),
                    'target_column': dataset.get('target_column'),
                    'positive_class': str(dataset.get('positive_class')),
                    'split_ratios': dataset.get('split_ratios'),
                    'preprocessing_pipeline': dataset.get('preprocessing_pipeline'),
                    'feature_engineering': dataset.get('feature_engineering'),
                    'license': dataset.get('license'),
                    'citation': dataset.get('citation'),
                    'tags': dataset.get('tags'),
                    'is_active': dataset.get('is_active', True),
                    'status': 'pending'
                }
                
                # Insert into Supabase
                result = supabase.insert_dataset(supabase_data)
                print(f"   ✅ Synced {dataset_id}")
                synced += 1
                
            except Exception as e:
                print(f"   ❌ Error syncing {dataset_id}: {e}")
                errors += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("SYNC COMPLETE")
        print("=" * 60)
        print(f"✅ Synced: {synced}")
        print(f"⏭️  Skipped: {skipped}")
        print(f"❌ Errors: {errors}")
        print("=" * 60)
        
        return errors == 0
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = sync_datasets()
    sys.exit(0 if success else 1)
