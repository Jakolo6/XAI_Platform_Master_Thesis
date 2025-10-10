"""Process dataset: download, preprocess, split, and save."""

import sys
import asyncio
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.datasets.registry import get_dataset_registry
from app.datasets.loaders import get_loader
from app.supabase.client import get_supabase_client
import structlog

logger = structlog.get_logger()


async def process_dataset(dataset_id: str, force_download: bool = False):
    """Process a dataset end-to-end.
    
    Args:
        dataset_id: Dataset identifier
        force_download: If True, re-download even if data exists
    """
    print("=" * 60)
    print(f"PROCESSING DATASET: {dataset_id}")
    print("=" * 60)
    
    try:
        # Get dataset configuration
        print("\n1. Loading dataset configuration...")
        registry = get_dataset_registry()
        config = registry.get_dataset_config(dataset_id)
        
        if not config:
            print(f"   ❌ Dataset not found: {dataset_id}")
            return False
        
        print(f"   ✅ Config loaded: {config['display_name']}")
        
        # Get loader
        print("\n2. Initializing dataset loader...")
        loader = get_loader(dataset_id, config)
        print(f"   ✅ Loader initialized: {loader.__class__.__name__}")
        
        # Check if splits already exist
        if loader.splits_exist() and not force_download:
            print("\n   ℹ️  Dataset splits already exist. Use --force to re-process.")
            print(f"   📁 Data directory: {loader.data_dir}")
            
            # Load and show stats
            train_df, val_df, test_df = loader.load_splits()
            print(f"\n   📊 Dataset statistics:")
            print(f"      Train: {len(train_df)} samples")
            print(f"      Val:   {len(val_df)} samples")
            print(f"      Test:  {len(test_df)} samples")
            print(f"      Features: {len(loader.get_feature_columns(train_df))}")
            
            return True
        
        # Download dataset
        print("\n3. Downloading dataset...")
        print(f"   Source: {config['source']}")
        if config['source'] == 'kaggle':
            if config.get('kaggle_competition'):
                print(f"   Competition: {config['kaggle_competition']}")
            elif config.get('kaggle_dataset'):
                print(f"   Dataset: {config['kaggle_dataset']}")
        
        await loader.download()
        print("   ✅ Download complete")
        
        # Load raw data
        print("\n4. Loading raw data...")
        raw_df = loader.load_raw_data()
        print(f"   ✅ Loaded {len(raw_df)} rows, {len(raw_df.columns)} columns")
        
        # Preprocess
        print("\n5. Preprocessing data...")
        print(f"   Pipeline: {', '.join(config.get('preprocessing_pipeline', []))}")
        processed_df = loader.preprocess(raw_df)
        print(f"   ✅ Preprocessed to {len(processed_df)} rows, {len(processed_df.columns)} columns")
        
        # Split
        print("\n6. Splitting dataset...")
        ratios = config.get('split_ratios', {})
        print(f"   Ratios: train={ratios.get('train')}, val={ratios.get('val')}, test={ratios.get('test')}")
        train_df, val_df, test_df = loader.split(processed_df)
        print(f"   ✅ Split complete")
        print(f"      Train: {len(train_df)} samples")
        print(f"      Val:   {len(val_df)} samples")
        print(f"      Test:  {len(test_df)} samples")
        
        # Save splits
        print("\n7. Saving splits to disk...")
        loader.save_splits(train_df, val_df, test_df)
        print(f"   ✅ Saved to {loader.data_dir}")
        
        # Calculate statistics
        print("\n8. Calculating statistics...")
        stats = loader.get_statistics(processed_df)
        print(f"   ✅ Statistics calculated")
        print(f"      Total samples: {stats['total_samples']}")
        print(f"      Features: {stats['num_features']}")
        print(f"      Missing values: {stats['missing_values']}")
        print(f"      Class balance: {stats.get('class_balance', {})}")
        
        # Update Supabase
        print("\n9. Updating Supabase...")
        supabase = get_supabase_client()
        
        # Find dataset in Supabase by name
        datasets = supabase.get_datasets(is_active=False)
        supabase_dataset = next((d for d in datasets if d['name'] == dataset_id), None)
        
        if supabase_dataset:
            # Update with statistics
            updates = {
                'status': 'completed',
                'total_samples': stats['total_samples'],
                'num_features': stats['num_features'],
                'class_balance': stats.get('class_balance'),
                'completed_at': 'now()'
            }
            supabase.update_dataset(supabase_dataset['id'], updates)
            print("   ✅ Supabase updated")
        else:
            print("   ⚠️  Dataset not found in Supabase")
        
        print("\n" + "=" * 60)
        print("SUCCESS: Dataset processed successfully!")
        print("=" * 60)
        print(f"\n📁 Data location: {loader.data_dir}")
        print(f"📊 Ready for model training!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error processing dataset: {e}")
        import traceback
        traceback.print_exc()
        
        # Update Supabase with error
        try:
            supabase = get_supabase_client()
            datasets = supabase.get_datasets(is_active=False)
            supabase_dataset = next((d for d in datasets if d['name'] == dataset_id), None)
            if supabase_dataset:
                supabase.update_dataset(supabase_dataset['id'], {
                    'status': 'failed',
                    'error_message': str(e)
                })
        except:
            pass
        
        return False


async def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process a dataset')
    parser.add_argument('dataset_id', help='Dataset ID to process')
    parser.add_argument('--force', action='store_true', help='Force re-download and re-process')
    
    args = parser.parse_args()
    
    success = await process_dataset(args.dataset_id, force_download=args.force)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    asyncio.run(main())
