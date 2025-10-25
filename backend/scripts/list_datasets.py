"""List all datasets in the database."""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.utils.supabase_client import supabase_db

if __name__ == '__main__':
    if not supabase_db.is_available():
        print("❌ Supabase not available")
        sys.exit(1)
    
    datasets = supabase_db.client.table('datasets').select('*').execute()
    
    if not datasets.data:
        print("No datasets found in database")
    else:
        print(f"\nFound {len(datasets.data)} datasets:\n")
        for ds in datasets.data:
            print(f"ID: {ds['id']}")
            print(f"Name: {ds.get('name', 'N/A')}")
            print(f"Display Name: {ds.get('display_name', 'N/A')}")
            print("-" * 60)
