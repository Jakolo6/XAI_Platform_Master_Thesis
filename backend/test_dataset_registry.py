"""Test dataset registry."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.datasets.registry import get_dataset_registry

def test_registry():
    """Test dataset registry."""
    print("=" * 60)
    print("DATASET REGISTRY TEST")
    print("=" * 60)
    
    try:
        # Load registry
        print("\n1. Loading dataset registry...")
        registry = get_dataset_registry()
        print(f"   ✅ Registry loaded with {len(registry.datasets)} datasets")
        
        # List all datasets
        print("\n2. Available datasets:")
        datasets = registry.list_datasets()
        for dataset in datasets:
            print(f"   • {dataset['id']}: {dataset['display_name']}")
            print(f"     Source: {dataset['source']}")
            print(f"     Target: {dataset['target_column']}")
            print(f"     Tags: {', '.join(dataset.get('tags', []))}")
            print()
        
        # Get specific dataset
        print("3. Testing dataset retrieval...")
        ieee_config = registry.get_dataset_config('ieee-cis-fraud')
        if ieee_config:
            print(f"   ✅ Retrieved: {ieee_config['display_name']}")
            print(f"   Description: {ieee_config['description'][:80]}...")
            print(f"   Preprocessing: {', '.join(ieee_config['preprocessing_pipeline'])}")
        else:
            print("   ❌ Failed to retrieve dataset")
            return False
        
        # Test non-existent dataset
        print("\n4. Testing non-existent dataset...")
        fake_config = registry.get_dataset_config('non-existent')
        if fake_config is None:
            print("   ✅ Correctly returned None for non-existent dataset")
        else:
            print("   ❌ Should have returned None")
            return False
        
        print("\n" + "=" * 60)
        print("SUCCESS: Dataset registry is working!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_registry()
    sys.exit(0 if success else 1)
